# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 12:36:44 2023

@author: rmartinezg
"""
import json
file_path = "toc_toc_params.json"

# read the last refresh_token to update it 
with open(file_path, "r") as file:
    data = json.load(file)

url = 'https://www.toctocviajes.com/flights/round-trip/' + data['airport_origin'] + '/' + data['airport_destiny']+'/' \
                        + data['depart_date']+ '/' + data['arrival_date'] + '/false/1/0/0/false/0/4/1///calendar'
                        
print(url)
print('https://www.toctocviajes.com/flights/round-trip/MVD/AKL/2023-11-01/2023-11-30/false/1/0/0/false/0/4/1///calendar')
