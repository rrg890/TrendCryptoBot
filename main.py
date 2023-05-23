# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

flag = "1"  # 0:live trading  1: demo trading

api_key = "5bc09a62-ada3-4e02-b69e-83da969915ff"
secret_key = "33FCE1313BC8BE3CA9CE5361F0768774"
passphrase = "oleoleolE4."

ticker = "BTC-USDT-230526"


#df = pd.DataFrame(data_candles["data"],columns=["Timestamp","Open","High","Low","Close","Volume","Quantity","QuantityQuote","Confirm"])

import ccxt
import pandas as pd
import asyncio
import time
last_time = 0

class TradingBot:
    def __init__(self, api_key, secret_key, pass_phrase):
        self.exchange = ccxt.okex({
            'apiKey': api_key,
            'secret': secret_key,
            'password': pass_phrase,
            'options': {'defaultType': 'swap'}
        })
        self.symbol = ticker
        self.balance = None
        self.current_order = None

    def fetch_balance(self):
        self.balance = self.exchange.fetch_balance()['total']['USDT']

    def fetch_ohlcv(self):
        return self.exchange.fetch_ohlcv(self.symbol, '5m')

    def calculate_sma(self, data, window):
        return pd.DataFrame(data).loc[:,4].rolling(window).mean()

    def place_order(self, side, amount):
        #order_info = self.exchange.create_order(self.symbol, 'market', side, amount, {'leverage': 10})
        self.current_order = 1 #order_info['id']

    def cancel_order(self, order_id):
        self.current_order = 1 #self.exchange.cancel_order(order_id, self.symbol)

    def update(self):
        self.fetch_balance()
        ohlcv = self.fetch_ohlcv()
        sma_9 = self.calculate_sma(ohlcv, 9)
        sma_20 = self.calculate_sma(ohlcv, 20)
        # Check for buy signal
        time = pd.to_datetime(ohlcv[len(ohlcv)-1][0], unit='ms')
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

            self.place_order('buy', self.balance * 0.01)
            print('Compramos en vela: ' + str(time))

        # Check for short signal
        elif sma_9.iat[-3] > sma_20.iat[-3] and sma_9.iat[-2] < sma_20.iat[-2]:
            if self.current_order is not None:
                self.cancel_order(self.current_order)
                print('Cerrar operación compra en vela: ' + str(time))

            self.place_order('sell', self.balance * 0.01)
            print('Vendemos en vela: ' + str(time))


bot = TradingBot(api_key,secret_key,passphrase)
current_time = 0
while True:
    current_time = pd.DataFrame(bot.fetch_ohlcv())[0].iat[-2]
    #print("Current "+str(current_time))
    #print("Last " + str(last_time))
    if current_time!=last_time:
        bot.update()
        last_time = current_time
        time.sleep(10)
    else:
        time.sleep(2)
