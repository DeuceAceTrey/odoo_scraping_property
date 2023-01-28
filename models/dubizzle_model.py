from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
import os
import json
import threading
from urllib.request import Request, urlopen
import requests
import asyncio
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from random import randint

def getSoup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Content-type': 'application/json', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br'}
    r = requests.get(url, headers=headers)
    html = r.text
    soup = BeautifulSoup(html, features="html.parser")

    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    return soup


def getCities():
    url = 'https://www.dubizzle.com/'
    soup = getSoup(url)
    site_blocks = soup.find('div', attrs={'class': 'site-blocks-wrapper'})
    sites = site_blocks.find_all('a')
    cities = []
    for site in sites:
        # cities.append({'city' : site.find('h1').get_text().replace('\n','').replace('dubizzle','').strip(),'link' : site['href']})
        cities.append(site['href'])
    return cities


def getSubLinks(city_link):
    soup = getSoup(city_link)
    # rent_a_tag = soup.find('a',attrs={'href' : '/property-for-rent/home/'})
    rent_panel = soup.find('div', attrs={'class': 'pfr'})
    rent_list = rent_panel.find('div', attrs={'class': 'popular_category_sub_section'}).find_all('a')
    rent_links = []
    for rent in rent_list:
        rent_links.append({'type': rent.get_text().strip().split(' ')[0], 'link': city_link + rent['href']})
    sale_panel = soup.find('div', attrs={'class': 'pfs'})
    sale_list = sale_panel.find('div', attrs={'class': 'popular_category_sub_section'}).find_all('a')
    sale_links = []
    for sale in sale_list:
        sale_links.append({'type': sale.get_text().strip().split(' ')[0], 'link': city_link + sale['href']})
    return rent_links, sale_links


def getResults(link, city_link, page , model):
    while (True):
        url = link['link'] + '?page' + str(page)
        soup = getSoup(url)
        try:
            listing_panel = soup.find('div', attrs={'class': 'list-listings'})
            lists = listing_panel.find_all('div', attrs={'class': 'ListItem__Root-sc-1i3osc0-1'})
        except:
            break
        results = []
        for item in lists:
            try:
                broker = item.find('img', attrs={'class': 'AgentLogo__Image-sc-1vhkgg0-1'})
                broker_co = broker['src']
                broker_name = broker['alt']
            except:
                broker_co = None
                broker_name = None
            signature_premium = None
            truecheck_verified = None
            image_div = item.find('div', attrs={'class': 'elements__ImageContainer-qyjwz8-0'})
            image = image_div.find('img')['src']
            title = image_div.find('img')['alt']
            details_link = city_link + item.find('a', attrs={'class': 'list-item-link'})['href']
            currency = item.find('span', attrs={'class': 'ListItem__PriceCurrency-sc-1i3osc0-10'}).get_text()
            amount = item.find('span', attrs={'class': 'ListItem__PriceValue-sc-1i3osc0-9'}).get_text()
            amount = amount.replace(',', '')
            amount = int(amount)
            frequency = ''
            location = item.find('span', attrs={'class': 'ListItem__Location-sc-1i3osc0-5'}).get_text().strip()
            type = link['type']
            exclusive = 'exclusive' in title.lower()
            status = None
            feature = title
            if ('furnished' in title.lower()):
                furnished = False if ('unfurnished' in title.lower()) else True
            else:
                furnished = None
            facts = item.find_all('span', attrs={'class': 'ListItem__Fact-sc-1i3osc0-12'})
            beds = facts[0].get_text().strip()
            baths = facts[1].get_text().strip()
            sqft = facts[2].get_text().strip()
            listing_date = item.find('span', attrs={'class': 'ListItem__Time-sc-1i3osc0-6'}).get_text()
            listing_date = listing_date.replace('about', '').strip()
            now = datetime.now()
            date_values = listing_date.split(' ')
            try:
                counts = int(date_values[0])
                if ('day' in date_values[1]):
                    listing_date = now - relativedelta(days=counts)
                elif ('month' in date_values[1]):
                    listing_date = now - relativedelta(months=counts)
                elif ('year' in date_values[1]):
                    listing_date = now - relativedelta(years=counts)
                else:
                    listing_date = now
            except:
                listing_date = now
            listing_date = listing_date.date()
            # check exists
            if (True):
                results.append({
                    'signature_premium': signature_premium,
                    'truecheck_verified': truecheck_verified,
                    'broker_co': broker_co,
                    'broker_name': broker_name,
                    'picture_link': image,
                    'listing_date': listing_date,
                    'type': type,
                    'currency': currency,
                    'price': amount,
                    'period': frequency,
                    'exclusive': exclusive,
                    'status': title,
                    'feature': title,
                    'furnished': furnished,
                    'address': location,
                    'bedrooms': beds,
                    'baths': baths,
                    'sqft': sqft,
                    'agents_name': '',
                    'details_link': details_link,
                    'create_date': now,
                    'write_date': now
                })
        # insert into model
        model.create(results)
        page += 2
        sleep(randint(3,5))

def getPropertyFromDubizzle(model):
    city_links = getCities()
    sub_rents = []
    sub_sales = []
    for city_link in city_links:
        rents, sales = getSubLinks(city_link)
        sub_rents += rents
        sub_sales += sales
        sub_links = sub_rents + sub_sales

        for link in sub_links:
            # handling pagination
            while (True):
                # add threading
                threads = []
                for i in range(0, 2):
                    # thread = threading.Thread(target=getResults,args=(self,link,city_link,i,))
                    thread = threading.Thread(target=getResults, args=(link, city_link, i,model,))
                    threads.append(thread)
                    # thread.start()
                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()

                # getResults(link , city_link , 0)

