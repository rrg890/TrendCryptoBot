# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

flag = "0"  # 0:live trading  1: demo trading

api_key = "5bc09a62-ada3-4e02-b69e-83da969915ff"
secret_key = "33FCE1313BC8BE3CA9CE5361F0768774"
passphrase = "oleoleolE4."

ticker = "BTC-USDT-SWAP"
timeframe = "4H" #[1m/3m/5m/15m/30m/1H/2H/4H]


#df = pd.DataFrame(data_candles["data"],columns=["Timestamp","Open","High","Low","Close","Volume","Quantity","QuantityQuote","Confirm"])

import ccxt
import pandas as pd
import okx.Account as Account
import okx.MarketData as MarketData
import okx.Trade as Trade
import time
last_time = 0

class TradingBot:
    def __init__(self, api_key, secret_key, pass_phrase):
        self.accountAPI = Account.AccountAPI(api_key, secret_key, pass_phrase, False, flag)
        self.tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
        self.marketdataAPI = MarketData.MarketAPI(flag=flag)
        self.symbol = ticker
        self.balance = None
        self.current_order = None

    def fetch_balance(self):
        self.balance = self.accountAPI.get_account_balance()

    def fetch_last_price(self):
        return self.marketdataAPI.get_ticker(instId=self.symbol)['data'][0]['last']

    def fetch_ohlcv(self):
        data = pd.DataFrame(self.marketdataAPI.get_mark_price_candlesticks(instId=self.symbol,bar=timeframe,limit=20)['data'],
                            columns=['Open Timestamp', 'Open', 'High', 'Low', 'Close', 'Confirm'])
                            #columns=['Open Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Quantity', 'Quote Quantity', 'Confirm'])
        data["Timestamp"] = pd.to_datetime(data['Open Timestamp'],unit='ms',origin='unix')
        data = data.sort_values(by=['Timestamp'],ascending=True)
        return data

    def calculate_sma(self, data, window):
        return data.rolling(window).mean()

    def place_order(self, side, amount):
        #order_info = self.exchange.create_order(self.symbol, 'market', side, amount, {'leverage': 10})
        self.current_order = 1 #order_info['id']

    def cancel_order(self, order_id):
        self.current_order = 1 #self.exchange.cancel_order(order_id, self.symbol)

    def update(self):
        #self.fetch_balance()
        ohlcv = self.fetch_ohlcv()
        sma_9 = self.calculate_sma(ohlcv['Close'], 9)
        sma_20 = self.calculate_sma(ohlcv['Close'], 20)
        print(ohlcv['Close'])
        #print(sma_20)
        # Check for buy signal
        time = ohlcv['Timestamp'][0]
        print("--------------------------")
        print("Time: "+ str(time))
        print("Vela 3 de 9 perídodos: " + str(sma_9.iat[-3]))
        print("Vela 3 de 20 perídodos: " + str(sma_20.iat[-3]))
        print("Vela 2 de 9 perídodos: " + str(sma_9.iat[-2]))
        print("Vela 2 de 20 perídodos: " + str(sma_20.iat[-2]))




bot = TradingBot(api_key,secret_key,passphrase)
print(bot.fetch_last_price())
print(bot.fetch_ohlcv())
bot.update()