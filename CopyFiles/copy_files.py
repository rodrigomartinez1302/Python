# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 10:20:33 2023

"""
import threading
import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pyodbc
import json
import time

total_MB = 0
total_files = 0

def copy_file(src_path, dst_path):
    
    shutil.copy2(src_path, dst_path)
    
def get_last_file_name(file_pattern, src_path, dst_path):

    # Get a list of all files matching the pattern in source
    files_scr = glob.glob(os.path.join(src_path, file_pattern))
    
    # Get a list of all files matching the pattern in destination
    files_dst = glob.glob(os.path.join(dst_path, file_pattern))
    
    # If no files were found, exit the script
    if not files_scr:
        sys.exit()
        
    # Get the most recently modified file in source
    latest_file_scr = max(files_scr, key=os.path.getmtime, default=None)
    # Get the size of the file in source
    file_size_scr = os.path.getsize(latest_file_scr)
    
    
    # Get the most recently modified file in destination
    latest_file_dst = max(files_dst, key=os.path.getmtime, default=None)
    
    # Get the last modified date of the file in destination
    file_size_dst = 0
    if latest_file_dst:
        file_size_dst = os.path.getsize(latest_file_dst)
        
    # if files are different in last modify date or different size, new file to copy
    if file_size_scr != file_size_dst and latest_file_scr:
        
        global total_MB
        total_MB +=  int(file_size_scr/1000000)
        global total_files
        total_files +=  1 
        
        return latest_file_scr
    else:
        return None
    
def get_file(file_pattern, src_path, dst_path):
    
    start_time = datetime.now()
    latest_file_to_copy_path = get_last_file_name(file_pattern, src_path, dst_path)
    if latest_file_to_copy_path:
        copy_file(latest_file_to_copy_path, dst_path)
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds()/60)
        filename = os.path.basename(latest_file_to_copy_path)
        description = 'File copied: {}'\
            .format(filename) 
        update_db_log(end_time, description, duration, conn)
    else:
        description = 'No updates  in file: {}'\
            .format(file_pattern) 
        update_db_log(start_time, description, 0, conn)
    
def read_params(params_scr):
    
    # Read the Excel file into a pandas DataFrame
    df_params = pd.read_excel(params_scr)
    # Convert the DataFrame to a list of tuples
    params = [tuple(x) for x in df_params.values]
    return params

def start_threading_copy(params_list, conn):
    
    start_time = datetime.now()
    description = 'Checking for updates in files'
    print(description,'|',start_time)
    update_db_log(start_time, description, 0, conn)
  
    # Define a list to hold the threads
    threads = []
    for params in params_list:
        name_thread = params[0]
        thread = threading.Thread(target=get_file, args=params, name=name_thread)
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    
    end_time = datetime.now()
    duration = int((end_time - start_time).total_seconds()/60)
    description = 'Finished copy: {} files copied:, total MB: {}'\
        .format(total_files, total_MB) 
    update_db_log(end_time, description, duration, conn)
    
def create_SQL_connection(driver ,server, db, user, password):
    conn_string = 'DRIVER={};SERVER={};\
                          DATABASE={};UID={};PWD={}'.format(driver, 
                          server, db, user, password)
                          
    conn = pyodbc.connect(conn_string)
    return conn

def update_db_log(date, description, duration, db_connection):
    # Define the INSERT statement
    insert_query = "INSERT INTO t_copy_files_log (fecha, descripcion, \
        tiempo_transferencia_en_min) VALUES (?, ?, ?)"
    
    # Define the values to be inserted into the table
    values = (date, description, duration)
    
    cursor = db_connection.cursor()
    
     try:
        # Execute the INSERT statement
        cursor.execute(insert_query, values)
     except Exception as e:
        time.sleep(1)
        update_db_log(date, description, duration, db_connection)
        
    # Commit the transaction
    db_connection.commit()
    
    # close the cursor
    cursor.close()

def load_config():
    
    with open('config.json') as f:
        config = json.load(f)
    return config
    
if __name__ == '__main__':
    
    # Initialization
    params_list = read_params('file_params.xlsx')
    config_file = load_config()
    user = config_file['db_username']
    password = config_file['db_password']
    driver = config_file['db_driver']
    server = config_file['db_IP_log']
    db = config_file['db_log']
    
    # Create a scheduler object
    scheduler = BlockingScheduler()
    
    #Create db object
    conn = create_SQL_connection(driver, server, db, user, password)
    
    # Compute the starting date, now + 10 seconds por delay
    start_time = datetime.now() + timedelta(seconds=10)
    
    # Add the job to the scheduler
    scheduler.add_job(start_threading_copy, args= [params_list, conn], max_instances=1,
                      trigger=IntervalTrigger(hours=2
                                              ,start_date = start_time
                                              ,timezone='America/Montevideo')
                      , misfire_grace_time=30)
    
    # Start the scheduler
    scheduler.start()
    
    # close the database connection
    conn.close()
    
    '''
    create table t_copy_files_log(
    fecha datetime,
    descripcion varchar(1000),
    tiempo_transferencia_en_min int
    );
    '''
              
              
              
              
              
              
              
              
              
