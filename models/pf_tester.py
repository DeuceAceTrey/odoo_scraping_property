from bs4 import BeautifulSoup
import requests
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

r = requests.get('https://www.dubizzle.com/', headers=headers)
html = r.text
soup = BeautifulSoup(html, features="html.parser")
site_blocks = soup.find('div', attrs={'class': 'site-blocks-wrapper'})
print(r.status_code)
print(len(site_blocks))

# import subprocess
# CurlUrl = "curl 'https://www.propertyfinder.ae/en/search?c=1&ob=mr&page=" + str(2) +"' -H 'authority: www.propertyfinder.ae'  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'  -H 'accept-language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,ko;q=0.6'  -H 'cache-control: max-age=0'  -H 'sec-ch-ua: \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"' -H 'sec-ch-ua-mobile: ?0' -H 'sec-ch-ua-platform: \"Linux\"' -H 'sec-fetch-dest: document' -H 'sec-fetch-mode: navigate' -H 'sec-fetch-site: none'  -H 'sec-fetch-user: ?1' -H 'upgrade-insecure-requests: 1' -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36' --compressed"
# print(CurlUrl)
# status, output = subprocess.getstatusoutput(CurlUrl)
# soup = BeautifulSoup(output, features="html.parser")
# panels = soup.find_all('div',attrs={'class':'card-list__item'})
# print(len(panels))
# print(status)
#
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from xvfbwrapper import Xvfb
# vdisplay = Xvfb(width=800, height=1280)
# vdisplay.start()
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--disable-gpu')
# # chrome_options.add_argument('--headless')
# chrome_options.add_argument('--window-size=1920,1080')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--start-maximized')
# chrome_options.add_argument('--disable-setuid-sandbox')
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options = chrome_options)
# driver.delete_all_cookies()
# driver.get('https://www.dubizzle.com/')
# for request in driver.requests:
#     print(request.url)
#     print(request.headers)
#     break
# vdisplay.stop()
