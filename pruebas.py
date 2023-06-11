#
# This is developed by @hobbiecode

# Links are
# Instagram:    https://www.instagram.com/hobbiecode/
# Youtube:      https://www.youtube.com/c/hobbiecode
# TikTok:       https://www.tiktok.com/@hobbiecode

########################################################
################## PARÁMETROS ##########################
########################################################

ticker = 'LTC-USDT-SWAP'    # Activo a operar, hay que poner el que aparece en la URL cuando lo abres en OKX
timeframe = '5m'            # [1m/3m/5m/15m/30m/1H/2H/4H/D1/W1]
leverage = 10               # Apalancamiento
risk = 0.01                 # Riesgo por operación. Ejemplo: si está en 0.01 significa que abrirá una operación de X contratos, dónde X representa el 1% de los contratos máximos que puedes abrir en dicho activo
ma_fast = 9                 # Media móvil rápida
ma_slow = 20                # Media móvil lenta

########################################################
################ FIN PARÁMETROS ########################
########################################################


import pandas as pd
import okx.Account as Account
import okx.MarketData as MarketData
import okx.Trade as Trade
import time

# General internal parameters
last_time = 0
ms = 0

flag = "0"  # 0:live trading  1: demo trading

# Script for loading credentials from a file
with open('credentials.txt') as f:
    lines = f.readlines()
api_key = str(lines[0].replace("\n",""))
secret_key = str(lines[1].replace("\n",""))
passphrase = str(lines[2].replace("\n",""))

class TradingBot:

    # Initialize variables connected to exchange account
    def __init__(self, api_key, secret_key, pass_phrase):
        self.accountAPI = Account.AccountAPI(api_key, secret_key, pass_phrase, False, flag,debug=False)
        self.tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag,debug=False)
        self.marketdataAPI = MarketData.MarketAPI(api_key, secret_key, pass_phrase,False,flag=flag,debug=False)
        self.symbol = ticker
        self.balance = None
        self.max_contracts = None
        self.current_order = None

    # Get the balance availabe in your account
    def fetch_balance(self):
        self.balance = pd.DataFrame(self.accountAPI.get_account_balance()['data'][0]['details'])
        self.balance = self.balance.loc[self.balance['ccy']=='USDT']['availBal'][0]
        return self.balance

    # Get the last price for a certain symbol
    def fetch_last_price(self):
        return self.marketdataAPI.get_ticker(instId=self.symbol)['data'][0]['last']

    # Get the current timestamp of the exchange
    def fetch_timestamp(self):
        data = pd.DataFrame(self.marketdataAPI.get_ticker(instId=self.symbol)['data'])['ts'].apply(pd.to_numeric)[0]
        return data

    # Get historical candlesticks
    def fetch_ohlcv(self):
        data = pd.DataFrame(self.marketdataAPI.get_candlesticks(instId=self.symbol, bar=timeframe, limit=100)['data'],
                            columns=['Open Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Quantity', 'Quote Quantity', 'Confirm'])
                            #columns=['Open Timestamp', 'Open', 'High', 'Low', 'Close', 'Confirm'])
        data['Open Timestamp'] =  data['Open Timestamp'].apply(pd.to_numeric)
        data["Timestamp"] = pd.to_datetime(data['Open Timestamp'], unit='ms', origin='unix')
        data = data.sort_values(by=['Timestamp'], ascending=True)
        return data

    # Calculate moving averages
    def calculate_sma(self, data, window):
        return data.rolling(window).mean()

    # Open positions (buy and sell)
    def place_order(self, side):
        self.max_contracts = self.accountAPI.get_max_order_size(instId=self.symbol, tdMode='isolated')['data'][0]['maxBuy']
        self.accountAPI.set_leverage(instId=self.symbol, lever=leverage, mgnMode='isolated')
        rou = round(float(self.max_contracts) * risk)
        qty = 1
        if rou >= 1:
            qty = rou
        self.current_order = self.tradeAPI.place_order(instId=self.symbol, tdMode='isolated', ccy='USDT', side=side, ordType='market', sz=qty, reduceOnly=False)

        if int(self.current_order['code']) == 0:
            print("Order " + side + " correctly placed " + str(self.symbol))
        else:
            print("Error message: " + str(self.current_order['data'][0]['sMsg']))

    # Close positions
    def cancel_order(self):
        self.tradeAPI.close_positions(instId=self.symbol,mgnMode='isolated')
        #self.tradeAPI.cancel_order(instId=self.symbol,ordId=self.current_order['data'][0]['ordId'])
        self.current_order = 0

    # Strategy logic
    def update(self,ohlcv):
        self.fetch_balance()

        sma_9 = self.calculate_sma(ohlcv['Close'], ma_fast)
        sma_20 = self.calculate_sma(ohlcv['Close'], ma_slow)

        # Check for buy signal
        time = ohlcv['Timestamp'][0]
        print("--------------------------")
        print("Time: "+ str(time))
        print("Vela 3 de "+str(ma_fast)+" perídodos: " + str(sma_9.iat[-3]))
        print("Vela 3 de "+str(ma_slow)+" perídodos: " + str(sma_20.iat[-3]))
        print("Vela 2 de "+str(ma_fast)+" perídodos: " + str(sma_9.iat[-2]))
        print("Vela 2 de "+str(ma_slow)+" perídodos: " + str(sma_20.iat[-2]))

        # Check for long signal
        if sma_9.iat[-3] < sma_20.iat[-3] and sma_9.iat[-2] > sma_20.iat[-2]:
            if self.current_order is not None:
                self.cancel_order()
                print('Cerrar operación venta en vela: ' + str(time))

            self.place_order('buy')
            print('Compramos en vela: ' + str(time))

        # Check for short signal
        elif sma_9.iat[-3] > sma_20.iat[-3] and sma_9.iat[-2] < sma_20.iat[-2]:
            if self.current_order is not None:
                self.cancel_order()
                print('Cerrar operación compra en vela: ' + str(time))

            self.place_order('sell')
            print('Vendemos en vela: ' + str(time))


bot = TradingBot(api_key,secret_key,passphrase)
bot.place_order('buy')
time.sleep(2)
bot.cancel_order()

