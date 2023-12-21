import re
import time
import scroll
import config
import csv
import requests as r
import pandas as pd
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import date
from time import strftime

class AmazonScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        }
        self.count = 1
        self.all_data = []

    def amazon_scraping(self):
        print("Scrapping is started at daily " + config.schd_time)
        print("Programme Executed " + str(self.count) + " times")
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=chrome_options)
        print("----------- Scrapping Started -----------")
        driver.maximize_window()
        driver.get("https://www.amazon.sg/gp/bestsellers")
        categories = [li.get_attribute("href") for li in driver.find_elements(By.XPATH, ".//div[@class='_p13n-zg-nav-tree-all_style_zg-browse-group__88fbz']/div/a")]
        for link in categories:
            driver.get(link)
            driver.implicitly_wait(5)
            time.sleep(1)
            element = driver.find_element(By.XPATH, "//a[contains(text(),'Next page')]")
            scroll.scroll(driver, 2)
            pro_links1 = [pro.get_attribute("href") for pro in driver.find_elements(By.XPATH, ".//div[@class='zg-grid-General-faceout']/div/a[1]")]
            print(len(pro_links1))
            element.click()
            driver.implicitly_wait(5)
            scroll.scroll(driver, 2)
            pro_links = pro_links1 + [pro.get_attribute("href") for pro in driver.find_elements(By.XPATH, ".//div[@class='zg-grid-General-faceout']/div/a[1]")]
            pro_rank = 1
            print(len(pro_links))
            for url in pro_links:
                prop_data = {}
                retry = 0
                while True:
                    retry = retry + 1
                    if retry == 3:
                        break
                    try:
                        response = r.get(url, headers=self.headers)
                        if response.status_code != 200:
                            raise Exception
                        else:
                            break
                    except:
                        continue
                try:
                    data = html.fromstring(response.content)
                except:
                    pass
                prop_data['Date'] = str(date.today())
                try:
                    prop_data['Title'] =data.xpath("//span[@id='productTitle']")[0].text.strip()
                except:
                    prop_data['Title'] = ''
                try:
                    prop_data['Price'] = data.xpath("//div[@class='a-section a-spacing-none aok-align-center']/span/span")[0].text
                except:
                    prop_data['Price'] = ''
                try:
                    prop_data['No of Rating'] = data.xpath("//span[@id='acrCustomerReviewText']")[0].text.strip()
                except:
                    prop_data['No of Rating'] = ''
                try:
                    prop_data['Manufacturer'] = data.xpath("//th[contains(text(),'Manufacturer')]/following-sibling::td")[0].text.strip().replace('\u200e', '')
                except:
                    prop_data['Manufacturer'] = ''
                try:
                    asin = re.search(r'/[dg]p/([^/]+)', url, flags=re.IGNORECASE)
                    if asin:
                        prop_data['ASIN'] = asin.group(1)
                    else:
                        prop_data['ASIN'] = ''
                except:
                    prop_data['ASIN'] = ''
                try:
                    catg = re.search(r'/bestsellers/([^/]+)', link, flags=re.IGNORECASE)
                    if catg:
                        prop_data['Categories'] = catg.group(1)
                    else:
                        prop_data['ASIN'] = ''
                except:
                    prop_data['Categories'] = ''
                    prop_data['Rank'] = pro_rank
                try:
                    prop_data['Best_Seller_In'] = data.xpath("//span[@class='cat-link']")[0].text
                except:
                    prop_data['Best_Seller_In'] = ''
                try:
                    prop_data['Sold By'] = data.xpath("//div[@id='merchant-info']/a/span/text()")[0]
                except:
                    prop_data['Sold By'] = ''
                try:
                    prop_data['Rating'] = data.xpath("//i[@class='a-icon a-icon-star a-star-4-5']/span")[0].text
                except:
                    prop_data['Rating'] = ''
                try:
                    prop_data['International Ratings'] = data.xpath("//div[@class='a-box a-spacing-none a-color-alternate-background review']/div")[0].text.strip()
                except:
                    prop_data['International Ratings'] = ''
                try:
                    prop_data['Global Rating'] = data.xpath("//div[@data-hook='total-review-count']/span/text()")[0].strip()
                except:
                    prop_data['Global Rating'] = ''
                    prop_data['Url'] = url
                    pro_rank+=1
                    self.all_data.append(prop_data)
        driver.quit()
        df=pd.DataFrame(self.all_data)
        curr_time = strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        df.to_csv(f'{curr_time}-amazon_scraped.csv',index=False,quoting=csv.QUOTE_ALL, encoding='utf-8') 
        count+=1
