import os 
import alpaca_trade_api as tradeapi
import pandas as pd 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


APCA_API_KEY_ID = 'PKK4H3QTLFRHA9RMH1KM'
APCA_API_SECRET_ID = 'JYBQUDKXyoWR34D7ZMKBt1wLwTZGpRTuTn74ea4h'
APCA_API_BASE_URL = "https://paper-api.alpaca.markets" # the paper trading URL
APCA_API_DATA_URL = 'https://data.alpaca.markets'


def pairs_trading_algo():
    # Specify paper trading environment
    os.environ["APCA_API_BASE_URL"] = "https://paper-api.alpaca.markets"
    # Insert API credentials
    api = tradeapi.REST('PKK4H3QTLFRHA9RMH1KM', 'JYBQUDKXyoWR34D7ZMKBt1wLwTZGpRTuTn74ea4h', api_version='v2')
    account = api.get_account()

    # Setup automailing feature
    sender_address = 'chrisalgotrade19@gmail.com'
    sender_pass = 'Fanfan0825'
    receiver_address = 'chrisalgotrade19@gmail.com'
    # Setup MIME (Multipurpose Internet Mail Extension)
    message = MIMEMultipart()
    message['From'] = 'Trading Bot'
    message['To'] = receiver_address
    message['Subject'] = 'Algo Bot Update'  #The subject line
    
    """
    BUILD A STRATEGY TO TRADE HERE
    
    Current strategy is sloppy; Accesses free data on Alpaca through
    IEX Exchange, and created needed variables for trading logic
    with 5-day moving averages.

    Example uses ADBE and AAPL
    """

    # Selection of stocks
    days = 1000
    stock1 = 'ADBE'
    stock2 = 'AAPL'
    # Put historical Data into variables
    # get_barset(symbols, timeframe, limit, start-None, end = None, after=None, until=None)
    # returns a set of Bars
    # Information on bars: https://alpaca.markets/docs/api-documentation/api-v2/market-data/bars/
    stock1_barset = api.get_barset(stock1, 'day', limit=days)
    stock2_barset = api.get_barset(stock2, 'day', limit=days)
    stock1_bars = stock1_barset[stock1]
    stock2_bars = stock2_barset[stock2]
    #Grab stock1 data and put into lsit
    data_1 = []
    times_1 = []
    for i in range(days):
        close = stock1_bars[i].c # .c property gets close price of bar
        time = stock1_bars[i].t
        data_1.append(close)
        times_1.append(time)
    
    #Repeat with second stock
    data_2 = []
    times_2 = []
    for i in range(days):
        close = stock1_bars[i].c    # .c property gets close price of bar
        time = stock1_bars[i].t
        data_2.append(close)
        times_2.append(time)v
    # join two datasets into panda dataframe
    hist_close = pd.DataFrame(data_1, columns=[stock1])
    hist_close[stock2] = data_2
    # Current spread between two stocks
    stock1_curr



