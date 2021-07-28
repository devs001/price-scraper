import requests_html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import bs4
import requests
import unicodedata
import random
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class Scrape:
    def __init__(self, site: str, keyword: str, hits_per_page: int, get_page_numbers=True, render=False, driver=None):
        print('new object')
        self.site = site
        self.keyword = keyword
        self.render = render
        self.hits_per_page = hits_per_page
        self.get_page_numbers = get_page_numbers
        self.user_ag = UserAgent()
        if render:
            self.season = driver
            print('driver')
            print(driver)
        else:
            self.season = requests.Session()
        if get_page_numbers:
            self.number_of_pages = self.get_number_of_pages(hits_per_page=self.hits_per_page)
            print("total number of pages >> "+str(self.number_of_pages))
            time.sleep(1)
        else:
            self.number_of_pages = 1
        self.remained_pages = [x for x in range(1, self.number_of_pages+1)]
        print("total remained of pages >> " + str(len(self.remained_pages)))
        self.remained_pages_copy = self.remained_pages.copy()

    def url_generation(self, page_num: int):
        if self.site == 'amazon':
            key_field = (self.keyword.strip()).replace(' ', '+')
            if self.get_page_numbers:
               url = f'https://www.amazon.ae/s?k={key_field}&page={page_num}&ref=sr_pg_{page_num}'
            else:
                url = f'https://www.amazon.ae/s?k={key_field}'
        if self.site == 'noon':

            key_field = (self.keyword.strip()[:48]).replace(' ', '%20')
            if self.get_page_numbers:
                url = f'https://www.noon.com/uae-en/search?limit=150&page={page_num}&q={key_field}'
            else:
                url = f'https://www.noon.com/uae-en/search?limit=150&q={key_field}'
            print(url)
        if self.site == 'supplyvan':
            key_field = (self.keyword.strip()).replace(' ', '+')
            url = f'https://www.supplyvan.com/catalogsearch/result/index/?p={page_num}&q={key_field}'
            print(url)
        if self.site == 'aceuae':
            url = f'https://www.aceuae.com/en-ae/product-list/?p={page_num-1}&l=72&k={self.keyword}'
        return url

    def get_number_of_pages(self, hits_per_page: int, retry=4):
        site = self.site
        keyword = self.keyword
        if self.render:
            first_page = self.render_html(1)
        else:
            first_page = self.send_req(1).content
        str_for_number = '-1'
        suop_first = bs4.BeautifulSoup(first_page, 'html5lib')
        if site == 'amazon':
            number_string = suop_first.find(lambda tag: tag.name == 'span' and "results for" in tag.text,
                                            attrs={'dir': 'auto'})
            if not number_string and retry > 0:
                print('sleep..', end="")
                time.sleep(3)
                print("..")
                time.sleep(2)
                self.get_number_of_pages(hits_per_page, retry=retry - 1)
            if not str_for_number:
                return 1
            try:
                str_for_number = str(number_string.text)
            except Exception as e:
                print(e)
                return 1
            str_for_number = str_for_number.replace('1-48 of', '')
            str_for_number = str_for_number.replace('over', '')
            lower_index = str_for_number.find('results for')
            str_for_number = str_for_number[0:lower_index]
            str_for_number = str_for_number.replace(' ', '')
            str_for_number = str_for_number.replace(',', '')
            print(str_for_number)
        if site == 'supplyvan':
            number_string = suop_first.find('span', attrs={'class': 'toolbar-number'})
            if not number_string and retry > 0:
                print('sleep..', end="")
                time.sleep(3)
                print("..")
                time.sleep(2)
                self.get_number_of_pages(hits_per_page, retry=retry - 1)
            str_for_number = unicodedata.normalize("NFKD", number_string.text)
            str_for_number = str_for_number.replace(' ', '')
            str_for_number = str_for_number.replace(',', '')
            print(str_for_number)

        if site == 'noon':
            number_string = suop_first.find(lambda tag: tag.name == 'h2' and "Results for" in tag.text)
            if not number_string and retry > 0:
                print(suop_first.prettify())
                print('sleep..', end="")
                time.sleep(3)
                print("..")
                time.sleep(2)
                self.get_number_of_pages(hits_per_page, retry=retry - 1)
            str_for_number = str(number_string.text)
            str_for_number = str_for_number.replace('Results for', '')
            str_for_number = str_for_number.strip()
            str_for_number = str_for_number.replace(',', '')
            print(str_for_number)

        if site == 'aceuae':
            number_string = suop_first.find(lambda tag: tag.name == 'p' and "Products Found" in tag.text)
            if not number_string and retry > 0:
                print(suop_first.prettify())
                print('sleep..', end="")
                time.sleep(3)
                print("..")
                time.sleep(2)
                self.get_number_of_pages(hits_per_page, retry=(retry - 1))
            str_for_number = str(number_string.text)
            str_for_number = str_for_number.replace('Products Found', '')
            str_for_number = str_for_number.strip()
            str_for_number = str_for_number.replace(',', '')
        if not str_for_number:
            return 1
        try:
            str_for_number = int(str_for_number)
        except Exception as e:
            print(e)
            print(str_for_number)
            return 1
        pages = int(str_for_number) // hits_per_page
        if int(str_for_number) % hits_per_page > 0:
            pages += 1
        elif int(str_for_number) % hits_per_page < 0:
            pages += 1
        if pages <= 0:
            return 1
        if keyword == 'amazon':
            if pages > 7:
                return 7
        return pages

    def send_req(self, page: int, post=False):

        ussera = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67',
                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox',
                  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:70.0) Gecko/20100101 Firefox/70.0'
                  ]
        inx = random.randint(0, 2)
        user = self.user_ag.random
        if self.site == 'noon':
            user = ussera[inx]
        headers = {
            'user-agent': user}

        try:
            if post:
                req_obj = self.season.post(url=self.url_generation(page), headers=headers)
            else:
                print(headers)
                req_obj = self.season.get(url=self.url_generation(page), headers=headers)
            if req_obj.status_code == 200:
                return req_obj
            else:
                print("status code "+str(req_obj.status_code))
            return None
        except Exception as e:
            print("problem in sending req -->> "+str(e))
            return None

    def render_html(self, page_num: int, retry=3, timeout=5):
        driver = self.season
        try:
            driver.find_elements(By.CLASS_NAME, "form-control form-control").send_keys(self.keyword)
            driver.find_elements(By.CLASS_NAME, 'btn-search').click()
            time.sleep(timeout)
            soup = driver.page_source
        except Exception as e:
            print(e)
            if retry > 0:
                self.render_html(page_num, retry=retry-1, timeout=timeout+5)
        return soup

    # loop through given times
    def page_loop(self, retry_count=1):
        for page_num in self.remained_pages:
            if self.render:
                page_soup = self.render_html(page_num)
            else:
                page_soup = self.send_req(page=page_num)
                if not page_soup:
                    print('nothing found ')
                    continue
                page_soup = page_soup.content
            if not page_soup:
                print("page problem")
                continue

            yield [page_soup, page_num]
        # if retry_count > 0:
        #    self.page_loop(retry_count=retry_count-1)



