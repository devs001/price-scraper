import bs4
from scrap_core import Scrape
import unicodedata
import numpy
import pandas
import time


def amazon_soup_extraction(soup: bs4.BeautifulSoup):
    name_list = list(soup.find_all('span', attrs={'class': 'a-size-base-plus a-color-base a-text-normal'}))
    price_list = list(soup.find_all('span', {'class': 'a-offscreen'}))
    product_lis = []
    for name_obj, price_obj in zip(name_list, price_list):
        print(name_obj.text)
        price = unicodedata.normalize("NFKD", price_obj.text)
        index = str(price.replace('AED', '')).strip()
        index = index.replace(',', '')
        print(float(index))
        product_lis.append([name_obj.text, float(index)])
    return product_lis


def noon_soup_extraction(soup: bs4.BeautifulSoup):
    print("its here im exraaction")

    product_obj_list = list(soup.find_all('div', attrs={'class': 'productContainer'}))
    print('products found',end='\t')
    print(len(product_obj_list))
    product_lis = []
    for product_obj in product_obj_list:
        name_obj = product_obj.find('div', attrs={'class': 'grid'})
        price_obj = product_obj.find('strong')
        try:
            name = name_obj['title']
            print(name)
        except Exception as e:
            print(e)
            continue
        price = unicodedata.normalize("NFKD", price_obj.text)
        index = str(price.strip())
        index = index.replace(',', '')
        print(float(index))
        product_lis.append([name, float(index)])
    return product_lis


def supplyvan_soup_extraction(soup: bs4.BeautifulSoup):
    print("its here im exraaction")
    name_list = list(soup.find_all('div', attrs={'class': 'product details product-item-details'}))
    price_list = list(soup.find_all('span', attrs={'class': 'price'}))
    print('list of product - ')
    print(len(name_list))
    product_lis = []
    for result_obj in name_list:
        name_obj = result_obj.find('a', attrs={'class': 'product-item-link'})
        price_obj = result_obj.find('span', attrs={'class': 'price'})
        name = str(name_obj.get_text()).strip()
        print(name)
        if price_obj:
            index = unicodedata.normalize("NFKD", price_obj.text)
            index = index.replace('AED', '')
            index = str(index.strip())
            index = index.replace(',', '')
            print(float(index))
            index = float(index)
        else:
            print('no price')
            index = 'null'
        product_lis.append([name, index])
    return product_lis


def aceuae_soup_extraction(soup: bs4.BeautifulSoup):
    print("its here im exraaction")
    name_list = list(soup.find_all('a', attrs={'class': 'product-title'}))
    price_list = list(soup.find_all('span', attrs={'class': 'price'}))
    print(len(name_list))
    print(len(price_list))
    for name_obj, price_obj in zip(name_list, price_list):
        print(name_obj.text)
        index = unicodedata.normalize("NFKD", price_obj.get_text())
        index = index.replace('AED', '')
        index = str(index.strip())
        index = index.replace(',', '')
        product_lis = []
        print(index)
        try:
            index = (float(index))
        except Exception as e:
            print(e)
            index = (int(index))
        product_lis.append([name_obj.text, float(index)])
    return product_lis


# amazon_scrape = Scrape('amazon', 'dewalt', 48)
# noon_scrape = Scrape('noon', 'dewalt', 150)
# supplyvan_scrape = Scrape('supplyvan', 'makita', 150)
# aceuae_scrape = Scrape('aceuae', 'makita', 72, render=True)


def get_data_soup(scrape_object: Scrape, retry=3):
    site_data = []
    for raw_soup_detail in scrape_object.page_loop(3):
        print("affter genrati")
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
            print("no suop ----------->>>>>>>>>   soup <<<---------------")
            time.sleep(4)
        if response:
            if len(response) > 0:
                site_data.extend(response)
                scrape_object.remained_pages_copy.remove(raw_soup_detail[1])
            else:
                print('_______---------->>> o  response <<<<---------____________')
        else:
            print(response)
            print('_______---------->>> no response <<<<---------____________')
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


def save_list(product_list: list):
    product_df = pandas.DataFrame(product_list)
    product_df.to_csv('xxx.csv')


def process_keyword_get_results(keyword: str, wanted_list: list, site:  str, get_page_numbers=True):
    keyword = keyword.strip()
    if keyword:
        if site == 'amazon':
            scrape = Scrape(site, keyword, 48, get_page_numbers)
        elif site == 'supplyvan':
            scrape = Scrape(site, keyword, 24, get_page_numbers)
        elif site == 'noon':
            scrape = Scrape(site, keyword, 150, get_page_numbers)
        elif site == 'aceuae':
            scrape = Scrape(site, keyword, 48, get_page_numbers)
        else:
            print('no site match')
            return None
        scraped_list = get_data_soup(scrape)
        final_list = compare_with_wanted(wanted_list, scraped_list)
        print('final list -')
        print(final_list)
        return final_list
    return None


def parse_for_site(keywords: str, wanted_list: list, site: str, retry=4):
    total_products_list = []
    if keywords:
        keywords_list = keywords.split(',')
        for keyword in keywords_list:
            final_list = process_keyword_get_results(keyword, wanted_list, site, get_page_numbers=False)
            total_products_list.extend(final_list)
        print(print(" total scraaped  ", end='\t'))
        print(len(total_products_list))
        remove_with_wanted(wanted_list, total_products_list)

    for keyword in wanted_list:
        final_list = process_keyword_get_results(keyword, wanted_list, site, get_page_numbers=False)
        total_products_list.extend(final_list)
    remove_with_wanted(wanted_list, total_products_list)
    if wanted_list and retry > 0:
        print("retry wanted left")
        final_list = parse_for_site("", wanted_list, site, retry=retry-1)
        total_products_list.extend(final_list)
    print('total in finals')

    print('wanted list left >> '+str(len(wanted_list))+" <<<")
    print("total product >> "+str(len(total_products_list)))
    return total_products_list


keywords = 'dewalt drill'
df_products = pandas.read_csv('price_scrap/noon-result22.csv')
wanted_list_amazon = [x for x in (df_products.to_dict()['name']).values()]
print(wanted_list_amazon)
print(df_products)
result = parse_for_site(keywords, wanted_list_amazon, 'noon')
df_results = pandas.DataFrame(result, columns=['name', 'price'])
print(" total get ", end='\t')
print(len(result))
print(print(" total wanted left ", end='\t'))
print(len(wanted_list_amazon))
df_results.to_csv('price_scrap/noon-resultxx.csv', index=False)
