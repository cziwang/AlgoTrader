import os 
import alpaca_trade_api as tradeapi
import pandas as pd 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Specify paper trading environment
os.environ["APCA_API_BASE_URL"] = "https://paper-api.alpaca.markets"
# Insert API credentials
api = tradeapi.REST('<PRIVATE KEY ID>', '<PRIVATE SECRET KEY ID>', api_version='v2')
account = api.get_account()


"""
BUILD A STRATEGY TO TRADE HERE

Current strategy is based off of pairs trade; Accesses free data on Alpaca through
IEX Exchange, and created needed variables for trading logic
with 5-day moving averages.

Currently uses ADBE and AAPL
"""
def pairs_trading_algo():
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
    stock1_mavg = getMovingAverage(data_1, 5, days)
    stock2_mavg = getMovingAverage(data_2, 5, days)

    #Sread_avg
    spread_avg = min(stock1_mavg - stock2_mavg)
    #Spread_factor
    spreadFactor = .01
    wide_spread = spread_avg*(1+spreadFactor)
    thin_spread = spread_avg*(1-spreadFactor)
    #Calc_of_shares_to_trade
    cash = float(account.buying_power)
    limit_stock1 = cash//stock1_curr
    limit_stock2 = cash//stock2_curr
    num_shares = min(limit_stock1, limit_stock2)/2

    # Trade according to pairs trade strategy
    trade(spread_curr, spread_avg, thin_spread, wide_spread, num_shares)
    
    


"""
This function sets up automailing feature
Will send email with MAIL_CONTENT to RECEIVER_ADDRESS when trade
is made.
"""
def autoMail(mail_content):
    sender_address = 'chrisalgotrade19@gmail.com'
    sender_pass = '************S'
    receiver_address = 'chrisalgotrade19@gmail.com'

    message = MIMEMultipart()
    message['From'] = 'Trading Bot'
    message['To'] = receiver_address
    message['Subject'] = 'Algo Bot Update'

    message.attach(MIMEText(mail_content, 'plain'))

    session = smtplib.SMTP('smtp.gmail.com', 587) 
    session.starttls() 
    session.login(sender_address, sender_pass) 
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()


"""
Gets the moving average of DATA the past AVG_NUM_DAYS
starting from DAYS
"""
def getMovingAverage(data, avg_num_days, days):
    stock_last = []
    for i in range(avg_num_days):
        stock_last.append(data[(days-1)-i])
    stock_hist = pd.DataFrame(stock1_last)
    stock_mavg = stock1_hist.mean()
    return stock_mavg


"""
Trades according to pairs strategy.
"""
def trade(curr_spread, spread_avg, thin_spread, wide_spread, num_shares):
    portfolio = api.list_positions()
    clock = api.get_clock()

   if clock.is_open == True:
        if bool(portfolio) == False: # if no positions are held
            if curr_spread > wide_spread:
                #short top stock
                api.submit_order(symbol = stock1,qty = num_shares,side = 'sell',type = 'market',time_in_force ='day')
                #Long bottom stock
                api.submit_order(symbol = stock2,qty = num_shares,side = 'buy',type = 'market',time_in_force = 'day')
                mail_content = "Trades have been made, short top stock and long bottom stock"
            #detect a tight spread
            elif curr_spread < thin_spread:
                #long top stock
                api.submit_order(symbol = stock1,qty = num_shares,side = 'buy',type = 'market',time_in_force = 'day')
                #short bottom stock
                api.submit_order(symbol = stock2,qty = num_shares,side = 'sell',type = 'market',time_in_force ='day')
                mail_content = "Trades have been made, long top stock and short bottom stock"
        else:
            wideTradeSpread = spread_avg *(1+spreadFactor + .03)
            thinTradeSpread = spread_avg *(1+spreadFactor - .03)
            if curr_spread <= wideTradeSpread and curr_spread >=thinTradeSpread:
                api.close_position(stock1)
                api.close_position(stock2)
                mail_content = "Position has been closed"
            else:
                mail_content = "No trades were made, position remains open"
                pass
    else:
        mail_content = "The Market is Closed"

    autoMail(mail_content)

    done = 'Mail Sent'
    return done
