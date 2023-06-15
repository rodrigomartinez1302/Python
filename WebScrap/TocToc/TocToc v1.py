# -*- coding: utf-8 -*-

# Python 3.x
# Selenium library (pip install selenium)
# Chrome driver executable (compatible with the installed Chrome browser version)
# JSON file with input parameters (named "toc_toc_params.json" and placed in the same directory as the script)
# Ensure that you have the necessary dependencies installed and the Chrome driver executable available in the specified path. 
# The JSON file should contain the following parameters: airport_origin, airport_destiny, depart_date, arrival_date, and budget_USD.

# Please note that the module relies on web scraping techniques to extract data from the Toc Toc Viajes website. 
# Ensure that you comply with the website's terms of service and any applicable legal regulations while using this module.


from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import json
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU usage

driver = webdriver.Chrome(executable_path='C:/Users/rmartinezg/Documents/chromedriver.exe'
                            ,options=chrome_options)

file_path = "toc_toc_params.json"

# Read the input user data
with open(file_path, "r") as file:
    data = json.load(file)

url = 'https://www.toctocviajes.com/flights/round-trip/' + data['airport_origin'] + '/' + data['airport_destiny']+'/' \
                        + data['depart_date']+ '/' + data['arrival_date'] + '/false/1/0/0/false/0/4/1///calendar'

driver.get(url)

time.sleep(20)

table = driver.find_element(By.CLASS_NAME, 'table-bordered').find_elements(By.TAG_NAME, 'th')
table_column_header = [element.text for element in table[0:8] if element.text]
table_row_header = [element.text for element in table[8:] if '/' in element.text]
table_content = [int(element.text[:element.text.index('x1')-1].replace('USD ', '')) for element in table[8:] if 'US' in element.text]
table_content_7_x_7 = np.reshape(table_content, [7, 7])

df = pd.DataFrame(table_content_7_x_7, columns = table_column_header, index = table_row_header)

lowest_value = df.min().min()  # Find the lowest value in the dataframe
column_name = df.columns[df.eq(lowest_value).any()]  # Find the column(s) containing the lowest value
index_name = df[df.eq(lowest_value)].stack().index.tolist()  # Find the index(es) containing the lowest value

# Print the results
print("From ", data['airport_origin'], "to ", data['airport_destiny'])
print("Budget USD", data['budget_USD'])
print("Lowest price U$S:", lowest_value)
print("Combination of departures & arrivels dates:", index_name)

if lowest_value < data['budget_USD']:
    print("send notification")

driver.close()
