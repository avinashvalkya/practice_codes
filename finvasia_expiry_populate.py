import pandas as pd
import datetime
from datetime import timedelta

def get_expiry(Symbol):
    req = "https://api.shoonya.com/NFO_symbols.txt.zip"
    df_exp_date = pd.read_csv(req, compression='zip')
    print(df_exp_date)
    df_exp_date.columns = [col.strip() for col in df_exp_date.columns]
    df_exp_date = df_exp_date[(df_exp_date['Instrument'] == 'OPTIDX') & (df_exp_date['Symbol'] == Symbol)]
    df_exp_date['expiry'] = pd.to_datetime(df_exp_date['Expiry'])

    near_week_expiry = pd.Timestamp(datetime.datetime.now().date() + timedelta(days =30))
    next_week_expiry = pd.Timestamp(datetime.datetime.now().date() + timedelta(days =30))

    # near week expiry
    for i in df_exp_date.index:
        near_week_expiry = min(df_exp_date['expiry'][i], near_week_expiry)
        if (near_week_expiry == df_exp_date['expiry'][i]):
            bn_sym_near = df_exp_date['TradingSymbol'][i]
    # next week expiry
    for i in df_exp_date.index:
        if df_exp_date['expiry'][i] != near_week_expiry:
            next_week_expiry = min(df_exp_date['expiry'][i], next_week_expiry)
            if (next_week_expiry == df_exp_date['expiry'][i]):
                bn_sym_next = df_exp_date['TradingSymbol'][i]
    ## monthly expiry            
    df_exp_monthly = df_exp_date[(df_exp_date['expiry'].dt.month == pd.Timestamp.now().date().month) & 
                                 (df_exp_date['expiry'].dt.year == pd.Timestamp.now().date().year)]
    if df_exp_monthly.empty == False:
        bn_sym_monthly = df_exp_monthly[df_exp_monthly['expiry'].dt.date == df_exp_monthly['expiry'].max().date()].head(1)['TradingSymbol'].values[0][:-7]
    else:
        df_exp_monthly = df_exp_date[(df_exp_date['expiry'].dt.month == pd.Timestamp.now().date().month+1) & 
                                     (df_exp_date['expiry'].dt.year == pd.Timestamp.now().date().year)]
        bn_sym_monthly = df_exp_monthly[df_exp_monthly['expiry'].dt.date == df_exp_monthly['expiry'].max().date()].head(1)['TradingSymbol'].values[0][:-7]
    print(bn_sym_monthly)
    print(bn_sym_near)
    if(Symbol == 'NIFTY'):
        bn_sym_near = bn_sym_near[:-6]
        bn_sym_next = bn_sym_next[:-6]
    elif(Symbol == 'BANKNIFTY'):
        bn_sym_near = bn_sym_near[:-6]
        bn_sym_next = bn_sym_next[:-6]
    print('Near week expiry is : ', bn_sym_near, '\nNext week expiry is : ', bn_sym_next)
    return (bn_sym_near, bn_sym_next)

get_expiry('NIFTY')
