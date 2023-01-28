from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
from dotenv import load_dotenv
import os
import json
import threading
from urllib.request import Request, urlopen
import requests
import asyncio
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


def getSoup(url): 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', 'Accept': '*/*', 'accept-language': 'en-US,en;q=0.9','upgrade-insecure-requests': '1'}
    r = requests.get(url,headers=headers)
    html = r.text
    soup = BeautifulSoup(html, features="html.parser")

    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    
    return soup

def update_propertyfinder(page = 1):
    for i in range(1,5):
        url = 'https://www.propertyfinder.ae/en/search?c=' + str(i) + '&ob=mr&page=' + str(page)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', 'Accept': '*/*', 'accept-language': 'en-US,en;q=0.9','upgrade-insecure-requests': '1'}
        r = requests.get(url,headers=headers)
        html = r.text
        soup = BeautifulSoup(html, features="html.parser")

        for script in soup(["script", "style"]):
            script.extract()    # rip it out
        
        panels = soup.find_all('div',attrs={'class' :'card-list__item'})
        results = []
        for panel in panels:
            type = panel.find('p',attrs={'class' :'card-intro__type'})
            type = type.get_text().strip()
            #try:
            if(panel.get_text() == ''):
                continue
            image_panel = panel.find('div' , attrs={'class' :'card__image-placeholder'})
            details_link = panel.find('a',attrs={'class' :'card__link'})['href']
            try:
                panel.find('p',attrs={'class' : 'card-intro__tag--property-premium'}).get_text()
                signature_premium = True
            except:
                signature_premium = False
            truecheck_verified = None
            image = image_panel.find('img')['src']
            
            price = panel.find('p',attrs={'class' : 'card-intro__price'})
            price = price.get_text().strip()
            listing_date = panel.find('p',attrs={'class' :'card-footer__publish-date'}).get_text()
            now = datetime.now()
            date_values = listing_date.split(' ')
            for date_text in date_values:
                try:
                    counts = int(date_text)
                    index = date_values.index(date_text)
                    break
                except:
                    continue
            if('day' in date_values[index + 1]):
                listing_date = now -relativedelta(days=counts)
            elif('month' in date_values[index + 1]):
                listing_date = now - relativedelta(months=counts)
            elif('year' in date_values[index + 1]):
                listing_date = now - relativedelta(years=counts)
            else:
                listing_date = now
            listing_date = listing_date.date()
            try:
                agents_name = panel.find('img',attrs={'class':'agent-avatar__image'})['alt']
            except:
                agents_name = None
            id_1 = price.index(' ')
            amount = price[0:id_1].replace(',','')
            amount = int(amount)
            id_2 = price.index('/',id_1)
            currency = price[(id_1 + 1):id_2]
            frequency = price[(id_2 + 1):]
            title = panel.find('h2',attrs={'class' : 'card-intro__title'})
            title = title.get_text().strip()
            location = panel.find('span',attrs={'class' : 'card-specifications__location-text'})
            location = location.get_text().strip()
            items = panel.find_all('p',attrs={'class':'card-specifications__item'})
            try:
                broker_co = panel.find('img',attrs={'class':'card-intro__broker-image'})['src']
            except:    
                broker_co = panel.find('img',attrs={'class':'card-intro__broker'})['src']
            beds = None
            baths = None
            sqft = None
            exclusive = 'exclusive' in title.lower()
            furnished = 'furnished' in title.lower()
            for item in items:
                v_text = item.get_text().strip().lower()
                if('studio' not in v_text):  
                    item_text = v_text[0:v_text.index(' ')]
                    if('bed' in v_text):
                        beds = item_text
                    elif('bath' in v_text):
                        baths = item_text
                    elif('sqft' in v_text):
                        sqft = item_text
            records = 0
            #records = model.search_count([('details_link','=',details_link),('type','=',type),('bedrooms','=',beds),('baths','=',baths),('sqft','=',sqft),('price','=',price)])
            address_info = location.split(',')
            if(len(address_info) == 2):
                area = address_info[1]
                project = address_info[0]
                master_project = ''
            elif(len(address_info) >= 3):
                area = address_info[2]
                project = address_info[1]
                master_project = address_info[0]
            else:
                area = location
                project = 'undefined'
                master_project = 'undefined'
            if(records == 0):  
                if (i == 1):
                    usage = 'Residential Rent'
                elif (i == 2):
                    usage = 'Residential Sale'
                elif (i == 3):
                    usage = 'Commercial Rent'
                else:
                    usage = 'Commercial Sale'
                address_info = location.split(',')
                length = len(address_info) - 1
                emirate = address_info[length]
                project = address_info[length - 1]
                results.append({
                    'isFreeHold' : 'Free Hold',
                    'usage' : usage,#residential or commercial
                    'emirate' : emirate,
                    'property_subtype' : type,
                    'transaction_size' : None,
                    'listing_size' : float(sqft.replace(' sqft','').replace(',','')),
                    'nearest_metro' : '',
                    'nearest_mall' : '',
                    'nearest_landmark' : '',
                    'master_project' : master_project,
                    'project' : project,
                    'transaction_price' : None,
                    'listing_price' : amount,
                    'transaction_date' : None,
                    'listing_date' : None,
                    'signature_premium' : signature_premium,
                    'truecheck_verified' : truecheck_verified,
                    'broker_co' : broker_co,
                    'broker_name' : '',
                    'picture_link' : image,
                    # currency : fields.Char()
                    # period : fields.Char()
                    'exclusive' : exclusive,
                    # status : fields.Char()
                    # feature : fields.Char()
                    'furnished' : furnished,
                    # address : fields.Char()
                    'bedrooms' : beds,
                    'baths' : baths,
                    #'sqft' : fields.Char()
                    'agents_name' : agents_name,
                    'details_link' : details_link,
                    'origin' : 'propertyfinder',
                    'create_date': now,
                    'write_date': now
                    })
                
        

update_propertyfinder()