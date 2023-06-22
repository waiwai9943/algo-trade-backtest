from backtesting.lib import crossover, SignalStrategy,TrailingStrategy
import talib 
from backtesting import Strategy

class RSI3070_ExitATR(Strategy):
    '''
    Ultimate Algorithmic Trading System Toolbox
    --> Welles Wilders RSI System P- code
    RSI14 < 30 long
        TP: close > entryprice + 3* ATR 10 
        SL:  close < entryprice -1* ATR 10
    RSI14 > 70 short
        SL:  close < entryprice +1* ATR 10 
        TP: close > entryprice - 3* ATR 10
    After each trade it will stop for 10 days so as to avoid frequent trade.

    Optimized Parameters:
    rsi_t = 13, ATR_t = 10, day_await = 8


    '''
    rsi_t = 12
    ATR_t = 10
    day_await = 7
    day = 1 #initial

    def countday(self,is_position):
        if is_position:
            self.day += 1
        else:
            self.day = 1

    def init(self):
            self.rsi_1 = self.I(talib.RSI, self.data.Close, timeperiod = self.rsi_t)
            self.atr= self.I (talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod = self.ATR_t)
    def next(self):
        price = self.data["Close"][-1]
        try:
            if not self.position:
                self.countday(True)
                if self.day > self.day_await:
                    if self.rsi_1 < 30 : 
                        long_tp = price + 3*self.atr
                        long_sl = price - 1*self.atr
                        self.buy(sl = long_sl,tp = long_tp)
                        self.countday(False)
                    elif self.rsi_1 > 70:
                        short_tp = price -3*self.atr
                        short_sl = price + 1*self.atr
                        self.sell(sl = short_sl, tp = short_tp)
                        self.countday(False)
        except:
            pass


class Mean_Reversion_box3_4(Strategy):
    '''
    Ultimate Algorithmic Trading System Toolbox
    --> Mean Reversion System
    1) 200 days MA
    2) 5-days BB% value
    3) 3-days BB% moving average of the BB% value
    
    Buy: close > MAV(c,200) and MAV (BB%,3) < 0.25/
        Close: BB% >.75 or close < entryPrice - 2000/big-pointvalue
    sell: close < MAV(c,200) and MAV (BB%,3) > 0.75
        close: BB% <0.25 or close > entryPrice + 2000/big-pointvalue
    '''
    ma = 200
    BB_t = 5
    ATR_t = 10
    def init(self):
            self.ma = self.I(talib.SMA,self.data.Close, timeperiod = self.ma)
            self.bbup,self.bbmiddle,self.bblow = self.I(talib.BBANDS, self.data.Close, timeperiod = self.BB_t)
            self.bbp = (self.data.Close - self.bblow)/ (self.bbup- self.bblow)
            self.bbp_moving = self.I(talib.SMA, self.bbp, 3)
            self.atr= self.I (talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod = self.ATR_t)
    def next(self):
        price = self.data["Close"][-1]
        try:
            if not self.position:
                if (self.bbp_moving < 0.25) and (self.data.Close > self.ma): 
                    long_tp = price + 3*self.atr
                    long_sl = price - 1*self.atr
                    self.buy(sl = long_sl,tp = long_tp)
                    
                elif (self.bbp_moving >0.75) and (self.data.Close < self.ma) :
                    short_tp = price -3*self.atr
                    short_sl = price + 1*self.atr
                    self.sell(sl = short_sl, tp = short_tp)
            #elif self.position:
            #    if (self.bbp  > 0.75):
            #        self.position.close()
            #    elif (self.bbp < 0.25):
            #        self.position.close()
        except:
            pass