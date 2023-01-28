# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from dotenv import load_dotenv
import os
import threading
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

final_results = []

load_dotenv()
TIME_INTERVAL = os.getenv('TIME_INTERVAL')
ON_OFF = os.getenv('ON_OFF')

class Property(http.Controller):
    @http.route('/property/property', auth='public')
    def index(self, **kw):
        return "Hello, world"

    # @http.route('/property/property/objects', auth='public')
    # def list(self, **kw):
    #     return http.request.render('property.listing', {
    #         'root': '/property/property',
    #         'objects': http.request.env['property.property'].search([]),
    #     })

    @http.route('/property/property/objects/<model("property.property"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('property.object', {
            'object': obj
        })

    @http.route("/property/setInterval/<frequency>/<OnOff>", auth="public")
    def test_func(self, frequency,OnOff,**kwargs):
        with open('../server/odoo/addons/property/.env','w') as f:
            lines =  'TIME_INTERVAL=' + str(frequency) + '\n' +  'ON_OFF=' + str(OnOff)
            f.write(lines)
        f.close()
        
        return 'success'
        #except:
            #return 'fail'

    @http.route('/property/property/update', auth='public')
    def index(self, **kw):
        if(ON_OFF.lower() == 'on'):
        #self.search([]).unlink()
            while(True):
                threads = []
                model = http.request.env['property.property']
                for i in range(1,11):
                    thread = threading.Thread(target=search,args=(model,i,))
                    threads.append(thread)
                    #thread.join()
                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()
                for result in final_results:                
                    model.create(result)
                sleep(int(TIME_INTERVAL))
        return http.request.render('property.listing', {
            'root': '/property/property',
            'objects': http.request.env['property.property'].search([]),
        })
    

    
        

    # @api.depends('value')
    # def _value_pc(self):
    #     for record in self:
    #         record.value2 = float(record.value) / 100

def search(model,i):
    update_bayut(model,i)
    update_propretyfinder(model,i)


def update_bayut(model,page):
    found = False
    while(not found):
        
        url = 'https://www.bayut.com/to-rent/property/uae/' if(page == 0) else 'https://www.bayut.com/to-rent/property/uae/page-'+str(page) + '/'
        if(page >= 10):
            break
        page += 10
        results = []
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        soup = BeautifulSoup(html, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        panels = soup.find_all('li',attrs={"class":"ef447dde"})
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
            
            records = model.search_count([('details_link','=',details_link),('broker_co','=',broker_co),('type','=',type),('furnished','=',furnished),('bedrooms','=',beds),('baths','=',baths),('sqft','=',sqft),('price','=',amount)])
            
            if(records == 0):
                
                results.append({
                    'signature_premium' : signature_premium,
                    'truecheck_verified' : truecheck_verified,
                    'broker_co' : broker_co,
                    'broker_name' : broker_name,
                    'picture_link':image,
                    'listing_date' : '',
                    'type' : type,
                    'currency' : currency,
                    'price' : amount ,
                    'period' : frequency,
                    'exclusive' : exclusive,
                    'status' : status,
                    'feature' : feature,
                    'furnished' : furnished,
                    'address' : location,
                    'bedrooms' : beds,
                    'baths' : baths,
                    'sqft' : sqft,
                    'agents_name' : '',
                    'details_link' : details_link,
                    "create_date" : str(datetime.now()),
                    'write_date' : str(datetime.now()),
                    })
                
            else:
                found = True
                break
        
            
        for result in results:
            req = Request(result['details_link'], headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req).read()
            soup = BeautifulSoup(html, features="html.parser")

            for script in soup(["script", "style"]):
                script.extract()    
            try:
                agents_name = soup.find('a',attrs={'aria-label':'Agent name'}).get_text()
            except:
                agents_name = None
            listing_date = soup.find('span',attrs={'aria-label':'Reactivated date'}).get_text().strip()
            listing_date = parse(listing_date)
            result['agents_name'] = agents_name
            result['listing_date'] = str(listing_date.date())            
            # model.create({
            #             'signature_premium' : True,
            #             'truecheck_verified' : False,
            #             'broker_co' : 'property-finder',
            #             'picture_link':'image',
            #             'listing_date' : '2022-11-04',
            #             'type' : 'type',
            #             'currency' : 'currency',
            #             'price' : 3 ,
            #             'period' : 'frequency',
            #             'exclusive' : True,
            #             'status' : 'status',
            #             'feature' : 'feature',
            #             'furnished' : False,
            #             'address' : 'location',
            #             'bedrooms' : 'beds',
            #             'baths' : 'baths',
            #             'sqft' : '1222',
            #             'agents_name' : '',
            #             'details_link' : '',
            #             'create_date' : datetime.now(),
            #             'write_date' : datetime.now()
            # })
            sleep(1)
        model.create(results)
        

def update_propretyfinder(model,page):
    found = False
    while(not found):
        
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=options)
        url = 'https://www.propertyfinder.ae/en/search?c=2&fu=0&ob=mr&page=' + str(page) + '&rp=y'
        page += 10
        driver.get(url)

        panels = driver.find_elements('xpath',"//div[@class ='card-list__item']")
        results = []
        for panel in panels:
            type = panel.find_element('xpath',"//p[@class='card-intro__type']")
            type = type.text.strip()
            #try:
            if(panel.text == ''):
                continue
            image_panel = panel.find_element(By.CLASS_NAME , 'card__image-placeholder')
            details_link = panel.find_element(By.CLASS_NAME,'card__link').get_attribute('href')
            try:
                panel.find_element(By.CLASS_NAME,'card-intro__tag--property-premium').text
                signature_premium = True
            except:
                signature_premium = False
            truecheck_verified = None
            checked = False
            while(not checked):
                try:
                    image = image_panel.find_element(By.TAG_NAME,"img").get_attribute('src')
                    checked = True
                except Exception as e:
                    location = image_panel.location['y']
                    driver.execute_script("window.scrollTo(0,"+ str(location) + ")")
                    print(e)
                    sleep(2)
                    continue
            # except:
            #     continue
            
            price = panel.find_element('xpath',"//p[@class='card-intro__price']")
            price = price.text.strip()
            listing_date = panel.find_element(By.CLASS_NAME,'card-footer__publish-date').text
            now = datetime.now()
            date_values = listing_date.split(' ')
            counts = int(date_values[1])
            if('day' in date_values[2]):
                listing_date = now -relativedelta(days=counts)
            elif('month' in date_values[2]):
                listing_date = now - relativedelta(months=counts)
            elif('year' in date_values[2]):
                listing_date = now - relativedelta(years=counts)
            else:
                listing_date = now
            listing_date = listing_date.date()
            try:
                agents_name = panel.find_element('xpath',"//img[@class='agent-avatar__image']").get_attribute('alt')
            except:
                agents_name = None
            id_1 = price.index(' ')
            amount = price[0:id_1].replace(',','')
            amount = int(amount)
            id_2 = price.index('/',id_1)
            currency = price[(id_1 + 1):id_2]
            frequency = price[(id_2 + 1):]
            title = panel.find_element('xpath',"//h2[@class='card-intro__title']")
            title = title.text.strip()
            location = panel.find_element('xpath',"//span[@class='card-specifications__location-text']")
            location = location.text.strip()
            items = panel.find_elements(By.CLASS_NAME,'card-specifications__item')
            broker_co = panel.find_element(By.CLASS_NAME,'card-intro__broker').get_attribute('src')
            beds = None
            baths = None
            sqft = None
            exclusive = 'exclusive' in title.lower()
            furnished = 'furnished' in title.lower()
            for item in items:
                v_text = item.text.strip().lower()
                if('studio' not in v_text):  
                    item_text = v_text[0:v_text.index(' ')]
                    if('bed' in v_text):
                        beds = item_text
                    elif('bath' in v_text):
                        baths = item_text
                    elif('sqft' in v_text):
                        sqft = item_text
            records = model.search_count([('details_link','=',details_link),('type','=',type),('bedrooms','=',beds),('baths','=',baths),('sqft','=',sqft),('price','=',price)])
            if(records == 0):  
                results.append({
                        'signature_premium' : signature_premium,
                        'truecheck_verified' : truecheck_verified,
                        'broker_co' : broker_co,
                        'broker_name' : '',
                        'picture_link':image,
                        'listing_date' : listing_date,
                        'type' : type,
                        'currency' : currency,
                        'price' : amount,
                        'period' : frequency,
                        'exclusive' : exclusive,
                        'status' : title,
                        'feature' : title,
                        'furnished' : furnished,
                        'address' : location,
                        'bedrooms' : beds,
                        'baths' : baths,
                        'sqft' : sqft,
                        'agents_name' : agents_name,
                        'details_link' : details_link,
                        'create_date': now,
                        'write_date' : now
                        })
            else:
                found = True
        #for result in results:
            # driver.get(result['details_link'])
            # try:
            #     agents_name = driver.find_element(By.CLASS_NAME,'property-agent__name').text
            # except:
            #     agents_name = None
            # try:
            #     broker_co = driver.find_element(By.CLASS_NAME,'property-agent__position-broker-name').text
            # except:
            #     broker_co = None
            
            # feature = driver.find_element(By.CLASS_NAME,'property-amenities').text
            # exclusive = 'exclusive' in feature.lower()
            # furnished = 'furnished' in feature.lower()
            # result['agents_name'] = agents_name
            # result['broker_co'] = broker_co
            # result['exclusive'] = exclusive
            # result['furnished'] = furnished
            # result['feature'] = feature
            # sleep(1)
        model.create(results)
        #final_results += results