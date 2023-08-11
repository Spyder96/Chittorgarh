# %%
from  bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import json
import re
import datetime
import time

from tqdm import tqdm
import os
import logging
import unicodedata
from unidecode import unidecode

Headers=({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0' , 'Accept-language':'en-US , en;q=0.5'})
URL = "https://www.chittorgarh.com/report/mainboard-ipo-list-in-india-bse-nse/83/"
PRD_URL = "https://www.chittorgarh.com/ipo/netweb-technologies-india-ipo/1459/"

# %%
def get_webpage_soup(URL):
    try: 
        webpage=requests.get(URL,headers=Headers)
    except Exception as e:
        logging.error(f"-Page Unavailable : {e}") 
    #Creating initial soup file
    soup = BeautifulSoup(webpage.content,"html.parser")
    return soup
    #searching for product links available in the page

def soup_table_data(table):
    data = {}
    if table is None:
        data = {"No Data Available" : "No Data"}
    else:
        rows = table.find_all('tr')
        if rows:
            for row in rows:
                cells = row.find_all(['th', 'td'])
                for cell in cells:
                    try:
                        key = cells[0].text.strip()
                    except:
                        key = "NA"
                    try:
                        value = cell.text.strip()
                    except:
                        value = "NA"
                    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('utf-8')
                    value = re.sub(r'[^\x00-\x7F\u20b9]+', '', value) 
                    value = re.sub(r'[^\x00-\x7F]+', '', value)  # Remove non-ASCII characters
                    value = unidecode(value)
                    key = re.sub(' ', '_' , key)
                    data[key] = value
        else:
            data = {"No Data Available" : "No data"}
    return data


# %%

def extract_ipo_data(soup):
    company_name = soup.find('h2', itemprop='about', class_='border-bottom').text.replace(" Details",'')
    tables = soup.find_all("table", attrs={'class':"table table-bordered table-striped table-hover w-auto"})
    all_table_data = {}
    for table in tables:
        table_data = soup_table_data(table)
        #print(table_data)
        all_table_data.update(table_data)
    json_data = json.dumps(all_table_data,indent=4)
    with open(f'{company_name}.json', 'w',encoding='utf-8') as file:
        json.dump(all_table_data, file, indent=4, ensure_ascii= False)

# %%
soup = get_webpage_soup(URL)

# %%
table = soup.find("table", attrs={'class': 'table table-bordered table-striped table-hover w-auto'})
links = table.find_all('a')

href_list = []
for link in links:
    href = link.get('href')
    if href and href.startswith("https://www.chittorgarh.com/ipo/"):
        href_list.append(href)



# %% [markdown]
# 

# %%




# %%
for link in href_list:
    ipo_soup = get_webpage_soup(link)
    extract_ipo_data(ipo_soup)
    

# %%



