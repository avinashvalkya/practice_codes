#!/usr/bin/python
import pickle
from api_helper import ShoonyaApiPy
import logging
from datetime import datetime, timedelta, date
from pytz import timezone, utc
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from pytz import timezone, utc
from time import sleep
import os
import subprocess
import json
from dateutil.relativedelta import relativedelta, TH
# from login_broker import shoonya
import requests
import logging
# logging.basicConfig(filename="/home/trading042023/trading_image_master/momentum/finvasia_data_logs.log",
#                     format='%(asctime)s %(message)s',
#                     filemode='a',level=logging.DEBUG)
def finvasia_session_token():

    # filepath = pathlib.Path(os.getcwd()).resolve().parent
    configFile= '/home/trading042023/trading_image_master/momentum/config.pkl'
    print(configFile)
    
    with open(configFile, 'rb') as input:
            config = pickle.load(input)
    
    return config
 

    
def get_login():
    
    try:
        session = finvasia_session_token()
        usersession = session['susertoken']
        print(usersession)
        user = json.loads(open('/home/trading042023/trading_image_master/momentum/creds.json', 'r').read().rstrip())
        uid    = user['uid']
        pwd     = user['pwd']
        api = ShoonyaApiPy()
        print(api)
        api.set_session(userid= uid, password = pwd, usertoken= usersession)
        return api
    except:
        
        code ="error while logging in bn auth, retrying in 30 seconds"
        logging.info(code)
        sleep(30)

        return

print(finvasia_session_token())
shoonya=get_login()  


def get_current_ist():
    india = timezone('Asia/Kolkata')
    ist = datetime.now(india)
    return ist

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + timedelta(days_ahead)


def find_atm(x, base=5):
    return base * round(x / base)

def check_dir(dir_path):
    isExist = os.path.exists(dir_path)
    if not isExist:
        os.makedirs(dir_path)
        print(f" {dir_path} directory is created!")

def get_data_from_nse(path_given):
    subprocess.Popen(f'curl "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY" -H "authority: beta.nseindia.com" -H "cache-control: max-age=0" -H "dnt: 1" -H "upgrade-insecure-requests: 1" -H "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36" -H "sec-fetch-user: ?1" -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9" -H "sec-fetch-site: none" -H "sec-fetch-mode: navigate" -H "accept-encoding: gzip, deflate, br" -H "accept-language: en-US,en;q=0.9,hi;q=0.8" --compressed  -o {path_given}', shell=True)
    sleep(2)
    

def fetch_expiry(ref_date):
    today_date = date.today().strftime("%d%b%Y")
    directory = '/home/trading042023/trading_image_master/momentum/option_chain_data/'
    check_dir(directory)

    option_file_name = f'option_chain_{today_date}.txt'
    file_path = directory + option_file_name

    if not os.path.isfile(file_path):
        mydata = get_data_from_nse(file_path)

    with open(f'{file_path}') as fileopen:
        lines = fileopen.readlines()
        mydata = json.loads(lines[0])
    try:
        expiry_dt_string = mydata['records']['expiryDates']
        expiry_dt = [(datetime.strptime(dt,'%d-%b-%Y').date() - ref_date).days for dt in expiry_dt_string]
        filtered_exp_lst = [(x,y) for x,y in enumerate(expiry_dt) if y >= 0]
        idx = min(filtered_exp_lst)[0]
        current_expiry = expiry_dt_string[idx]
        current_expiry = current_expiry.replace("-","").upper()
        current_expiry = current_expiry[:5] + current_expiry[-2:]
        print(f'Expiry pulled from NSE website: {current_expiry}')
        return current_expiry
    except:
        
        print('Expiry using date logic')
        if expiry_type == 'monthly':
            print('Expiry using date logic')
            current_expiry = ref_date.strftime('%d%b%Y').upper()
            current_expiry = current_expiry[:5] + current_expiry[-2:]
            return current_expiry

        if date.today().weekday() == 3: #it's thursday
            current_expiry = date.today().strftime('%d%b%Y').upper()
            current_expiry = current_expiry[:5] + current_expiry[-2:]
            return current_expiry
        else: #it's Mon, tues,wed,friday
            current_expiry = next_weekday(date.today(), 3).strftime('%d%b%Y').upper()
            current_expiry = current_expiry[:5] + current_expiry[-2:]
            return current_expiry 

def fin_nifty_expiry():
    if date.today().weekday() == 1: #it's tuesday
        current_expiry = date.today().strftime('%d%b%Y').upper()
        current_expiry = current_expiry[:5] + current_expiry[-2:]
        return current_expiry
    else: #it's Mon, tues,wed,friday
        current_expiry = next_weekday(date.today(), 1).strftime('%d%b%Y').upper()
        current_expiry = current_expiry[:5] + current_expiry[-2:]
        return current_expiry

def get_string(scp):
    if scp.upper() == 'NIFTY BANK':
        return 'BANKNIFTY'
    elif scp.upper() == 'NIFTY INDEX':
        return 'NIFTY'
    elif scp.upper() == 'FIN NIFTY':
        return 'FINNIFTY'

def get_token(exch, query):
  scp = shoonya.searchscrip(exchange=exch, searchtext=query)
  if scp != None:
      symbols = scp['values']
      for symbol in symbols:
          return symbol['token']

def download_df_from_shoonya(exch, my_script):
  today_dt = get_current_ist().today().replace(hour=0, minute=0, second=0, microsecond=0)
  week_ago = today_dt - timedelta(days=7)
  mytime = get_current_ist().replace(second=0, microsecond=0)

  tk = get_token(exch, my_script)

  df = pd.DataFrame(shoonya.get_time_price_series(exchange = exch, token = tk,
      starttime = week_ago.timestamp(), interval = 1))
  
  # print(df)
  if isinstance(df, pd.DataFrame):
      df['time'] = pd.to_datetime(df['time'], format = '%d-%m-%Y %H:%M:%S')
      df = df.sort_values(by = 'time', ascending = True)
      cols = ['into','inth','intl','intc','intvwap','intv','intoi','v','oi']
      df[cols] = df[cols].astype(float)
      spot = df[df['time'].dt.strftime('%Y-%m-%d') == today_dt.strftime('%Y-%m-%d')].copy()
      spot['time'] = spot['time'].dt.strftime('%Y-%m-%d %H:%M:00')
      spot['time'] = pd.to_datetime(spot['time'], format = '%Y-%m-%d')
      spot['timelast'] = spot['time'].dt.time
      spot = spot[spot['timelast'] != '15:30:00']
      cols = ['stat', 'time', 'ssboe', 'open', 'high', 'low', 'close', 'vwap','volume','coi','tvol','oi','timelast']
      spot.columns = cols
      mycols = ['time', 'open', 'high', 'low', 'close', 'volume','oi']
      spot_df = spot[mycols]
      return spot_df



if __name__ == '__main__':
    global expiry_type
    expiry_type = 'weekly'
    print("started")
    if expiry_type == 'monthly':
        ref_date = (datetime.today() + relativedelta(day=31, weekday=TH(-1))).date()
    else:
        ref_date  = datetime.today().date()
    expiry=fetch_expiry(ref_date)


    for sym in ['FIN NIFTY','NIFTY BANK', 'NIFTY INDEX', ]:
        strike_change = 50 if sym in ['NIFTY INDEX','FIN NIFTY'] else 100 #'FIN NIFTY'
        myspot = download_df_from_shoonya('NSE', sym)
        # myspot.drop('oi', axis = 1, inplace= True)
        high, low = find_atm(myspot['high'].max(), strike_change), find_atm(myspot['low'].min(), strike_change)

        for r in range(low - 3000,high + 3000, strike_change):
          for ce_pe in ['C', 'P']:
            exch = 'NFO'
            symb_prefix = get_string(sym)
            expiry2 = fin_nifty_expiry() if sym == 'FIN NIFTY' else expiry
            instrument = f"{symb_prefix}{expiry2}{ce_pe}{r}"
            try:
                i_df = download_df_from_shoonya(exch, instrument)
                if isinstance(i_df, pd.DataFrame):
                    myprefix = f"{r}{ce_pe}_"
                    date_col = f"{r}{ce_pe}_time"
                    i_df = i_df.add_prefix(myprefix)
                    i_df = i_df.rename(columns = {date_col:'time'})
                    myspot = myspot.merge(i_df, 'left', on = 'time')

            except Exception as e:
                pass
    
        myspot.rename(columns = {'time':'date'}, inplace = True)
        myspot['timestamp'] = myspot['date']
        myspot['ds'] = myspot['date']
        myspot['time'] = myspot['date'].dt.time
        myspot['expiry'] = pd.to_datetime(expiry,format = '%d%b%y').date()
        filename = f"{symb_prefix}-{get_current_ist().today().strftime('%Y-%m-%d')}.csv"

        filepath = f"/home/trading042023/trading_image_master/momentum/data/{filename}"
        myspot.to_csv(filepath, index= False)

        files = {'document':open(filepath, 'rb')}
        chatid = "@" #
        token = ""
        url = f"https://api.telegram.org/bot{token}/sendDocument?chat_id={chatid}&caption={filename}"
        print(url)
        resp = requests.post(url, files = files)
        print(resp)
        if resp.status_code == 200:
            os.remove(filepath)
