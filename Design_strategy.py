from backtesting.lib import crossover, SignalStrategy,TrailingStrategy
import talib 
from backtesting import Strategy
import numpy as np

class MeanReversion(Strategy):
    #https://www.linkedin.com/pulse/algorithmic-trading-mean-reversion-using-python-bryan-chen/
    t = 6
    day_await = 3
    day = 1

    def countday(self,is_position):
        if is_position:
            self.day += 1
        else:
            self.day = 1

    def init(self):

            self.rsi_1 = self.I(talib.RSI, self.data.Close, timeperiod = self.t)
            self.upper, self.middle, self.lower = self.I(talib.BBANDS,self.data.Close, timeperiod = 10)
            #self.adx =self.I (talib.ADX, self.data.High, self.data.Low, self.data.Close)
            #self.sar = self.I(talib.SAR,self.data.High,self.data.Low)
            #self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod = 14)

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
        #istrend = self.adx > 30
        #uptrend = (price > self.SSMA) and (self.SSMA > self.LSMA)
        #downtrend = (price < self.SSMA) and (self.SSMA < self.LSMA)
        if not self.position:
            self.countday(True)
            if self.day > self.day_await:
                if closeCrossBBLower and rsi_buy : 
                    self.position.close()
                    self.buy(sl = long_sl,tp = long_tp)
                    self.countday(False)
                elif closeCrossBBUpper and rsi_sell:
                    self.position.close()
                    self.sell(sl = short_sl, tp = short_tp)
                    self.countday(False)

class MeanReversion_withRACD(Strategy):
    #https://www.linkedin.com/pulse/algorithmic-trading-mean-reversion-using-python-bryan-chen/
    t = 6
    x = 12
    y = 26
    z = 9
    def init(self):

            self.rsi_1 = self.I(talib.RSI, self.data.Close, timeperiod = self.t)
            self.upper, self.middle, self.lower = self.I(talib.BBANDS,self.data.Close, timeperiod = self.t)
            self.slow, self.fast = self.I(talib.MACD, self.data.Close, fastperiod=self.x, slowperiod=self.y, signalperiod=self.z)[0:2]

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
        macd_both_greater_0 = (self.slow > 0 ) and (self.fast > 0)
        macd_both_smaller_0 = (self.slow < 0 ) and (self.fast < 0)
        #istrend = self.adx > 30
        #uptrend = (price > self.SSMA) and (self.SSMA > self.LSMA)
        #downtrend = (price < self.SSMA) and (self.SSMA < self.LSMA)
        if macd_both_greater_0:
            if closeCrossBBLower and rsi_buy : 
                self.position.close()
                self.buy(sl = long_sl,tp = long_tp)
        elif macd_both_smaller_0:
            if closeCrossBBUpper and rsi_sell:
                self.position.close()
                self.sell(sl = short_sl, tp = short_tp)


class BB_RSI_OBV(Strategy):
    t = 6
    
    def init(self):
        float_data = np.array((self.data.Close), dtype='f8')
        float_data2 = np.array((self.data.Volume), dtype='f8')
        self.rsi_1 = self.I(talib.RSI, self.data.Close, timeperiod = self.t)
        self.upper, self.middle, self.lower = self.I(talib.BBANDS,self.data.Close, timeperiod = self.t)
        self.obv = self.I(talib.OBV,float_data,float_data2)
    def next(self):
        price = self.data["Close"][-1]
        long_sl = price * 0.96
        long_tp = price * 1.12
        short_sl = price * 1.04
        short_tp = price * 0.88

        is_above_MA = (self.data.Close > self.middle) and (self.data.Close < self.upper)
        is_above_rsi = self.rsi_1 > 50
        is_increasing_OBV = (self.obv[-1] > self.obv[-2]) and  (self.obv[-2] > self.obv [-3])

        if not self.position: 
            if is_above_MA and is_above_rsi and is_increasing_OBV:
                self.position.close()
                self.buy(sl = long_sl,tp = long_tp)
