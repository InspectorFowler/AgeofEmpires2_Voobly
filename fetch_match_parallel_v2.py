import sys
import pandas as pd
from functools import partial

import tqdm
import time

import mechanize
import http.cookiejar
import requests

import multiprocessing as mp
from multiprocessing import Pool
from ipynb.fs.full.voobly_scraping_modules import fetch_all_match_details,setup_sql_conn,fetch_latest_match_id
from ipynb.fs.full.fetch_proxy_list import fetch_proxies
from ipynb.fs.full.credentials import credentials

collect = int(sys.argv[1])
procs = int(sys.argv[2])

def voobly_login(username, password):
    # Browser
    br = mechanize.Browser()

    # Cookie Jar
    cj = http.cookiejar.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    br.addheaders = [('User-agent', 'Chrome')]

    # The site we will navigate into, handling it's session
    br.open('https://voobly.com/login')

    # Select the second (index one) form (the first form is a search query box)
    br.select_form(nr=0)

    # User credentials
    br.form['username'] = username
    br.form['password'] = password

    # Login
    br.submit()
    
    return(br)

def fetch_matches(match,instance_var,engine_var):           
    
    obj = pd.Series.to_frame(pd.Series([match], dtype='str'))
    obj.columns = ['Match_ID']       

    try:            
        data = fetch_all_match_details(match,instance_var)

        if len(data) == 1 and data == [2]:
            obj.to_sql('NONEXISTENT_FAILS',con=engine_var, if_exists="append",index=False)

        elif len(data) == 1 and data == [1]:
            obj.to_sql('TIMEOUT_FAILS',con=engine_var, if_exists="append",index=False)

        elif len(data) == 1 and data == [3]:
            obj.to_sql('NONAOE2MATCH_FAILS',con=engine_var, if_exists="append",index=False)
            
        else:
            data.to_sql('RAW_MATCH_DATA',con=engine_var, if_exists="append",index=False)
    except:
        obj.to_sql('UNKNOWN_FAILS',con=engine_var, if_exists="append",index=False)    
        
if __name__ == '__main__':
    
    # Create connection instance
    username, password = credentials()
    instance = voobly_login(username,password)
    
    # Set up SQL connection
    db_conn,db_cursor,engine = setup_sql_conn()   
    
    # Fetch last match ID downloaded
    start_id = fetch_latest_match_id(db_conn)+1
    
    print('Starting download from match id: '+str(start_id)+'\n')
    iterations = list(range(start_id,start_id+collect))
    
    # Parallel processing
    p = mp.Pool(processes=procs)
    for _ in tqdm.tqdm(p.imap(partial(fetch_matches, instance_var = instance, engine_var = engine), iterations),bar_format='{desc:<5.5}{percentage:3.0f}%|{bar:70}{r_bar}', total = collect):
        pass
    