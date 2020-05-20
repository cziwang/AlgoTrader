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

    # Universe of selected stocks
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
    stock1_curr = data_1[days-1]
    stock2_curr = data_2[days-1]
    spread_curr = stock1_curr - stock2_curr

    # Find 5-day moving averages
    move_avg_days = 5
    # Moving averages for stock1
    stock1_last = []
    for i in range(move_avg_days):
        stock1_last.append(data_1[(days-1)-i])
    stock1_hist = pd.DataFrame(stock1_last)
    stock1_mavg = stock1_hist.mean()
    #Moving average for stock2
    stock2_last = []
    for i in range(move_avg_days):
        stock2_last.append(data_2[(days-1)-i])
    stock2_hist = pd.DataFrame(stock2_last)
    stock2_mavg = stock2_hist.mean()

    #Sread_avg
    spread_avg = min(stock1_mavg - stock2_mavg)
    #Spread_factor
    spreadFactor = .01
    wideSpread = spread_avg*(1+spreadFactor)
    thinSpread = spread_avg*(1-spreadFactor)
    #Calc_of_shares_to_trade
    cash = float(account.buying_power)
    limit_stock1 = cash//stock1_curr
    limit_stock2 = cash//stock2_curr
    number_of_shares = min(limit_stock1, limit_stock2)/2
    
    #Trading_algo
    portfolio = api.list_positions()
    clock = api.get_clock()
    
    if clock.is_open == True:
        if bool(portfolio) == False: # if no positions are held
            #detect a wide spread
            if spread_curr > wideSpread:
                #short top stock
                api.submit_order(symbol = stock1,qty = number_of_shares,side = 'sell',type = 'market',time_in_force ='day')
                #Long bottom stock
                api.submit_order(symbol = stock2,qty = number_of_shares,side = 'buy',type = 'market',time_in_force = 'day')
                mail_content = "Trades have been made, short top stock and long bottom stock"
            #detect a tight spread
            elif spread_curr < thinSpread:
                #long top stock
                api.submit_order(symbol = stock1,qty = number_of_shares,side = 'buy',type = 'market',time_in_force = 'day')
                #short bottom stock
                api.submit_order(symbol = stock2,qty = number_of_shares,side = 'sell',type = 'market',time_in_force ='day')
                mail_content = "Trades have been made, long top stock and short bottom stock"
        else:
            wideTradeSpread = spread_avg *(1+spreadFactor + .03)
            thinTradeSpread = spread_avg *(1+spreadFactor - .03)
            if spread_curr <= wideTradeSpread and spread_curr >=thinTradeSpread:
                api.close_position(stock1)
                api.close_position(stock2)
                mail_content = "Position has been closed"
            else:
                mail_content = "No trades were made, position remains open"
                pass
    else:
        mail_content = "The Market is Closed"
        
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    
    done = 'Mail Sent'

    return done




