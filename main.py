# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import okx.Trade as Trade
import okx.MarketData as Market
from datetime import datetime
import pandas as pd

flag = "1"  # 0:live trading  1: demo trading

api_key = ""
secret_key = ""
passphrase = ""

ticker = "BTC-USDT-230519"

marketdata = Market.MarketAPI(flag=flag)


data = marketdata.get_ticker(instId=ticker)
last_price = data["data"][0]['last']

data_candles = marketdata.get_candlesticks(instId=ticker,bar='1H')
print(data_candles["data"])

df = pd.DataFrame(data_candles["data"],columns=["Timestamp","Open","High","Low","Close","Volume","Quantity","QuantityQuote","Confirm"])

df["Time"] = pd.to_timedelta(df["Timestamp"])
print(df)