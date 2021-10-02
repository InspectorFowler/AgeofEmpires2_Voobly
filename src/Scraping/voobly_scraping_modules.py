
# --------------------------------------------------------------------------------------------------------
# Age of Empires II Voobly community scraping modules
# --------------------------------------------------------------------------------------------------------

# Function definitions
# 1. Proxy - Setup proxy settings by randomly picking a proxy/port from online list
# 2. Database - Setup database connection strings and variables. Might have to change based on OS (Linux/Win)
# 3. Login - login to the main page using existing credentials
# 4. Pick lobbies & ladders to scrape - Focus would be on New player and RM/DM lobbies & RM and DM 1x1 ladders 
#    which are the most competitive ranked ladders
# 5. Fetch match details - Match details to include post match economy, military stats along with win/loss 
#    records and civilizations picked. 

# --------------------------------------------------------------------------------------------------------
# Libraries
# --------------------------------------------------------------------------------------------------------

# DB connectors
import pyodbc
from sqlalchemy import create_engine
import mysql.connector

# Data manupilation
import os
import pandas as pd
import numpy as np
import re
from functools import reduce

# Scraping and web
from bs4 import BeautifulSoup
import mechanize
import http.cookiejar
import requests

# Utility
from tqdm import tqdm
import random
import warnings
import datetime
from datetime import date, timedelta

# --------------------------------------------------------------------------------------------------------
# Proxy Setup
# --------------------------------------------------------------------------------------------------------

def fetch_proxies():   

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    URL = "https://free-proxy-list.net/"
    req = requests.get(URL, headers = headers) # .json()
    soup = BeautifulSoup(req.text, "lxml")

    for body in soup("tbody"):
        body.unwrap()

    df = pd.read_html(str(soup), flavor="bs4")
    df = pd.DataFrame(df[0])
    proxies = df[(df.Https == 'yes')] # (df.Https == 'yes') & (df.Country == 'United States')
    proxies['Port'] = proxies['Port'].astype(int)
    proxies = proxies[['IP Address','Port']][(proxies['Https']=='yes') & (proxies['Anonymity']=='elite proxy')]
    
    index = random.randint(0,proxies.shape[0])
    
    return(str(proxies.iloc[index,]['IP Address']),str(proxies.iloc[index,]['Port']))

# --------------------------------------------------------------------------------------------------------
# Database connection
# --------------------------------------------------------------------------------------------------------

# Set up ODBC connection and SQL engine for write back
def setup_sql_conn():
    
    server = 'localhost'
    database = 'AOE2_VOOBLY'
    user = 'admin'
    password = 'admin'

    db_conn = mysql.connector.connect(host = server,
                                      port = 3306,
                                      user = user,
                                      password = password)

    engine = create_engine("mysql+mysqlconnector://" + user + ":" + password + "@" + server + "/" + database)
    return(db_conn,engine)

# fetch max match ID in DB
def fetch_latest_match_id(db_conn):
    
    data = pd.DataFrame(pd.read_sql_query('''SELECT MAX(A.Match_ID) FROM AOE2_VOOBLY.RAW_MATCH_DATA A''', db_conn))
    data.columns = ['head']
    return(int(data['head'][0]))

# --------------------------------------------------------------------------------------------------------
# Voobly login
# --------------------------------------------------------------------------------------------------------

# Login into voobly
def voobly_login(username, password, proxy = None, port = None):
    # Browser
    br = mechanize.Browser()

    # Cookie Jar
    cj = http.cookiejar.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    if (not proxy) and (not port):
        br.set_proxies({"https":proxy+":"+port})
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

# --------------------------------------------------------------------------------------------------------
# Pick lobbies and ladders
# --------------------------------------------------------------------------------------------------------

# Find all lobbies and ladders
def fetch_lobby_ladders(instance):
    
    lobby_page = 'https://www.voobly.com/games/view/Age-of-Empires-II-The-Conquerors'
    soup = BeautifulSoup(instance.open(lobby_page).read())
    table = soup.find('table').find_all('td')

    # Create dataframe of links
    data = pd.DataFrame(columns=['Lobby', 'Lobby_link', 'Ladder', 'Ladder_link'])
    for i in table:
        lobby = i.find_all('a')
        if len(lobby) == 0:
            continue 
        for j in lobby:
            if 'games' in j['href']:
                lobby_text = j.text
                lobby_link = j['href']        
            if lobby_text == j.text:
                continue    
            ladder_text = j.text
            ladder_link = j['href']        

            # fill dataframe
            row = pd.DataFrame.from_dict({'Lobby':[lobby_text], 'Lobby_link':[lobby_link], 'Ladder':[ladder_text], 'Ladder_link':[ladder_link]})
            data = data.append(row)
    data = data.set_index([pd.Index(range(0,data.shape[0],1))])
    
    return(data)

# --------------------------------------------------------------------------------------------------------
# Fetch match details
# --------------------------------------------------------------------------------------------------------

# Fetch soup and tags:
def fetch_html(match_id,instance):
    
    match_page = 'https://www.voobly.com/match/view/'+str(match_id)+'/Match-Details'    
    
    try:
        obj = instance.open(match_page,timeout = 10)
        soup = BeautifulSoup(obj.read())
        table = soup.find_all('table')    
    
        all_tags = []
        if len(table)>0:

            for i in table:
                all_tags.append(i.text)
            all_tags = [re.sub('\n+', '||', sub) for sub in all_tags]
            all_tags = reduce(lambda l, x: l.append(x) or l if x not in l else l, all_tags, [])            
    
        return(soup,all_tags,1)
    
    except:
        return([],[],0)
    
# Fetch match ladder
def fetch_match_ladder(all_tags):   
    
    title_tags = all_tags[0].split(sep="||")
    title_tags = [x for x in title_tags if x]
    ladder = title_tags[1]
    
    return(ladder)

# Fetch match details
def fetch_match_details(all_tags):   
    
    detail_tags = all_tags[2].split(sep="||")
    detail_tags = pd.DataFrame([x for x in detail_tags if x])
    detail_tags.columns = ['head']

    match_id = int(re.sub('#','',detail_tags['head'][int(detail_tags[detail_tags['head']=='Match Details'].index[0])+1]))
    
    date_time = detail_tags['head'][int(detail_tags[detail_tags['head']=='Date Played:'].index[0])+1]
    if 'Yesterday' in  date_time:
        match_date = (date.today() - timedelta(days=1)).strftime('%m/%d/%Y')
        match_time = datetime.datetime.strptime(date_time.split(', ')[1],'%I:%M %p').strftime('%H:%M')
    elif 'Today' in  date_time:
        match_date = date.today().strftime('%m/%d/%Y')
        match_time = datetime.datetime.strptime(date_time.split(', ')[1],'%I:%M %p').strftime('%H:%M')
    else:
        match_date = datetime.datetime.strptime(date_time.split(' - ')[0],'%d %B %Y').strftime('%m/%d/%Y')
        match_time = datetime.datetime.strptime(date_time.split(' - ')[1],'%I:%M %p').strftime('%H:%M')
    
    match_rating = int(detail_tags['head'][int(detail_tags[detail_tags['head']=='Match Rating:'].index[0])+1])
    match_map = detail_tags['head'][int(detail_tags[detail_tags['head']=='Map:'].index[0])+1]
    match_length = detail_tags['head'][int(detail_tags[detail_tags['head']=='Duration:'].index[0])+1]
    match_player_no = int(detail_tags['head'][int(detail_tags[detail_tags['head']=='Players:'].index[0])+1])
    match_mod = detail_tags['head'][int(detail_tags[detail_tags['head']=='Game Mod:'].index[0])+1]

    match_details = {'Match_ID':[match_id],'Match_date':[match_date],'Match_time':[match_time],'Match_rating':[match_rating],
                     'Match_map':[match_map],'Match_length':[match_length],'Match_player_no':[match_player_no],'Match_mod':[match_mod]}

    match_details = pd.DataFrame.from_dict(match_details)
    return(match_details)

# Fetch player details
def fetch_player_details(soup,all_tags):    
    
    player_tags = all_tags[5].split(sep="||")
    player_tags = pd.DataFrame([x for x in player_tags if x and not str(x).isspace()])
    player_tags.columns = ['head']
    player_tags = pd.concat([pd.DataFrame(player_tags['head'][[num for num in range(player_tags.shape[0]) if num % 2 == 0]]).reset_index(),
                             pd.DataFrame(player_tags['head'][[num for num in range(player_tags.shape[0]) if num % 2 != 0]]).reset_index()],axis=1).drop(['index'],axis=1)
    player_tags.columns = ['Player','Details']

    player_c_tags = player_tags[player_tags.Player.str.contains('\(Computer\)$')]
    player_tags = player_tags[~player_tags.Player.str.contains('\(Computer\)$')]

    if player_c_tags.shape[0]>0:    
        player_c_tags['New Rating'] = ''
        player_c_tags['Points'] = ''
        player_c_tags['Team'] = player_c_tags.Details.apply(lambda x: int(x.split('Team: ')[1].split(' ')[0]))
        player_c_tags = player_c_tags.drop(['Details'],axis=1)

    player_tags['New Rating'] = player_tags.Details.apply(lambda x: int(x.split('New Rating: ')[1].split(' ')[0]))
    player_tags['Points'] = player_tags.Details.apply(lambda x: int(x.split('Points: ')[1].split(' ')[0]))
    player_tags['Team'] = player_tags.Details.apply(lambda x: int(x.split('Team: ')[1].split(' ')[0]))
    player_tags = player_tags.drop(['Details'],axis=1)
    
    if player_c_tags.shape[0]>0:
        player_tags = pd.concat([player_tags,player_c_tags],axis=0)

    civs = [re.search('(^\\|\\|[A-Z][A-Z][A-Z]\\|\\||)',x).group(1) for x in all_tags]
    civs = [x for x in civs if x]
    civs = pd.DataFrame([re.sub("\|\|","",x) for x in civs])
    player_tags['Civilization'] = civs
    player_no = player_tags.shape[0]
    
    images = soup.find_all('img')
    win_players = []
    for i in range(len(images)):
        if re.search('win.PNG', str(images[i])):
            string = str(images[i-1])
            start = [x.start() for x in re.finditer('\"', string)][0]+1
            end = [x.start() for x in re.finditer('\"', string)][1]        
            win_players.append(string[start:end])

    player_tags['Victory'] = player_tags.Player.apply(lambda x: sum([i in x for i in win_players]))    
    
    return(player_tags,player_no)    

# Create scores metadata table
def create_metadata_table():
    
    score_table = [0, 5, 5, 7, 6, 5]
    score_table = pd.DataFrame(score_table, columns = ['Columns']) 
    score_table = pd.concat([score_table,score_table.cumsum()],axis=1)
    score_table.columns = ['Columns','CumColumns']
    
    return(score_table)

# Fetch match scores for all players
def fetch_match_scores(soup,score_table,player_no):
    
    table = soup.find_all('center')

    score_tags = []
    for i in table:
        score_tags.append(i.text)
        
    start_index = [ i for i, word in enumerate(score_tags) if re.search('Military Score', word)]    
    del score_tags[0:int(start_index[0])]

    for k in range(score_table.shape[0]-1):

        score_tag_headers = score_tags[(player_no*score_table.CumColumns[k])+score_table.CumColumns[k]:(player_no*score_table.CumColumns[k])+score_table.CumColumns[k+1]]
        score_tag = pd.DataFrame(score_tags[(player_no*score_table.CumColumns[k])+score_table.CumColumns[k+1]:(player_no*score_table.CumColumns[k+1])+score_table.CumColumns[k+1]])
        score_tag.columns = ['head']

        indicies = [num for num in range(score_tag.shape[0]) if num % score_table.Columns[k+1] == 0]

        for i in range(score_table.Columns[k+1]):
            c_index = [x+i for x in indicies]
            col = pd.DataFrame(score_tag['head'][c_index]).reset_index().drop(['index'],axis=1)
            col.columns = [score_tag_headers[i]]
            if i==0:
                score = col
            else:
                score = pd.concat([score,col],axis = 1)

        if k == 0:
            match_score = score
        else:
            match_score = pd.concat([match_score,score],axis = 1)
            
    return(match_score)

def aggregate_details(ladder,match_details,player_details,match_scores,player_no):
    
    match_data = pd.DataFrame(pd.Series([ladder]).repeat(player_no))
    match_data.columns = ['ladder']
    match_data = pd.concat([match_data,pd.concat([match_details]*player_no)],axis=1)
    match_data = match_data.set_index([pd.Index(range(0,match_data.shape[0],1))])
    match_data = pd.concat([match_data,player_details,match_scores],axis = 1)
    
    return(match_data)

def fetch_all_match_details(match_id,instance):
    
    # Fetch html data
    soup,all_tags,status = fetch_html(match_id,instance)
    
    if status == 1:        
    
        if len(all_tags) !=0:
            
            try:
                # Match ladder
                ladder = fetch_match_ladder(all_tags)

                # Match details
                match_details = fetch_match_details(all_tags)

                # Player details
                player_details,player_no = fetch_player_details(soup,all_tags)

                # Match scores
                score_table = create_metadata_table()
                match_scores = fetch_match_scores(soup,score_table,player_no)

                match_data = aggregate_details(ladder,match_details,player_details,match_scores,player_no)

                for column in match_data:
                    match_data[column] = match_data[column].astype(str)
                match_data.columns = match_data.columns.str.replace(' ', '_')

                return(match_data)
            except:
                return([3]) # Not an AOE2 Match
        else:
            return([2]) # Match ID does not exist  
    else:
        return([1]) # Connection timed out  
    
# --------------------------------------------------------------------------------------------------------
# fetch all match details
# --------------------------------------------------------------------------------------------------------

# fetch match details and write to DB
def fetch_matches_write(match_id,instance,engine):    
    
    obj = pd.Series.to_frame(pd.Series([match_id], dtype='str'))
    obj.columns = ['Match_ID']   
        
    try:            
        data = fetch_all_match_details(match_id,instance)

        if len(data) == 1 and data == [2]:
            obj.to_sql('NONEXISTENT_FAILS',con=engine, if_exists="append",index=False)
            fails.append(match_id)

        elif len(data) == 1 and data == [1]:
            obj.to_sql('TIMEOUT_FAILS',con=engine, if_exists="append",index=False)
            timeout_fails.append(match_id)

        elif len(data) == 1 and data == [3]:
            obj.to_sql('NONAOE2MATCH_FAILS',con=engine, if_exists="append",index=False)
            fails.append(match_id)

        else:
            data.to_sql('RAW_MATCH_DATA',con=engine, if_exists="append",index=False)
    except:
        obj.to_sql('UNKNOWN_FAILS',con=engine, if_exists="append",index=False)      