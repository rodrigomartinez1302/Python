# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.common.by import By
import time
import re
import pandas as pd
from datetime import date
from bs4 import BeautifulSoup


pd.set_option('display.max_columns', None)
 
def spot_data(spot_id, spot_name, iteration=1):
    
    iteration+=1
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(service=Service('C:/Users/rmartinezg/Documents/chromedriver.exe')
                               , options=options)
    #browser.implicitly_wait(10)
    browser.get('https://www.windguru.cz/' + spot_id)
    
    time.sleep(20)
    #button = browser.find_element(By.ID, 'accept-choices')
    #button.click()
    
    block_length = 81
    
    data = []
    #Inizialize headers
    headers = ['spot_id']
    
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    
    try:
        headers.append('dates_hours')
        block = soup.find_all('tr', {'id': 'tabid_0_0_dates'})
        dates_hours= [i.text for i in block[0].find_all('td', re.compile('^tcell'))]
         
        headers.append('period')
        block = soup.find_all('tr', {'id': 'tabid_0_0_PERPW'})
        period = [float(i.text) for i in block[0].find_all('td', re.compile('^tcell'))]
        
        headers.append('wind_direction')
        block = soup.find_all('tr', {'id': 'tabid_0_0_SMER'})
        wind_direction = [i.span['title'] for i in block[0]]
        
        headers.append('wind_velocity')
        block = soup.find_all('tr', {'id': 'tabid_0_0_WINDSPD'})
        wind_velocity = [float(i.text) for i in block[0].find_all('td', re.compile('^tcell'))]
        
        headers.append('wave_direction')
        block = soup.find_all('tr', {'id': 'tabid_0_0_DIRPW'})
        wave_direction = [i.span['title'] for i in block[0]]
        
        headers.append('wave_size')
        block = soup.find_all('tr', {'id': 'tabid_0_0_HTSGW'})
        wind_size = [float(i.text) for i in block[0].find_all('td', re.compile('^tcell'))]
        
        data= []
        #first field is a the spot id, it is used to append many dataframes 
        #in one finall dataframe with all spots
        for i in range(block_length):
            data.append([spot_id, dates_hours[i], period[i] , wind_direction[i],
                         wind_velocity[i], wave_direction[i], wind_size[i]])
        
        
        browser.close()
    except Exception as excep:
        browser.close()
        print('Error spot load: {spotid} - {spotname} - retrying {iternumber},\
              error message: {expection}'.format(spotid=spot_id, 
              spotname=spot_name, iternumber=iteration, expection=excep))
      
        # try 2 times reloading, otherwise skip spot
        if iteration <3:
            
            spot_data(spot_id, spot_name, iteration)
        else:
            print('Spot load {spotid} - {spotname} - failed'.format(
                spotid= spot_id, spotname=spot_name))
            raise excep
    
    return pd.DataFrame(data, columns= headers)
        
    
def clean(df):
    
    df['date_stamp'] = date.today()
    df['day'] = df['dates_hours'].str.slice(0, 1)
    df['day_nr'] = df['dates_hours'].str.slice(1, 3)
    df['hour'] = df['dates_hours'].str.slice(4, 6)
    df['day'].replace('L', 'Lunes', inplace=True)
    df['day'].replace('M', 'Martes', inplace=True)
    df['day'].replace('X', 'Miércoles', inplace=True)
    df['day'].replace('J', 'Jueves', inplace=True)
    df['day'].replace('V', 'Viernes', inplace=True)
    df['day'].replace('S', 'Sabado', inplace=True)
    df['day'].replace('D', 'Domingo', inplace=True) 
    df.drop(['dates_hours'], inplace=True, axis=1)
    df['wind'] = df['wind_direction'].str.slice(0, 2)
    df.drop(['wind_direction'], inplace=True, axis=1)
    
    return df

spots = [{'spot_id':'116713', 'name': 'Punta Negra'},
         {'spot_id':'182618', 'name': 'La Aguada'},
         {'spot_id':'233002', 'name': 'José Ignacio'},
         {'spot_id':'405892', 'name': 'El Emir'},
         {'spot_id':'313168', 'name': 'Arroyo Pando'},
         {'spot_id':'212902', 'name': 'Arroyo Solis Chico'},
         {'spot_id':'405896', 'name': 'La Plage'},
         {'spot_id':'79550', 'name': 'Bikini'},
         {'spot_id':'119326', 'name': 'El Pepe'},
         {'spot_id':'37673', 'name': 'Los Botes'},
         {'spot_id':'333481', 'name': 'La Balconada'},
         {'spot_id':'333463', 'name': 'La Posta del Cangrejo'},
         {'spot_id':'405921', 'name': 'Playa del Barco'},
         {'spot_id':'93781', 'name': 'La Moza'},
         {'spot_id':'333460', 'name': 'La Boca de la Barra'},
         {'spot_id':'405894', 'name': 'La Olla'},
         {'spot_id':'34544', 'name': 'Santa Lucia del Este'},
         {'spot_id':'422330', 'name': 'Cuchilla Alta'}]


all_spots = pd.DataFrame()
      
for i in spots:
    try:
        spot = spot_data(i['spot_id'], i['name'])
        all_spots = pd.concat([all_spots, spot])
        print('Spot: {spot_name} loaded'.format(spot_name= i['name']))
        
    except:
        continue

all_spots = clean(all_spots)
spots = pd.DataFrame(spots)

#pd.merge(all_spots, spots,  how='inner').sort_values('wave_size', 
#                                                     ascending= False).head(10)
