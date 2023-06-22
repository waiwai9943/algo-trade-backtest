import talib as ti

def MACD_12_26_9(df,x,y,z):
        return ti.MACD(df['Close'], fastperiod=x, slowperiod=y, signalperiod=z)


x,y,z= MACD_12_26_9(12,26,9)

print (x,y,z)