#
# This is developed by @hobbiecode

# Links are
# Instagram:    https://www.instagram.com/hobbiecode/
# Youtube:      https://www.youtube.com/c/hobbiecode
# TikTok:       https://www.tiktok.com/@hobbiecode

flag = "0"  # 0:live trading  1: demo trading

api_key = "a7e765a8-5687-47b7-a72a-fc9fe036fbff"
secret_key = "07FEA49A36124D2BEF1D340D3326FBD9"
passphrase = "oleoleolE4."

ticker = 'BTC-USDT-SWAP'
timeframe = '1m' #[1m/3m/5m/15m/30m/1H/2H/4H]
leverage = 10
risk = 0.01


#df = pd.DataFrame(data_candles["data"],columns=["Timestamp","Open","High","Low","Close","Volume","Quantity","QuantityQuote","Confirm"])

import ccxt
import asyncio
import pandas as pd
import okx.Account as Account
import okx.MarketData as MarketData
import okx.Trade as Trade
import okx.Funding as Funding
import time
last_time = 0
ms = 0


if (timeframe=='1m'):
    ms = 60000
elif (timeframe=='3m'):
    ms = 180000
elif (timeframe=='5m'):
    ms = 300000
elif (timeframe=='15m'):
    ms = 900000
elif (timeframe=='30m'):
    ms = 1800000
elif (timeframe=='1H'):
    ms = 3600000
elif (timeframe=='2H'):
    ms = 7200000
elif (timeframe=='4H'):
    ms = 26400000
elif (timeframe=='1D'):
    ms = 86400000
elif (timeframe=='1W'):
    ms = 604800000

class TradingBot:
    def __init__(self, api_key, secret_key, pass_phrase):
        self.accountAPI = Account.AccountAPI(api_key, secret_key, pass_phrase, False, flag,debug=False)
        self.tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag,debug=False)
        self.marketdataAPI = MarketData.MarketAPI(api_key, secret_key, pass_phrase,False,flag=flag,debug=False)
        self.symbol = ticker
        self.balance = None
        self.max_contracts = None
        self.current_order = None

    def fetch_balance(self):
        self.balance = pd.DataFrame(self.accountAPI.get_account_balance()['data'][0]['details'])
        self.balance = self.balance.loc[self.balance['ccy']=='USDT']['availBal'][0]
        return self.balance

    def fetch_last_price(self):
        return self.marketdataAPI.get_ticker(instId=self.symbol)['data'][0]['last']

    def fetch_timestamp(self):
        data = pd.DataFrame(self.marketdataAPI.get_ticker(instId=self.symbol)['data'])['ts'].apply(pd.to_numeric)[0]
        return data

    def fetch_ohlcv(self):
        data = pd.DataFrame(self.marketdataAPI.get_candlesticks(instId=self.symbol,bar=timeframe,limit=100)['data'],
                            columns=['Open Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Quantity', 'Quote Quantity', 'Confirm'])
                            #columns=['Open Timestamp', 'Open', 'High', 'Low', 'Close', 'Confirm'])
        data['Open Timestamp'] =  data['Open Timestamp'].apply(pd.to_numeric)
        data["Timestamp"] = pd.to_datetime(data['Open Timestamp'],unit='ms',origin='unix')
        data = data.sort_values(by=['Timestamp'],ascending=True)
        return data

    def calculate_sma(self, data, window):
        return data.rolling(window).mean()

    def place_order(self, side):
        self.max_contracts = self.accountAPI.get_max_order_size(instId=self.symbol, tdMode='isolated')['data'][0]['maxBuy']
        self.accountAPI.set_leverage(instId=self.symbol, lever=leverage, mgnMode='isolated')
        rou = round(float(self.max_contracts) * risk)
        qty = 1
        if rou >= 1:
            qty = rou
        self.current_order = self.tradeAPI.place_order(instId=self.symbol,tdMode='isolated',ccy='USDT',side=side,ordType='market',sz=qty,reduceOnly=False)
        if (int(self.current_order['code'])==0):
            print("Order " + side + " correctly placed "+ str(self.symbol))

    def cancel_order(self, order_id):
        self.tradeAPI.cancel_order(instId=self.symbol,ordId=self.current_order['ordId'])
        self.current_order = 0

    def update(self,ohlcv):
        self.fetch_balance()
        #ohlcv = self.fetch_ohlcv()
        sma_9 = self.calculate_sma(ohlcv['Close'], 9)
        sma_20 = self.calculate_sma(ohlcv['Close'], 20)
        #print(sma_20)
        # Check for buy signal
        time = ohlcv['Timestamp'][0]
        print("--------------------------")
        print("Time: "+ str(time))
        print("Vela 3 de 9 perídodos: " + str(sma_9.iat[-3]))
        print("Vela 3 de 20 perídodos: " + str(sma_20.iat[-3]))
        print("Vela 2 de 9 perídodos: " + str(sma_9.iat[-2]))
        print("Vela 2 de 20 perídodos: " + str(sma_20.iat[-2]))

        if sma_9.iat[-3] < sma_20.iat[-3] and sma_9.iat[-2] > sma_20.iat[-2]:
            if self.current_order is not None:
                self.cancel_order(self.current_order)
                print('Cerrar operación venta en vela: ' + str(time))

            self.place_order('buy')
            print('Compramos en vela: ' + str(time))

        # Check for short signal
        elif sma_9.iat[-3] > sma_20.iat[-3] and sma_9.iat[-2] < sma_20.iat[-2]:
            if self.current_order is not None:
                self.cancel_order(self.current_order)
                print('Cerrar operación compra en vela: ' + str(time))

            self.place_order('sell')
            print('Vendemos en vela: ' + str(time))


bot = TradingBot(api_key,secret_key,passphrase)
current_time = 0
ohlcv = 0

while True:
    ohlcv = bot.fetch_ohlcv()
    current_time = ohlcv['Open Timestamp'][0]
    #print("Current "+str(current_time))
    #print("Last " + str(last_time))
    if current_time>last_time:
        bot.update(ohlcv)
        last_time = current_time
        time.sleep(10)
    else:
        time.sleep(2)
