import bs4
from scrap_core import Scrape
import unicodedata
import numpy
import pandas
import time
from selenium import webdriver
from multiprocessing.pool import Pool
import traceback
import multiprocessing
from PyQt5 import QtCore


def amazon_soup_extraction(soup: bs4.BeautifulSoup):
    name_list = list(soup.find_all('span', attrs={'class': 'a-size-base-plus a-color-base a-text-normal'}))
    price_list = list(soup.find_all('span', {'class': 'a-offscreen'}))
    product_lis = []
    print('amzon product name and price', end='\t')
    print(len(name_list))
    print(len(price_list))
    for name_obj, price_obj in zip(name_list, price_list):
        price = unicodedata.normalize("NFKD", price_obj.text)
        index = str(price.replace('AED', '')).strip()
        index = index.replace(',', '')
        product_lis.append([name_obj.text, float(index)])
    return product_lis


def noon_soup_extraction(soup: bs4.BeautifulSoup):
    print("noon page")

    product_obj_list = list(soup.find_all('div', attrs={'class': 'productContainer'}))
    print(f'products found noon {len(product_obj_list)}')
    product_lis = []
    for product_obj in product_obj_list:
        name_obj = product_obj.find('div', attrs={'class': 'grid'})
        price_obj = product_obj.find('strong')
        try:
            name = name_obj['title']
            name = unicodedata.normalize("NFKD", name)
            name = name.strip()
            brand = name.split(' ')[0]
            name = name.replace(brand, '')
            print(brand)
            print(name)
            name = name.strip()
        except Exception as e:
            print(e)
            continue
        traceback.print_exc()
        price = unicodedata.normalize("NFKD", price_obj.text)
        index = str(price.strip())
        index = index.replace(',', '')
        product_lis.append([name, float(index)])
    print('noon list')
    print(product_lis)
    return product_lis


def supplyvan_soup_extraction(soup: bs4.BeautifulSoup):
    print("supplyy page")
    name_list = list(soup.find_all('div', attrs={'class': 'product details product-item-details'}))
    price_list = list(soup.find_all('span', attrs={'class': 'price'}))
    print('list of product spply - ')
    print(len(name_list))
    product_lis = []
    for result_obj in name_list:
        name_obj = result_obj.find('a', attrs={'class': 'product-item-link'})
        price_obj = result_obj.find('span', attrs={'class': 'price'})
        name = str(name_obj.get_text()).strip()
        if price_obj:
            index = unicodedata.normalize("NFKD", price_obj.text)
            index = index.replace('AED', '')
            index = str(index.strip())
            index = index.replace(',', '')
            index = float(index)
        else:
            print('no price')
            index = 'null'
        product_lis.append([name, index])
    return product_lis


def aceuae_soup_extraction(soup: bs4.BeautifulSoup):
    print("aceuae")
    name_list = list(soup.find_all(attrs={'class': 'product-title'}))
    price_list = list(soup.find_all('span', attrs={'class': 'price'}))
    print('aecuae name and price')
    print(len(name_list))
    print(len(price_list))
    for name_obj, price_obj in zip(name_list, price_list):
        print(name_obj.text)
        index = unicodedata.normalize("NFKD", price_obj.get_text())
        index = index.replace('AED', '')
        index = str(index.strip())
        index = index.replace(',', '')
        product_lis = []
        try:
            index = float(index)
        except Exception as e:
            print(e)
            try:
                index = (int(index))
            except Exception as e:
                print(e)
                print('index cant covert', end='\t')
                print(index)
                index = 'null'
            traceback.print_exc()

        product_lis.append([name_obj.text, index])
        return product_lis
    return None


# amazon_scrape = Scrape('amazon', 'dewalt', 48)
# noon_scrape = Scrape('noon', 'dewalt', 150)
# supplyvan_scrape = Scrape('supplyvan', 'makita', 150)
# aceuae_scrape = Scrape('aceuae', 'makita', 72, render=True)


def get_data_soup(scrape_object: Scrape, retry=1):
    site_data = []
    for raw_soup_detail in scrape_object.page_loop(3):
        page_number = raw_soup_detail[1]
        soup = bs4.BeautifulSoup(raw_soup_detail[0], 'html5lib')
        if soup:
            if scrape_object.site == 'aceuae':
                response = aceuae_soup_extraction(soup)
            elif scrape_object.site == 'noon':
                response = noon_soup_extraction(soup)
            elif scrape_object.site == 'amazon':
                if 'discuss automated access to Amazon data please contac' in soup.text:
                    print('captcha')
                else:
                    response = amazon_soup_extraction(soup)
            elif scrape_object.site == 'supplyvan':
                response = supplyvan_soup_extraction(soup)
            else:
                response = None
                print('no site found')
        else:
            print(f"{scrape_object.site}----------->>>>>>>>>   soup   <<<---------------")
            time.sleep(4)
        if response:
            if len(response) > 0:
                site_data.extend(response)
                scrape_object.remained_pages_copy.remove(raw_soup_detail[1])
            else:
                print(f'{scrape_object.site}_______---------->>> o  response <<<<---------____________')
        else:
            print(f'{scrape_object.site}_______---------->>> no response <<<<---------____________')
            print(len(scrape_object.remained_pages))
            time.sleep(5)

    scrape_object.remained_pages = scrape_object.remained_pages_copy
    if len(scrape_object.remained_pages) > 0 and retry > 0:
        print('retry')
        print(len(scrape_object.remained_pages))
        get_data_soup(scrape_object, retry=retry-1)
    if retry == 0:
        print('no retry left failed')
        print(len(scrape_object.remained_pages))
    return site_data


def compare_with_wanted(wanted_list: list, extrated_list: list):
    # this function compare with wanted list if get it then returns it
    # deletes it from wanted list
    lis = []

    print(wanted_list)
    for product in extrated_list:
        if product[0] in wanted_list:
            lis.append(product)
    return lis


def remove_with_wanted(wanted_list: list, product_list):
    # deletes it from wanted list
    blen = len(wanted_list)
    print('wanted list before ', end='\t')
    print(blen)
    for product in product_list:
        if product[0] in wanted_list:
            wanted_list.remove(product[0])
    print('total removed from wanted list ', end='\t')
    print(blen-len(wanted_list))


# num_site_array1 = get_data_soup(amazon_scrape)
#  print(('total -scraped '+str(len(num_site_array1))))
# num_site_array2 = get_data_soup(noon_scrape)
# print(len(num_site_array2))
# num_site_array3 = numpy.array(get_data_soup(supplyvan_scrape))
# num_site_array4 = numpy.array(get_data_soup(aceuae_scrape))


def match_prob(string1: str, string2: str):
    string1 = string1.replace(',', ' ')
    string2 = string2.replace(',', '')
    split_list1 = string1.split(" ")
    count = 0
    for word in split_list1:
        if word in string2:
            count += 1
    return count


def percentage_to_part(percent, whole):
    return float(whole) * float(percent)/100


def get_top_five_match(list_int: list):
    result_list = []
    for p in range(1, 5):
        max_num = max(list_int)
        list_int.index(max_num)
        index = list_int.index(max_num)
        result_list.append(list_int.index(max_num))
        list_int.pop(index)
    return result_list


def check_match_by_price(price, matched_product_price_disto):
    #  this  function check if price distortion in within allowed limit in matched product
    distortion = 10
    if price < 5:
        distortion = 25
    elif 5 <= price < 25:
        distortion = 20
    elif 25 <= price < 100:
        distortion = 18
    elif 100 <= price > 200:
        distortion = 16
    price_distorttion = percentage_to_part(distortion, price)
    if matched_product_price_disto <= price_distorttion:
        return True
    return False


def comparing_sites_products(list1: numpy.array, list2: numpy.array):
    matched_product = []
    # x is getting checked from y we are getting match for y or list1 from list2
    for x in list1:
        match_list = []
        for y in list2:
            match_number = match_prob(x[0], y[0])
            match_list.append(match_number)
        list_address = get_top_five_match(match_list)
        price = x[1]
        list_price = []
        for i in list_address:
            x = list2[i][1]
            list_price.append(abs(x - price))
        if check_match_by_price(price, min(list_price)):
            matched_product_address = list_address[list_price.index(min(list_price))]
        else:
            matched_product_address = -1
        matched_product.append(matched_product_address)
    return matched_product


count = 0
"""for i in comparing_sites_products(num_site_array2, num_site_array1):
    if i is -1:
        print(str(num_site_array2[count][0]) + "nothing matched")
        count += 1
        continue
    x = num_site_array1[i][0]
    y = num_site_array2[count][0]
    count += 1
    print(str(x)+" -> "+str(y))
"""


def start_driver(url=None):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=1200,1100')
    driver = webdriver.Chrome('chromedriver', options=options)
    if url:
        driver.get(url)
        return driver
    return driver


def save_list(product_list: list):
    product_df = pandas.DataFrame(product_list)
    product_df.to_csv('xxx.csv')


def process_keyword_get_results(keyword: str, wanted_list: list, site:  str, get_page_numbers=True, driver=None):
    keyword = keyword.strip()
    if keyword:
        if site == 'amazon':
            scrape = Scrape(site, keyword, 48, get_page_numbers)
        elif site == 'supplyvan':
            scrape = Scrape(site, keyword, 24, get_page_numbers)
        elif site == 'noon':
            scrape = Scrape(site, keyword, 150, get_page_numbers)
        elif site == 'aceuae':
            scrape = Scrape(site, keyword, 48, get_page_numbers, render=True, driver=driver)
        else:
            print('no site match')
            return None
        scraped_list = get_data_soup(scrape)
        final_list = compare_with_wanted(wanted_list, scraped_list)
        print(f'final list - {final_list}')
        return final_list
    return None

"""
def parse_for_site(keywords: str, wanted_list: list, site: str, progress_bar, retry=4):
    total_products_list = []
    if site == 'aceuae':
        driver = start_driver('https://www.aceuae.com/')
    else:
        driver = None
    if keywords:
        keywords_list = keywords.split(',')
        for keyword in keywords_list:
            final_list = process_keyword_get_results(keyword, wanted_list, site, get_page_numbers=True, driver=driver)
            total_products_list.extend(final_list)
            print(print(f" total scraaped  {site}"))
            print(len(total_products_list))
            print(print(f" total left {site} "))
            print(len(wanted_list))
            QtCore.QMetaObject.invokeMethod(progress_bar, "setValue",
                                            QtCore.Qt.QueuedConnection,
                                            QtCore.Q_ARG(int, len(total_products_list)))
        remove_with_wanted(wanted_list, total_products_list)

    for keyword in wanted_list:
        try:
            final_list = process_keyword_get_results(keyword, wanted_list, site, get_page_numbers=False, driver=driver)
            total_products_list.extend(final_list)
        except Exception as e:
            print(e)
        else:
            print(print(f" total scraaped {site} ", end='\t'))
            print(len(total_products_list))
            print(print(f" total left  {site}", end='\t'))
            print(len(wanted_list))
        traceback.print_exc()
    remove_with_wanted(wanted_list, total_products_list)
    if wanted_list and retry > 0:
        print("retry wanted left")
        final_list = parse_for_site("", wanted_list, site, retry=retry-1,)
        total_products_list.extend(final_list)
    print('total in finals')

    print(f'wanted list left >> {site}'+str(len(wanted_list))+" <<<")
    print(f"total product {site} >> "+str(len(total_products_list)))
    return total_products_list
"""


class ScrapeTheSite(QtCore.QRunnable):
    def __init__(self, keywords: str, wanted_list: list, site: str, progress_bar, retrys=2):
        QtCore.QRunnable.__init__(self)
        self.keywords = keywords
        self.wanted_list = wanted_list
        self.site = site
        self.progress_bar = progress_bar
        self.retrys = retrys
        self.total_products_list = []
        self.return_result()

    def return_result(self):
        return self.total_products_list

    def run(self):
        site = self.site
        progress_bar = self.progress_bar
        if site == 'aceuae':
            driver = start_driver('https://www.aceuae.com/')
        else:
            driver = None
        if keywords:
            keywords_list = keywords.split(',')
            for keyword in keywords_list:
                final_list = process_keyword_get_results(keyword, self.wanted_list, site, get_page_numbers=True,
                                                         driver=driver)
                self.total_products_list.extend(final_list)
                print(print(f" total scraped {site} > {len(self.total_products_list)}"))
                print(print(f" total left  {site}  > {len(self.wanted_list)}"))
                QtCore.QMetaObject.invokeMethod(progress_bar, "setValue",
                                                QtCore.Qt.QueuedConnection,
                                                QtCore.Q_ARG(int, len(self.total_products_list)))

            remove_with_wanted(self.wanted_list, self.total_products_list)

        for keyword in self.wanted_list:
            try:
                final_list = process_keyword_get_results(keyword, self.wanted_list, site, get_page_numbers=False,
                                                         driver=driver)
                self.total_products_list.extend(final_list)
            except Exception as e:
                print(e)
            else:
                print(print(f" total scraped {site} > {len(self.total_products_list)}"))
                print(print(f" total left  {site}  .> {len(self.wanted_list)}"))
                QtCore.QMetaObject.invokeMethod(progress_bar, "setValue",
                                                QtCore.Qt.QueuedConnection,
                                                QtCore.Q_ARG(int, len(self.total_products_list)))
        remove_with_wanted(self.wanted_list, self.total_products_list)
        if self.wanted_list and self.retrys > 0:
            print("retry wanted left")
            self.keywords = ''
            self.retrys = self.retrys - 1

        print('total in finals ------------- >')
        print(f'wanted list left >> {site}' + str(len(self.wanted_list)) + " <<<")
        print(f"total product {site} >> " + str(len(self.total_products_list)))





"""
keywords = 'dewalt,makita drill'
df_products = pandas.read_csv('ace.csv')
wanted_list_amazon = [x for x in (df_products.to_dict()['name']).values()]
print(wanted_list_amazon)
print(df_products)
result = parse_for_site(keywords, wanted_list_amazon, 'aceuae')
df_results = pandas.DataFrame(result, columns=['name', 'price'])
print(" total get ", end='\t')
print(len(result))
print(print(" total wanted left ", end='\t'))
print(len(wanted_list_amazon))
df_results.to_csv('ace-result.csv', index=False)
"""

keywords = ''


def match_sequence(master_list: list, fellow_list: list, site: str):
    mdf = pandas.DataFrame(master_list, columns=[site])
    fdf = pandas.DataFrame(fellow_list, columns=[site, f'{site}-price'])
    rdf = pandas.merge(mdf, fdf.drop_duplicates(), how='left', on=site)
    return rdf


def get_price_for_list(master_df: pandas.DataFrame, site: str, progressBar):
    wanted_list = [str(x) for x in (master_df.to_dict()[site]).values()]
    print(print(f" total wanted left {site} > {len(wanted_list)}"))
    print(type(wanted_list[0]))
    try:
        runnable = ScrapeTheSite(keywords, wanted_list, site, progress_bar=progressBar)
        QtCore.QThreadPool.globalInstance().start(runnable)
        print('here now')

        result_list = runnable.return_result()
        # result_list = parse_for_site(keywords, wanted_list, site, progress_bar=progressBar)
    except Exception as e:
        print(e)
        result_list = []
    traceback.print_exc()
    print(print(f" total wanted left mmmmmmmmmmmmmmmmmmm {site} ", end='\t'))
    print(len(wanted_list))
    wanted_list = [x for x in (master_df.to_dict()[site]).values()]
    structured_df = match_sequence(wanted_list, result_list, site)
    print(f" total get {site}", end='\t')
    print('here we are')
    print(structured_df.count())
    return structured_df


def get_product_count(df: pandas.DataFrame):
    lis = {}
    list_sites = ['amazon', 'aceuae', 'noon', 'supplyvan']
    for x in list_sites:
        try:
            lis[x] = df[x].count()
        except Exception as e:
            print('>> '+e)
            lis[x] = 0
    return lis


def wrapper_product(lists):
    return get_price_for_list(*lists)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    print('here')
    input_file = ''
    print('path > '+input_file)
    try:
        df_products = pandas.read_csv(input_file, encoding='unicode_escape')
        dic = get_product_count(df_products)
        print(dic)
    except Exception as e:
        print(e)
    print('here')
    pool = Pool(4)
    list_of_sites = [[df_products, 'amazon'], [df_products, 'aceuae'], [df_products, 'supplyvan'], [df_products, 'noon']]
    main_lis = pool.map(wrapper_product, list_of_sites)
    pool.close()
    pool.join()
    add_list = pandas.concat(main_lis, axis=1)
    add_list.to_csv('result3.csv')


