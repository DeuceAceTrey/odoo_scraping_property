# -*- coding: utf-8 -*-

from odoo import models, fields, api
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
#from dotenv import load_dotenv
import os
import threading
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from random import randint
import csv
import random
import logging
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import subprocess
#logging.basicConfig(filename='property.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)
#load_dotenv()
#load_dotenv()
#TIME_INTERVAL = os.getenv('TIME_INTERVAL')
#ON_OFF = os.getenv('ON_OFF')


class property(models.Model):
    _name = 'property.property'
    _description = 'property.property'

    isFreeHold = fields.Boolean()
    usage = fields.Char()
    emirate = fields.Char()
    project = fields.Char()
    master_project = fields.Char()
    property_subtype = fields.Char()
    transaction_size = fields.Float()
    listing_size = fields.Float()
    nearest_metro = fields.Char()
    nearest_mall = fields.Char()
    nearest_landmark = fields.Char()
    master_project = fields.Char()
    transaction_price = fields.Integer()
    listing_price = fields.Integer()
    transaction_date = fields.Date()
    listing_date = fields.Date()
    signature_premium = fields.Boolean()
    truecheck_verified = fields.Boolean()
    broker_co = fields.Char()
    broker_name = fields.Char()
    picture_link = fields.Char()
    exclusive = fields.Boolean()
    furnished = fields.Boolean()
    bedrooms = fields.Char()
    baths = fields.Char()
    agents_name = fields.Char()
    details_link = fields.Char()
    origin = fields.Char()
    # status = fields.Char()
    # currency = fields.Char()
    # period = fields.Char()
    # feature = fields.Char()
    # sqft = fields.Char()

    def getTop10Broker(self):
        sql = """SELECT broker_name , COUNT(*) count , SUM(listing_price) listing_price_total FROM property_property GROUP BY broker_name ORDER BY count DESC LIMIT 10"""
        self.env.cr.execute(sql)
        for rec in self.env.cr.fetchall():
            print("Name is", rec[0])
        return {
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": self._name,
        }

    def update_data(self):
        #self.search([]).unlink()
        update_bayut(self)
        #search_propertyfinder(self)
        update_propertyfinder(self)
        getPropertyFromDubizzle(self)
        getPropertyFromDubailand(self)
        # if(ON_OFF.lower() == 'on'):
        #     #self.search([]).unlink()
        #
        #     threads = []
        #     for i in range(1,11):
        #         thread = threading.Thread(target=search_data,args=(self,i,))
        #         threads.append(thread)
        #         #thread.start()
        #     for thread in threads:
        #         thread.start()
        #
        #     for thread in threads:
        #         thread.join()
        #     # for result in final_results:
        #     #     self.create(result)
        return  {
          "type": "ir.actions.act_window",
          "view_mode": "tree,form",
          "res_model": self._name,
        }





def update_bayut(model):
    found = False
    page = 10
    while(found == False):
        
        url = 'https://www.bayut.com/to-rent/property/uae/' if(page == 1) else 'https://www.bayut.com/to-rent/property/uae/page-'+str(page) + '/'
        # if(page >= 2):
        #     break
        page += 1
        results = []
        soup = getSoup(url)
        panels = soup.find_all('li',attrs={"class":"ef447dde"})
        if(len(panels) == 0):
            print(url)
            print('panel len == 0')
            break
        #found = True
        for panel in panels:
            signature_premium = None
            
            try:
                panel.find('div',attrs={'aria-label':'Property Verified Button'}).get_text()
                truecheck_verified = True
            except:
                truecheck_verified = False
            image = panel.find('img',attrs={'role':'presentation'})['src']
            
            try:
                broker_co = panel.find('img',attrs={'arai-label':'Agency photo'})['src']
                broker_name = panel.find('img',attrs={'arai-label':'Agency photo'})['alt']
            except:
                broker_co = None
                broker_name = None
            
            try:
                details_link = 'https://www.bayut.com' + panel.find('a',attrs={'aria-label':'Listing link'})['href']

                currency =panel.find('span',attrs={'aria-label':'Currency'})
                currency = currency.get_text().strip()
                amount =panel.find('span',attrs={'aria-label':'Price'}).get_text()
                amount = int(amount.strip().replace(',',''))

                frequency =panel.find('span',attrs={'aria-label':'Frequency'})
                frequency = frequency.get_text().strip()
                price = {'currency' : currency , 'price' : amount , 'frequency':frequency}
                location = panel.find('div',attrs={'aria-label':'Location'})
                location = location.get_text().strip()

                type = panel.find('div',attrs={'aria-label':'Type'})
                type = type.get_text().strip()
                title = panel.find('h2',attrs={'aria-label':'Title'})
                title = title.get_text().strip()
                exclusive = 'exclusive' in title.lower()
                status = title
                feature = title

                if('furnished' in title.lower()):
                    furnished = False if('unfurnished' in title.lower()) else True
                else:
                    furnished = None
                try:
                    beds = panel.find('span',attrs={'aria-label':'Beds'})
                    beds = beds.get_text().strip()
                except:
                    beds = 'Studio'
                try:
                    baths = panel.find('span',attrs={'aria-label':'Baths'})
                    baths = baths.get_text().strip()
                except:
                    baths = 'No Bathroom'
                try:
                    sqft = panel.find('span',attrs={'aria-label':'Area'})
                    sqft = sqft.get_text().strip()
                except:
                    sqft = None

                records = model.search_count([('details_link','=',details_link),('property_subtype','=',type),('listing_price','=',amount)])
                now = datetime.now()
                if(records == 0):
                    found = False
                    address_info = location.split(',')
                    length = len(address_info) -1
                    emirate = address_info[length]
                    project = address_info[length -1]
                    try:
                        master_project = address_info[length - 2]
                    except:
                        master_project = ''

                    try:
                        results.append(({
                        'isFreeHold' : 'Free Hold',
                        'usage' : '',#residential or commercial
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
                        'broker_name' : broker_name,
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
                        'agents_name' : '',
                        'details_link' : details_link,
                        'origin' : 'bayut',
                        'create_date': now,
                        'write_date': now
                    }))
                    except Exception as e:
                        print(e)
                        print(url)
                        continue
                    # results.append({
                    #     'signature_premium' : signature_premium,
                    #     'truecheck_verified' : truecheck_verified,
                    #     'broker_co' : broker_co,
                    #     'broker_name' : broker_name,
                    #     'picture_link':image,
                    #     'listing_date' : '',
                    #     'type' : type,
                    #     'currency' : currency,
                    #     'price' : amount ,
                    #     'period' : frequency,
                    #     'exclusive' : exclusive,
                    #     'status' : status,
                    #     'feature' : feature,
                    #     'furnished' : furnished,
                    #     'address' : location,
                    #     'bedrooms' : beds,
                    #     'baths' : baths,
                    #     'sqft' : sqft,
                    #     'agents_name' : '',
                    #     'details_link' : details_link,
                    #     "create_date" : str(datetime.now()),
                    #     'write_date' : str(datetime.now()),
                    #     })

                
            except:
                continue

        threads = []
        for i in range(1, 13):
            thread = threading.Thread(target=update_bayut_results,args=(results,i,))
            threads.append(thread)
            #thread.start()
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        if(len(results) > 0):
            model.create(results)
            model.env.cr.commit()


def update_bayut_results(results,index):
    while(index < len(results)):
        soup = getSoup((results[index]['details_link']))
        try:
            agents_name = soup.find('a',attrs={'aria-label':'Agent name'}).get_text()
        except:
            agents_name = None
        listing_date = soup.find('span',attrs={'aria-label':'Reactivated date'}).get_text().strip()
        listing_date = parse(listing_date)
        try:
            usage = soup.find('span',attrs={'aria-label':'Usage'}).get_text().strip()
        except:
            usage = 'residential'
        results[index]['agents_name'] = agents_name
        results[index]['listing_date'] = str(listing_date.date())
        results[index]['usage'] = usage
        index += 12
        sleep(randint(3,5))


def search_propertyfinder(model):
    threads = []
    for i in range(1, 3):
        thread = threading.Thread(target=update_propertyfinderBySelenium, args=(model, i,))
        threads.append(thread)
        # thread.start()
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

def update_propertyfinderBySelenium(model,page):
    proxies = [
        'mazenwb338:fJaemQW3FH@185.127.164.148:50100',
        'mazenwb338:fJaemQW3FH@5.133.163.99:50100',
        'mazenwb338:fJaemQW3FH@5.133.163.82:50100',
        'mazenwb338:fJaemQW3FH@5.133.163.98:50100',
        'mazenwb338:fJaemQW3FH@5.133.163.90:50100',
        'mazenwb338:fJaemQW3FH@217.21.58.116:50100',
        'mazenwb338:fJaemQW3FH@178.172.227.209:50100',
        'mazenwb338:fJaemQW3FH@31.130.201.162:50100',
        'mazenwb338:fJaemQW3FH@93.125.114.8:50100',
        'mazenwb338:fJaemQW3FH@91.149.167.17:50100',
        'mazenwb338:fJaemQW3FH@194.233.150.13:50100',
        'mazenwb338:fJaemQW3FH@50.114.105.226:50100',
        'mazenwb338:fJaemQW3FH@141.98.235.184:50100',
        'mazenwb338:fJaemQW3FH@216.162.201.15:50100',
        'mazenwb338:fJaemQW3FH@200.10.34.33:50100',
        'mazenwb338:fJaemQW3FH@94.124.160.157:50100',
        'mazenwb338:fJaemQW3FH@138.36.95.71:50100',
        'mazenwb338:fJaemQW3FH@185.212.205.151:50100',
        'mazenwb338:fJaemQW3FH@193.178.134.91:50100',
        'mazenwb338:fJaemQW3FH@193.43.119.104:50100',
        'mazenwb338:fJaemQW3FH@185.238.229.30:50100',
        'mazenwb338:fJaemQW3FH@185.206.248.90:50100',
    ]
    found = False
    options = webdriver.ChromeOptions()
    random_proxy = random.choice(proxies).strip()
    parts = random_proxy.split('@')
    options.add_argument('--proxy-server=http://%s@%s' % (parts[1], parts[0]))
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    while (not found):


        for i in range(1, 5):
            url = 'https://www.propertyfinder.ae/en/search?c=' + str(i) + '&ob=mr&page=' + str(page)
            # 1 : residential_rent 2: residential_sale 3: commercial_rent 4 : commercial_buy
            page += 10
            driver.get(url)

            panels = driver.find_elements('xpath', "//div[@class ='card-list__item']")
            results = []
            logging.info(url)
            logging.info(str(len(panels)))
            if (len(panels) == 0):
                break
            for panel in panels:
                type = panel.find_element('xpath', "//p[@class='card-intro__type']")
                type = type.text.strip()
                # try:
                if (panel.text == ''):
                    continue

                details_link = panel.find_element(By.CLASS_NAME, 'card__link').get_attribute('href')
                try:
                    panel.find_element(By.CLASS_NAME, 'card-intro__tag--property-premium').text
                    signature_premium = True
                except:
                    signature_premium = False
                truecheck_verified = None
                checked = False
                try:
                    image_panel = panel.find_element(By.CLASS_NAME, 'card__image-placeholder')
                except:
                    continue
                while (not checked):
                    try:

                        image = image_panel.find_element(By.TAG_NAME, "img").get_attribute('src')
                        checked = True
                    except Exception as e:
                        location = image_panel.location['y']
                        driver.execute_script("window.scrollTo(0," + str(location) + ")")
                        print(e)
                        sleep(2)
                        continue
                # except:
                #     continue

                price = panel.find_element('xpath', "//p[@class='card-intro__price']")
                price = price.text.strip()
                listing_date = panel.find_element(By.CLASS_NAME, 'card-footer__publish-date').text
                now = datetime.now()
                date_values = listing_date.split(' ')
                number_index = 0
                for date_value in date_values:
                    try:
                        counts = int(date_value)
                        number_index = date_values.index(date_value)
                        break
                    except:
                        continue
                counts = int(date_values[number_index])
                if ('day' in date_values[number_index + 1]):
                    listing_date = now - relativedelta(days=counts)
                elif ('month' in date_values[number_index + 1]):
                    listing_date = now - relativedelta(months=counts)
                elif ('year' in date_values[number_index + 1]):
                    listing_date = now - relativedelta(years=counts)
                else:
                    listing_date = now
                listing_date = listing_date.date()
                try:
                    agents_name = panel.find_element('xpath', "//img[@class='agent-avatar__image']").get_attribute(
                        'alt')
                except:
                    agents_name = None
                id_1 = price.index(' ')
                amount = price[0:id_1].replace(',', '')
                try:
                    amount = int(amount)
                except:
                    amount = None
                id_2 = price.index(' ', id_1)
                currency = price[(id_1 + 1):id_2]
                frequency = price[(id_2 + 1):]
                title = panel.find_element('xpath', "//h2[@class='card-intro__title']")
                title = title.text.strip()
                location = panel.find_element('xpath', "//span[@class='card-specifications__location-text']")
                location = location.text.strip()
                items = panel.find_elements(By.CLASS_NAME, 'card-specifications__item')
                try:
                    broker_co = panel.find_element(By.CLASS_NAME, 'card-intro__broker').get_attribute('src')
                except:
                    broker_co = None
                beds = None
                baths = None
                sqft = None
                exclusive = 'exclusive' in title.lower()
                furnished = 'furnished' in title.lower()
                for item in items:
                    v_text = item.text.strip().lower()
                    if ('studio' not in v_text):
                        item_text = v_text[0:v_text.index(' ')]
                        if ('bed' in v_text):
                            beds = item_text
                        elif ('bath' in v_text):
                            baths = item_text
                        elif ('sqft' in v_text):
                            sqft = item_text
                records = model.search_count([('details_link', '=', details_link), ('property_subtype', '=', type),
                                              ('listing_price', '=', amount)])
                if (records == 0):
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
                    try:
                        master_project = address_info[length - 2]
                    except:
                        master_project = ''
                    try:
                        results.append({
                            'isFreeHold': 'Free Hold',
                            'usage': usage,  # residential or commercial
                            'emirate': emirate,
                            'property_subtype': type,
                            'transaction_size': None,
                            'listing_size': float(sqft.replace(' sqft', '').replace(',', '')),
                            'nearest_metro': '',
                            'nearest_mall': '',
                            'nearest_landmark': '',
                            'master_project': master_project,
                            'project': project,
                            'transaction_price': None,
                            'listing_price': amount,
                            'transaction_date': None,
                            'listing_date': None,
                            'signature_premium': signature_premium,
                            'truecheck_verified': truecheck_verified,
                            'broker_co': broker_co,
                            'broker_name': '',
                            'picture_link': image,
                            # currency : fields.Char()
                            # period : fields.Char()
                            'exclusive': exclusive,
                            # status : fields.Char()
                            # feature : fields.Char()
                            'furnished': furnished,
                            # address : fields.Char()
                            'bedrooms': beds,
                            'baths': baths,
                            # 'sqft' : fields.Char()
                            'agents_name': '',
                            'details_link': details_link,
                            'origin': 'propertyfinder',
                            'create_date': now,
                            'write_date': now
                        })
                    except Exception as e:
                        print(e)
                        print(url)
                        continue
                else:
                    found = True
            # getting agent name
            for result in results:
                driver.get(result['details_link'])
                try:
                    agents_name = driver.find_element(By.CLASS_NAME, 'property-agent__name').text
                except:
                    agents_name = None
                try:
                    broker_name = driver.find_element(By.CLASS_NAME, 'property-agent__position-broker-name').text
                    broker_co = driver.find_element(By.CLASS_NAME, 'property-agent__broker-image').get_attribute('src')
                except:
                    broker_name = None
                    broker_co = None

                try:
                    feature = driver.find_element(By.CLASS_NAME, 'property-amenities').text
                    exclusive = 'exclusive' in feature.lower()
                    furnished = 'furnished' in feature.lower()
                except:
                    exclusive = None
                    furnished = None
                result['agents_name'] = agents_name
                result['broker_name'] = broker_name
                result['broker_co'] = broker_co
                result['exclusive'] = exclusive
                result['furnished'] = furnished
                # result['feature'] = feature
                sleep(1)
            model.create(results)
            model.env.cr.commit()


def update_propertyfinder(model):


    found = False
    page = 1
    while(not found):
        #found = True
        for i in range(1,5):
            CurlUrl = "curl 'https://www.propertyfinder.ae/en/search?c=" + str(i) +"&ob=mr&page=" + str(
                page) + "' -H 'authority: www.propertyfinder.ae'  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'  -H 'accept-language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,ko;q=0.6'  -H 'cache-control: max-age=0'  -H 'sec-ch-ua: \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"' -H 'sec-ch-ua-mobile: ?0' -H 'sec-ch-ua-platform: \"Linux\"' -H 'sec-fetch-dest: document' -H 'sec-fetch-mode: navigate' -H 'sec-fetch-site: none'  -H 'sec-fetch-user: ?1' -H 'upgrade-insecure-requests: 1' -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36' --compressed"

            page += 1

            status, output = subprocess.getstatusoutput(CurlUrl)
            soup = BeautifulSoup(output, features="html.parser")

            
            panels = soup.find_all('div',attrs={'class' :'card-list__item'})
            #logging.info(soup)
            logging.info('length of panels : ' + str(len(panels)))
            results = []
            if(len(panels) == 0):
                continue
            else:
                found = False
            for panel in panels:
                type = panel.find('p',attrs={'class' :'card-intro__type'})
                type = type.get_text().strip()
                #try:
                if(panel.get_text() == ''):
                    continue
                try:
                    image_panel = panel.find('div' , attrs={'class' :'card__image-placeholder'})
                    details_link = panel.find('a',attrs={'class' :'card__link'})['href']
                    details_link = 'https://www.propertyfinder.ae' + details_link
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
                    try:
                        amount = int(amount)
                    except:
                        amount = None
                    # try:
                    #     id_2 = price.index('/',id_1)
                    # except:
                    #     id_2 = price.index('\n', id_1)
                    # currency = price[(id_1 + 1):id_2]
                    #frequency = price[(id_2 + 1):]
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
                    
                    records = model.search_count([('details_link','=',details_link),('property_subtype','=',type),('listing_price','=',amount)])
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
                        found = False
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
                except Exception as e:
                    logging.info(e)
                    continue
            #getting agent name
            threads = []
            for j in range(len(results)):
                thread = threading.Thread(target=update_property_results,args=(results,j,))
                threads.append(thread)
                #thread.start()
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()
            if(len(results) > 0):
                logging.info('length of results : ' + str(len(results)))
                model.create(results)
                model.env.cr.commit()

def update_property_results(results,i):
    url = results[i]['details_link']
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', 'Accept': '*/*', 'accept-language': 'en-US,en;q=0.9','upgrade-insecure-requests': '1'}
    soup = getSoup(url,headers)
    try:
        agents_name = soup.find('a',attrs={'class':'property-agent__name'}).get_text()
    except:
        agents_name = None
    try:
        broker_name = soup.find('div',attrs={'class':'property-agent__position-broker-name'}).get_text()
        broker_co = soup.find('img',attrs={'class':'property-agent__broker-image'})['src']
    except:
        broker_name = None
        broker_co = None

    try:
        feature = soup.find_element(By.CLASS_NAME,'property-amenities').text
        exclusive = 'exclusive' in feature.lower()
        furnished = 'furnished' in feature.lower()
    except:
        exclusive = None
        furnished = None
    results[i]['agents_name'] = agents_name
    results[i]['broker_name'] = broker_name
    results[i]['broker_co'] = broker_co
    results[i]['exclusive'] = exclusive
    results[i]['furnished'] = furnished
        #result['feature'] = feature
        
            #final_results += results

def getSoup(url , headers=''):
    proxies = [
        'mazenwb338:fJaemQW3FH@185.127.164.148:50100',
        'mazenwb338:fJaemQW3FH@5.133.163.99:50100',
        'mazenwb338:fJaemQW3FH@5.133.163.82:50100',
        'mazenwb338:fJaemQW3FH@5.133.163.98:50100',
        'mazenwb338:fJaemQW3FH@5.133.163.90:50100',
        'mazenwb338:fJaemQW3FH@217.21.58.116:50100',
        'mazenwb338:fJaemQW3FH@178.172.227.209:50100',
        'mazenwb338:fJaemQW3FH@31.130.201.162:50100',
        'mazenwb338:fJaemQW3FH@93.125.114.8:50100',
        'mazenwb338:fJaemQW3FH@91.149.167.17:50100',
        'mazenwb338:fJaemQW3FH@194.233.150.13:50100',
        'mazenwb338:fJaemQW3FH@50.114.105.226:50100',
        'mazenwb338:fJaemQW3FH@141.98.235.184:50100',
        'mazenwb338:fJaemQW3FH@216.162.201.15:50100',
        'mazenwb338:fJaemQW3FH@200.10.34.33:50100',
        'mazenwb338:fJaemQW3FH@94.124.160.157:50100',
        'mazenwb338:fJaemQW3FH@138.36.95.71:50100',
        'mazenwb338:fJaemQW3FH@185.212.205.151:50100',
        'mazenwb338:fJaemQW3FH@193.178.134.91:50100',
        'mazenwb338:fJaemQW3FH@193.43.119.104:50100',
        'mazenwb338:fJaemQW3FH@185.238.229.30:50100',
        'mazenwb338:fJaemQW3FH@185.206.248.90:50100',
    ]
    if(headers == ''):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Content-type': 'application/json', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br'}
    random_proxy = random.choice(proxies).strip()
    proxy = {
        'http': 'http://' + random_proxy}
    r = requests.get(url, headers=headers, )
    #r = requests.get(url, headers=headers,)
    html = r.text
    soup = BeautifulSoup(html, features="html.parser")
    logging.info(soup)
    for script in soup(["script", "style"]):
        script.extract()  # rip it out
    sleep(randint(3,5))
    return soup


def getCities():
    url = 'https://www.dubizzle.com'
    headers = {
        'authority': 'www.dubizzle.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'de,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }
    soup = getSoup(url,headers=headers)
    site_blocks = soup.find('div', attrs={'class': 'site-blocks-wrapper'})
    logging.info(soup)
    logging.info('site_blocks' + str(len(site_blocks)))
    sites = site_blocks.find_all('a')
    cities = []
    for site in sites:
        # cities.append({'city' : site.find('h1').get_text().replace('\n','').replace('dubizzle','').strip(),'link' : site['href']})
        cities.append(site['href'])
    return cities


def getSubLinks(city_link):
    headers = {
        'authority': 'www.dubizzle.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'de,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }
    soup = getSoup(city_link , headers=headers)
    city_link = city_link[0:len(city_link) - 1] if(city_link[-1] == '/') else city_link
    # rent_a_tag = soup.find('a',attrs={'href' : '/property-for-rent/home/'})
    rent_panel = soup.find('div', attrs={'class': 'dubizzle_menu_dropdown_RP'})
    rent_list = rent_panel.find_all('li', attrs={'class': 'dubizzle_menu_dropdown_item'})
    rent_links = []
    for rent in rent_list:
        rent_link = city_link + rent.find('a')['href']
        type = rent.get_text().strip()

        rent_links.append({'type': type, 'link': rent_link})
    rent_panel = soup.find('div', attrs={'class': 'dubizzle_menu_dropdown_SP'})
    sale_list = rent_panel.find_all('li', attrs={'class': 'dubizzle_menu_dropdown_item '})
    sale_links = []
    for sale in sale_list:
        sale_link = city_link + sale.find('a')['href']
        type = sale.get_text().strip()

        sale_links.append({'type': type, 'link': sale_link})
    return rent_links, sale_links


def getResultsFromDubizlle(link, city_link, page , model):
    while (True):
        # if(page >= 1):
        #     break
        url = link['link'] + '?page' + '=' + str(page)
        headers = {
            'authority': 'www.dubizzle.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'de,en-US;q=0.9,en;q=0.8',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        }
        soup = getSoup(url, headers = headers)
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
            #try:
            try:
                image_div = item.find('div', attrs={'class': 'elements__ImageContainer-qyjwz8-0'})
                image = image_div.find('img')['src']
            except:
                image_div = item.find('div', attrs={'class': 'elements__ImageContainer-sc-qyjwz8-0'})
                image = image_div.find('img')['src']

            title = image_div.find('img')['alt']
            details_link = city_link + item.find('a', attrs={'class': 'list-item-link'})['href']
            currency = item.find('span', attrs={'class': 'ListItem__PriceCurrency-sc-1i3osc0-10'}).get_text()
            price = item.find('span', attrs={'class': 'ListItem__PriceValue-sc-1i3osc0-9'}).get_text()
            price = price.replace(',', '')
            price = int(price)
            frequency = ''
            location = item.find('span', attrs={'class': 'ListItem__Location-sc-1i3osc0-5'}).get_text().strip()
            type = link['type']
            if('commercial' in link['type'].lower()):
                usage = 'Commercial'
            else:
                usage = 'Residential'
            exclusive = 'exclusive' in title.lower()
            status = None
            feature = title
            if ('furnished' in title.lower()):
                furnished = False if ('unfurnished' in title.lower()) else True
            else:
                furnished = None
            facts = item.find_all('span', attrs={'class': 'ListItem__Fact-sc-1i3osc0-12'})
            beds = ''
            baths = ''
            sqft = ''
            for fact in facts:
                if('bed' in fact.get_text().lower()):
                    beds = fact.get_text().strip()
                if ('bath' in fact.get_text().lower()):
                    baths = fact.get_text().strip()
                if ('sqft' in fact.get_text().lower()):
                    sqft = fact.get_text().strip()
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
            records = model.search_count([('details_link', '=', details_link), ('property_subtype', '=', type),  ('listing_price', '=', price)])
            if (records == 0):
                emirate  = city_link.split('.')
                emirate = emirate[0].replace('https://','')
                address_info = location.split(',')
                master_project = address_info[0]
                try:
                    project = address_info[1]
                except:
                    project = ''
                try:
                    results.append({
                    'isFreeHold': 'Free Hold',
                    'usage': usage,  # residential or commercial
                    'emirate': emirate,
                    'property_subtype': type,
                    'transaction_size': None,
                    'listing_size': float(sqft.split(' ')[0].replace(',', '')) if(sqft == '') else 0,
                    'nearest_metro': '',
                    'nearest_mall': '',
                    'nearest_landmark': '',
                    'master_project': master_project,
                    'project': project,
                    'transaction_price': None,
                    'listing_price': price,
                    'transaction_date': None,
                    'listing_date': None,
                    'signature_premium': signature_premium,
                    'truecheck_verified': truecheck_verified,
                    'broker_co': broker_co,
                    'broker_name': '',
                    'picture_link': image,
                    # currency : fields.Char()
                    # period : fields.Char()
                    'exclusive': exclusive,
                    # status : fields.Char()
                    # feature : fields.Char()
                    'furnished': furnished,
                    # address : fields.Char()
                    'bedrooms': beds,
                    'baths': baths,
                    # 'sqft' : fields.Char()
                    'agents_name': '',
                    'details_link': details_link,
                    'origin': 'dubizzle',
                    'create_date': now,
                    'write_date': now
                })
                except Exception as e:
                    print(e)
                    print(url)
                    continue
            else:
                break
            #except:
                #continue
        # insert into model
        model.create(results)
        model.env.cr.commit()
        print(len(results))
        page += 1
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
            threads = []
            for i in range(0, 10):
                # thread = threading.Thread(target=getResults,args=(self,link,city_link,i,))
                thread = threading.Thread(target=getResultsFromDubizlle, args=(link, city_link, i,model,))
                threads.append(thread)
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

                # getResults(link , city_link , 0)

def getResultDubailLand(model,k):
    results = []
    length = len(rows) - 1
    while(True):
    #while (k < 1005):
        row = rows[length - k]
        row = row.replace('\"', '')
        row = row.split(',')
        if (k == length):
            break
        now = datetime.now()
        if(len(row) == 1):
            k += thread_cnt
            continue
        try:
            records = model.search_count(
                [('emirate', '=', 'dubai'), ('transaction_date', '=', parse(row[1])),('transaction_size','=',float(row[12])),('master_project','=',row[21]),('project','=',row[22])])
            if(records == 0):
                results.append({
                    'isFreeHold': True if('Free Hold' == row[6]) else False,
                    'usage': row[7],  # residential or commercial
                    'emirate': 'Dubai',
                    'property_subtype': row[10],
                    'transaction_size': float(row[12]),
                    'listing_size': None,
                    'nearest_metro': row[16],
                    'nearest_mall': row[17],
                    'nearest_landmark': row[18],
                    'master_project': row[21],
                    'project': row[22],
                    'transaction_price': int(float(row[11])),
                    'listing_price': None,
                    'transaction_date': parse(row[1]),
                    'listing_date': None,
                    'signature_premium': False,
                    'truecheck_verified': False,
                    'broker_co': None,
                    'broker_name': None,
                    'picture_link': None,
                    # currency : fields.Char()
                    # period : fields.Char()
                    'exclusive': None,
                    # status : fields.Char()
                    # feature : fields.Char()
                    'furnished': None,
                    # address : fields.Char()
                    'bedrooms': row[14],
                    'baths': None,
                    # 'sqft' : fields.Char()
                    'agents_name': None,
                    'details_link': '',
                    'origin': 'dubailand',
                    'create_date': now,
                    'write_date': now
                })

                #results.append(result)
            else:#met the last end
                break
            print(k)
        except Exception as e:
            print(e)
            print(row)
            k += thread_cnt
            continue


        k += thread_cnt
    model.create(results)
    model.env.cr.commit()


def getPropertyFromDubailand(model):
    url = 'https://gateway.dubailand.gov.ae/open-data/transactions/export/csv'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Content-type': 'application/json', 'Accept': '*/*'}
    now = datetime.now().date()
    date_from = now -relativedelta(days=30)

    date_from = str(date_from.month) + '/' + str(date_from.day) + '/' + str(date_from.year)
    date_to = str(now.month) + '/' + str(now.day) + '/' + str(now.year)
    body = {
        "parameters": {
            "P_FROM_DATE": date_from,
            "P_TO_DATE": date_to,
            "P_GROUP_ID": "",
            "P_IS_OFFPLAN": "",
            "P_IS_FREE_HOLD": "",
            "P_AREA_ID": "",
            "P_USAGE_ID": "",
            "P_PROP_TYPE_ID": "",
            "P_TAKE": "-1",
            "P_SKIP": "",
            "P_SORT": "TRANSACTION_NUMBER_ASC"
        },
        "command": "transactions",
        "labels": {
            "TRANSACTION_NUMBER": "Transaction Number",
            "INSTANCE_DATE": "Transaction Date",
            "PROPERTY_ID": "Property ID",
            "GROUP_EN": "Transaction Type",
            "PROCEDURE_EN": "Transaction sub type",
            "IS_OFFPLAN_EN": "Registration type",
            "IS_FREE_HOLD_EN": "Is Free Hold?",
            "USAGE_EN": "Usage",
            "AREA_EN": "Area",
            "PROP_TYPE_EN": "Property Type",
            "PROP_SB_TYPE_EN": "Property Sub Type",
            "TRANS_VALUE": "Amount",
            "PROCEDURE_AREA": "Transaction Size (sq.m)",
            "ACTUAL_AREA": "Property Size (sq.m)",
            "ROOMS_EN": "Room(s)",
            "PARKING": "Parking",
            "NEAREST_METRO_EN": "Nearest Metro",
            "NEAREST_MALL_EN": "Nearest Mall",
            "NEAREST_LANDMARK_EN": "Nearest Landmark",
            "TOTAL_BUYER": "No. of Buyer",
            "TOTAL_SELLER": "No. of Seller",
            "MASTER_PROJECT_EN": "Master Project",
            "PROJECT_EN": "Project"}
    }
    r = requests.post(url=url, headers=headers, json=body)
    result = r.text
    global rows
    rows = result.split('\n')
    threads = []
    global thread_cnt
    thread_cnt = 1
    for i in range(0, thread_cnt):
        # thread = threading.Thread(target=getResults,args=(self,link,city_link,i,))
        thread = threading.Thread(target=getResultDubailLand, args=(model,i,))
        threads.append(thread)
        # thread.start()
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    #getResultDubailLand(self,1)