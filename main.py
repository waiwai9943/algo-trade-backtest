import talib 
import datetime as dt #in-built module
import pandas as pd
from pandas_datareader import data
import yfinance as yf
from yahoo_fin import stock_info as si
import matplotlib.pyplot as plt
from matplotlib import style
from backtesting import Strategy, Backtest
from backtesting.lib import crossover, SignalStrategy,TrailingStrategy
from backtesting.test import GOOG, SMA
from pathlib import Path
import os
from tqdm import tqdm   

import Utimate_Algo_Trade as utimate
import Design_strategy as design

#requests.packages.urllib3.disable_warnings()i

#stockIDs =['BIIB','DAL','GILD','HST','IBM','INCY','UHS','VT']
stockIDs = ['^HSI']


Startyear = 2013

 

def getrawdata (stockID,Startyear):  ##using pandas
    yf.pdr_override()
    style.use('ggplot')

    start = dt.datetime(int(Startyear), 1, 1)
    end = dt.datetime.now()

    df = data.get_data_yahoo(stockID, start, end, interval = "1d", )
    df.to_csv('pddatareader_mpf.csv', index = True, header=True)
    return df

def rawdata2pd():
    return pd.read_csv("pddatareader_mpf.csv",index_col=0,header='infer', parse_dates= True)


def plotting(df):
    style.use('ggplot')
    ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)      #******refer to https://pythonprogramming.net/subplot2grid-add_subplot-matplotlib-tutorial/
    ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1,sharex=ax1)
    ax3 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1,sharex=ax1)
    ax1.plot(df.index, df['Adj Close'])
    ax1.plot(df.index, df['100ma'])
    ax1.plot(df.index, df['150ma'])
    #ax1.plot(df.index,df.loc['up','low'],color='black')
    #ax1.plot(df.index,df['low'],color='black')
    ax2.bar(df.index, df['Volume'])
    #ax3.plot(df.index,df['rsi_14'])
    plt.show()

def savefile_original(stat_raw):
    text_file= open(r"report\Original_Report.txt","w+")
    stat_raw = stat_raw.to_string()
    text_file.write(stat_raw)
    text_file.close()

def savefie_optimized(stats_optimized):
    text_file= open(r"report\Optimized_Report.txt","w+")
    stats_optimized = stats_optimized.to_string()
    text_file.write(stats_optimized)
    text_file.close()


class SmaCross(SignalStrategy,
               TrailingStrategy):
    n1 = 10
    n2 = 25
    
    def init(self):
        # In init() and in next() it is important to call the
        # super method to properly initialize the parent classes
        super().init()
        
        # Precompute the two moving averages
        sma1 = self.I(SMA, self.data.Close, self.n1)
        sma2 = self.I(SMA, self.data.Close, self.n2)
        
        # Where sma1 crosses sma2 upwards. Diff gives us [-1,0, *1*]
        signal = (pd.Series(sma1) > sma2).astype(int).diff().fillna(0)
        signal = signal.replace(-1, 0)  # Upwards/long only
        
        # Use 95% of available liquidity (at the time) on each order.
        # (Leaving a value of 1. would instead buy a single share.)
        entry_size = signal * .95
                
        # Set order entry sizes using the method provided by 
        # `SignalStrategy`. See the docs.
        self.set_signal(entry_size=entry_size)
        
        # Set trailing stop-loss to 2x ATR using
        # the method provided by `TrailingStrategy`
        self.set_trailing_sl(2)

class MACDcross(Strategy):
    x=12
    y=26
    z=9

    def init(self):
        self.fast = self.I(talib.MACD, self.data.Close, fastperiod=self.x, slowperiod=self.y, signalperiod=self.z)[1]
        self.slow = self.I(talib.MACD, self.data.Close, fastperiod=self.x, slowperiod=self.y, signalperiod=self.z)[0]
    
    def next(self):
        # If sma1 crosses above sma2, buy the asset
        if crossover(self.fast, self.slow):
            self.buy()
        # Else, if sma1 crosses below sma2, sell it
        elif crossover(self.slow, self.fast):
            self.sell()

class KDJcross(Strategy):
    x=9
    y=9
    z=3

    def init(self):
        self.fast = self.I(talib.STOCH,self.data.High,self.data.Low,self.data.Close, fastk_period= self.x, slowk_period=self.y, slowk_matype=0, slowd_period=self.z, slowd_matype=0)[0]
        self.slow = self.I(talib.STOCH,self.data.High,self.data.Low,self.data.Close, fastk_period= self.x, slowk_period=self.y, slowk_matype=0, slowd_period=self.z, slowd_matype=0)[1]

    def next(self):
        # If sma1 crosses above sma2, buy the asset
        if crossover(self.fast, self.slow):
            self.buy()
        # Else, if sma1 crosses below sma2, sell it
        elif crossover(self.slow, self.fast):
            self.sell()

class ParaSAR_EMACross(TrailingStrategy):
    #https://www.fxleaders.com/learn-forex/course/ch9-6-killer-combinations-for-trading-strategies/
    #https://www.litefinance.org/blog/for-beginners/trading-strategies/three-profitable-forex-trading-strategies/
    short_ema = 5
    long_ema = 25
    t = 9

    def init(self):

        self.ema1 = self.I(talib.EMA, self.data.Close, timeperiod = self.short_ema)
        self.ema2 = self.I(talib.EMA, self.data.Close, timeperiod = self.long_ema)
        self.sar = self.I(talib.SAR,self.data.High,self.data.Low)
    def next(self):
        price = self.data["Close"][-1]
        long_sl = price * 0.96
        long_tp = price * 1.08
        short_sl = price * 1.04
        short_tp = price * 0.92
        if crossover(self.ema1, self.ema2) and price > self.sar :
            self.position.close()
            self.buy(sl = long_sl)
        elif crossover(self.ema2, self.ema1) and price < self.sar:
            self.position.close()
            self.sell(sl = short_sl)



class ADX_RSI(TrailingStrategy):
    #https://medium.com/codex/does-combining-adx-and-rsi-create-a-better-profitable-trading-strategy-125a90c36ac    
    rsi_t = 6
    dmi_t = 14
    def init(self):
        self.adx =self.I (talib.ADX, self.data.High, self.data.Low, self.data.Close)
        self.pdm = self.I(talib.PLUS_DM, self.data.High, self.data.Low, timeperiod = self.dmi_t)
        self.ndm = self.I(talib.MINUS_DM, self.data.High, self.data.Low, timeperiod = self.dmi_t)
        self.rsi = self.I(talib.RSI, self.data.Close,  timeperiod = self.rsi_t)
    def next(self):
        price = self.data["Close"][-1]
        long_sl = price * 0.96
        long_tp = price * 1.08
        short_sl = price * 1.04
        short_tp = price * 0.92
        condition1 = self.adx > 35
        if not self.position:
            if condition1 and self.rsi > 30 and (self.ndm >self.pdm):
                self.position.close()
                self.buy()
            elif condition1 and self.rsi <70 and (self.pdm > self.ndm):
                self.position.close()
                self.sell()



class MeanReversion(Strategy):
    #https://www.linkedin.com/pulse/algorithmic-trading-mean-reversion-using-python-bryan-chen/
    ssma = 20
    lsma = 180
    t = 6

    def init(self):

            self.rsi_1 = self.I(talib.RSI, self.data.Close, timeperiod = self.t)
            self.upper, self.middle, self.lower = self.I(talib.BBANDS,self.data.Close, timeperiod = 10)
            self.adx =self.I (talib.ADX, self.data.High, self.data.Low, self.data.Close)
            #self.sar = self.I(talib.SAR,self.data.High,self.data.Low)
            #self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod = 14)
            #self.SSMA = self.I(talib.SMA, self.data.Close, timeperiod = self.ssma)
            #self.LSMA = self.I(talib.SMA, self.data.Close, timeperiod = self.lsma)
    def next(self):
        price = self.data["Close"][-1]
        long_sl = price * 0.96
        long_tp = price * 1.12
        short_sl = price * 1.04
        short_tp = price * 0.88

        closeCrossBBLower = (self.data.Close < self.lower) 
        closeCrossBBUpper  = (self.data.Close > self.upper)
        rsi_buy = self.rsi_1 < 30 
        rsi_sell = self.rsi_1 >70 
        istrend = self.adx > 30
        #uptrend = (price > self.SSMA) and (self.SSMA > self.LSMA)
        #downtrend = (price < self.SSMA) and (self.SSMA < self.LSMA)
        if not istrend:
            if closeCrossBBLower and rsi_buy : 
                self.position.close()
                self.buy(sl = long_sl,tp = long_tp)
            elif closeCrossBBUpper and rsi_sell:
                self.position.close()
                self.sell(sl = short_sl, tp = short_tp)
        #elif istrend:
        #    if price < self.sar and not self.position:
        #        self.position.close()
        #        self.buy(sl = long_sl)
        #    elif price > self.sar and not self.position:
        #        self.position.close()
        #        self.sell(sl = short_sl)
        print ('')


class MACDcross_RSI(Strategy):
    x=9
    y=11
    z=25
    rsi_t = 9


    def init(self):
        self.fast = self.I(talib.MACD, self.data.Close, fastperiod=self.x, slowperiod=self.y, signalperiod=self.z)[1]
        self.slow = self.I(talib.MACD, self.data.Close, fastperiod=self.x, slowperiod=self.y, signalperiod=self.z)[0]
        self.rsi = self.I(talib.RSI, self.data.Close,  timeperiod = self.rsi_t)
    def next(self):
        price = self.data["Close"][-1]
        long_sl = price * 0.96
        long_tp = price * 1.12
        short_sl = price * 1.04
        short_tp = price * 0.88
        if crossover(self.fast, self.slow) and self.fast > 0 and self.rsi > 50  :
            self.position.close()
            #self.buy(sl = long_sl,tp = long_tp)
            self.buy()
        elif crossover(self.slow, self.fast) and self.fast < 0 and self.rsi < 50:
            self.position.close()
            #self.sell(sl = short_sl, tp = short_tp)
            self.sell()



def one_stock (strategies):
    for stockID in stockIDs:
        df = getrawdata (stockID,Startyear)
        #df= pd.read_csv(r'pddatareader_mpf.csv',delimiter=',')
        #
        #
        #print (df)
        #
        bt = Backtest(df, strategies, cash=13000000,hedging = True , commission=.002,
            trade_on_close=True, 
            exclusive_orders=True)

        stat_raw = bt.run()

        print (stat_raw)
        stat_raw_df= pd.Series(stat_raw, name = stockID)
        stat_raw_df.to_csv("%s_%s.csv"%(strategies.__name__,stockID))
        bt.plot(plot_volume= True, plot_pl=True, filename ="%s_%s"%(strategies.__name__,stockID) )
        #optimization(bt)

def optimization (bt):    
    ############### Parameters Optimization #####

    stats_optimized = bt.optimize( 
                       rsi_t=range(6,14,1),
                       x = range(5,12,1),
                       y = range(12,26,1),
                       z = range (5,10,1),
                       rsi_thresold_overbuy = [70,80,90],
                       rsi_thresold_oversell = [10,20,30],
                       #BB_t=range(3,10,1),
                       #ATR_t = range(5,15,3),
                       maximize='Sharpe Ratio',
                       #maximize='Win Rate [%]',
                       constraint= lambda para : para.x < para.y,
                       return_heatmap=True
                       )
    bt.plot(plot_volume= True, plot_pl=True)
    #savefie_optimized(stats_optimized)
    #savefile_original(stat_raw)
    print ("Optimized Data\n",stats_optimized)
    #stat_raw['_equity_curve'].to_csv('equity_curve.csv')
    #stat_raw['_trades'].to_csv('Trades_Records.csv') 
    print ('')

class L200MA_B30RSI(TrailingStrategy):
    #https://www.tradingwithrayner.com/mean-reversion-trading-strategy/
    #The market is above the 200-day moving average
    #10-period RSI is below 30
    #Buy on the next day’s open
    #Exit when the 10-period RSI crosses above 40 (or after 10 trading days)
    RSI_t = 10
    MA_T = 200


    def init(self):
            super().init()
            self.ma = self.I(talib.MA, self.data.Close, timeperiod = self.MA_T)
            self.rsi = self.I(talib.RSI, self.data.Close, timeperiod = self.RSI_t)
        
    def next(self):

        price = self.data["Close"][-1]
        long_sl = price * 0.96
        long_tp = price * 1.08
        short_sl = price * 1.04
        short_tp = price * 0.92
        #risk_reward ratio = 2

        condition_1 = (self.data.Close > self.ma)
        condition_2 =  (self.rsi < 30)


        if  condition_1 and condition_2 and not self.position: 
            self.position.close()
            self.buy(sl = long_sl)

        if self.position.is_long:
            if  self.rsi > 40:
                self.position.close()

def get_allstock ():
    tickers = si.tickers_sp500()
    start = dt.datetime.now()- dt.timedelta(days=3650)
    end = dt.datetime.now()

    for ticker in tickers:
        print('getting {ticker}'.format(ticker = ticker))
        try:
            instrument = yf.Ticker(ticker)
            df=instrument.history(start = start, end = end)
            df.to_csv(f'stock_data/{ticker}.csv')
        except:
            pass
        
    
    
def all_stock (strategies):
    combined = pd.Series (dtype = "object")
    datapath = './stock_data'
    for file in tqdm(Path(datapath).glob('*.csv')):
        df = pd.read_csv(file,delimiter = ',', index_col='Date', parse_dates=True)
        df.dropna(inplace = True)
        try:
            bt = Backtest(df, strategies, cash=13000,hedging = True , commission=.002,
            trade_on_close=True, 
            exclusive_orders=True)

            stat_raw = bt.run()
            _ , ticker_name = os.path.split (str(file))
            
            #get the stock sector
            get_sector = yf.Ticker(ticker_name[:-4].replace("_","")) ##erase the character "_"
            stat_raw['Sector'] = get_sector.info['sector']

            #combine into one excel
            s = pd.Series(stat_raw, name = ticker_name[:-4])
            combined = pd.concat([combined,s],axis=1)
        except:
            pass
    combined = combined.T.iloc[1:,:]
    combined.to_csv('all_results_MACD_RSI.csv')



if __name__ == "__main__":
    #df = getrawdata (stockID,Startyear)
    #df ['adf'] = df['Close'].rolling(60).apply(adf)
    #df.to_csv('with_adf.csv')

    one_stock(MACDcross_RSI)
    #one_stock(MeanReversion)
    #get_allstock()
    #all_stock(MACDcross_RSI)      



