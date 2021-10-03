
# --------------------------------------------------------------------------------------------------------
# Age of Empires II aoe2recs.com API modules
# --------------------------------------------------------------------------------------------------------

# Function definitions
# 1. Database - Setup database connection strings and variables. Might have to change based on OS (Linux/Win)
# 2. Database - Call API and fetch match details

# --------------------------------------------------------------------------------------------------------
# Libraries
# --------------------------------------------------------------------------------------------------------

# DB connectors
from pymongo import MongoClient

# Data manupilation
import pandas as pd, numpy as np
import os, math, random, time, warnings, json

# Scraping and web
from bs4 import BeautifulSoup
import requests, mechanize, http.cookiejar

# Utility
from tqdm import tqdm
from itertools import cycle

# Parallel processing
from joblib import Parallel, delayed

# --------------------------------------------------------------------------------------------------------
# Proxies and User agents
# --------------------------------------------------------------------------------------------------------

def fetch_proxies(top = 100, https = True):   

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}    
    URL = "https://free-proxy-list.net/"
    req = requests.get(URL, headers = headers)
    soup = BeautifulSoup(req.text, "lxml")

    for body in soup("tbody"):
        body.unwrap()

    df = pd.read_html(str(soup), flavor="bs4")
    df = pd.DataFrame(df[0])
    
    # Filter to HTTPS if necessary
    if https:
        proxies = df[(df.Https == 'yes')]
    else:
        proxies = df[(df.Https == 'no')]
        
    return(proxies[1:top])

def fetch_user_agents():

    # Set up user agent/header
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}    
    URL = "https://developers.whatismybrowser.com/useragents/explore/operating_system_name/windows/"
    
    # Fetch popular user agents
    req = requests.get(URL, headers = headers)
    soup = BeautifulSoup(req.text, "lxml")
    table = soup.find(lambda tag: tag.name=='table') 

    # Format
    uas = pd.DataFrame(pd.read_html(str(table), flavor="bs4")[0])
    
    # return
    return(uas)

# --------------------------------------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------------------------------------

def setup_mongo_conn():
    
    client = MongoClient(os.environ['mongopath'])    
    return(client)

# --------------------------------------------------------------------------------------------------------
# Read/delete/update matches
# --------------------------------------------------------------------------------------------------------

def insert_match_mongo(match_data, db_conn):
    
    db_conn.aoe2.matches.insert_one(match_data) 
    
def fetch_latest_match_id_aoe2recs(db_conn):
    
    match_id = db_conn.aoe2.matches.find_one(sort=[("id", -1)])['id']
    return(match_id)

def delete_invalid_match_mongo(db_conn):
    
    db_conn.aoe2.matches.delete_many({"id": -999})
    print('Invalid entries deleted !')
    
def insert_multiple_match_mongo(m_match_data, db_conn):
    
    for res in m_match_data:
        if res is None:
            db_conn.aoe2.matches.insert_one({'id': -999}) 
        else:
            db_conn.aoe2.matches.insert_one(res)                

def fetch_missing_match_ids(db_conn):
    
    # Fetch all match ids
    ids = []
    for i in db_conn.aoe2.matches.find({'id':{'$gt': 0}}).sort('id'):
        ids.append(int(i['id']))
        
    # All possible match ids
    all_ids = list(np.array(range(1,fetch_latest_match_id_aoe2recs(db_conn))))
    
    # missing matches
    miss_ids = set(all_ids).difference(ids)
    
    #return
    return(miss_ids)

# --------------------------------------------------------------------------------------------------------
# Fetch match details
# --------------------------------------------------------------------------------------------------------

def fetch_all_match_details_aoe2recs(match_id,query,proxy = None, ua = None):
    
    # Set session    
    s = requests.session()
    if ua != None:
        s.headers.update({'User-Agent': ua})                        
    if proxy != None:
        s.proxies.update(proxy)
    
    #Fetch from API
    res = s.post('https://aoe2recs.com/api', json={'query': query.replace('$$__$$',str(match_id))}).text
    res = json.loads(res)['data']['match']
    
    # Clear cookies
    s.cookies.clear()
    
    if res is None:
        res = {'id': -999}
        
    return(res)

def fetch_matches_iterate_aoe2recs(db_conn, collect = 1, type = 'new', clean_empty = True, cores = 4, proxy = None, ua = None, progress_bar = True):
    
    # CLean empty entries
    if clean_empty:
        delete_invalid_match_mongo(db_conn)
    
    # Function to fetch match details and insert to mongoDB
    def parallel_fetch(match_id,query,proxy,ua):   
        
        # Fetch match data
        match_data = fetch_all_match_details_aoe2recs(match_id,query,proxy,ua)
        
        # Setup Mongo connection
        db_conn = MongoClient(os.environ['mongopath'])          
        insert_match_mongo(match_data,db_conn)
    
    # Read query
    with open('/Projects/AgeofEmpires2_Voobly/Input/aoe2recs_match_data_query.txt', "r", encoding="utf-8") as text:
        query = text.read()
        
    if type == 'new':
         # Find last fetched match ID
        start = fetch_latest_match_id_aoe2recs(db_conn) + 1

        match_list = list(range(start,start+collect))
    elif type == 'missing':                
        match_list = fetch_missing_match_ids(db_conn)
        
    if progress_bar:    
        inputs = tqdm(match_list,miniters = 1,bar_format='{desc:<5.5}{percentage:3.0f}%|{bar:60}{r_bar}')
    else:
        inputs = match_list
    
    # Parallel fetch matches
    if __name__ == "__main__":
        processed_list = Parallel(n_jobs=cores)(delayed(parallel_fetch)(i,query,proxy,ua) for i in inputs)
    
    print('\nDONE !')
    print('\nAOE2 MATCHES DOWNLOADED : ' + str(collect))   
    
# --------------------------------------------------------------------------------------------------------
# Fetch multiple match details
# --------------------------------------------------------------------------------------------------------

def fetch_all_multiple_match_details_aoe2recs(matches,match_query,proxy = None, ua = None):
    
    # Create query
    query = ''
    for x in matches:
        query = query + '\n match' + str(x) + ' : ' + match_query.replace('$$__$$',str(x))
    query = 'query {' + query + '\n}'    
    
    # Set session    
    s = requests.session()
    if ua != None:
        s.headers.update({'User-Agent': ua})                        
    if proxy != None:
        s.proxies.update(proxy)
    
    # Fetch
    res = s.post('https://aoe2recs.com/api', json={'query': query}).text
    mres = []
    for x in matches : mres.append(json.loads(res)['data']['match'+str(x)])
    
    # Clear cookies
    s.cookies.clear()
            
    return(mres)

def fetch_multiple_matches_iterate_aoe2recs(db_conn, collect = 30, batch_size = 20):
        
    # CLean empty entries
    delete_invalid_match_mongo(db_conn)
        
    # Proxy iterator
    print('\nFetch proxy list')    
    proxies = []

    for index, row in fetch_proxies(https = False).iterrows():
        proxies.append({'http' : 'http://' + row['IP Address'] + ':' + str(row['Port'])})    
    proxy_cycle = cycle(proxies)        
    
    # User agent iterator
    print('\nFetch user agent list')
    uas_cycle = cycle(fetch_user_agents()['User agent'])    
        
    # Read query
    with open('/Projects/AgeofEmpires2_Voobly/Input/aoe2recs_multiple_match_data_query.txt', "r", encoding="utf-8") as text:
        query = text.read()    
    
    # Fetch latest match ID
    match_start_id = fetch_latest_match_id_aoe2recs(db_conn) + 1
    
    # Create match batches
    iters = np.array(range(0,math.floor(collect/batch_size)))*batch_size
    
    matches = []
    for i in iters : matches.append(np.array(range(i,batch_size+i))+match_start_id)

    last_match_complete = matches[len(iters)-1].max()
    last_match = match_start_id+collect

    if last_match != last_match_complete: matches.append(np.array(range(last_match_complete+1, last_match)))
     
    # Iterator
    total_batches = tqdm(np.array(range(0,len(matches))),miniters = 1,bar_format='{desc:<5.5}{percentage:3.0f}%|{bar:60}{r_bar}')
    
    for i in total_batches:
        
        fail_counter = 0
        fail_flag = True
        
        # Proxy
        proxy = next(proxy_cycle)

        # User agent
        ua = next(uas_cycle)
        
        while fail_flag: 
            
            try : 
                # Proxy
                proxy = next(proxy_cycle)

                # User agent
                ua = next(uas_cycle)

                # Fetch match data
                match_data = fetch_all_multiple_match_details_aoe2recs(matches[i],query,proxy,ua)
                
                # Insert to DB
                insert_multiple_match_mongo(match_data,db_conn)
                
                fail_flag = False
                
            except:
                
                if(fail_counter > 10):
                    
                    # If more than 10 retires then sleep for a while
                    time.sleep(75)
                elif(fail_counter > 15):
                    
                    # If more than 15 Retires then stop 
                    raise Exception('Stopping process, too many retires !')
                else:
                    
                    # else retry
                    fail_counter+=1                      
    
    print('\nDONE !')
    print('\nAOE2 MATCHES DOWNLOADED : ' + str(collect))   