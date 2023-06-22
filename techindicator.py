
import talib as ti
import mplfinance as mpf
import matplotlib.dates as mdates
import pandas as pd

def Bollinger(df):
    df['up'], df['mid'], df['low'] = ti.BBANDS(df['Adj Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    bbp(df)
    return df 

def bbp(df):  #Bollinger Bells percentage
    df['up'], df['mid'], df['low'] = ti.BBANDS(df['Adj Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['bbp'] = (df['Adj Close'] - df['low']) / (df['up'] - df['low'])
    return df

def rsi_14(df):
    df['rsi_14'] = ti.RSI(df['Adj Close'],timeperiod=12)
    return df
    

def CCI_14(df):
    df['CCI']= ti.CCI(df['High'],df['Low'],df['Close'],timeperiod = 14)
    return df

def MACD_12_26_9(df):
    df['macd'],df['macdsignal'],df['macdhist'] = ti.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    return df

def williams(df):
    df['wr%'] = ti.WILLR (df['High'],df['Low'],df['Close'],timeperiod=14)
    return df

def KDJ(df):
    df['k'],df['d'] = ti.STOCH(df['High'],df['Low'],df['Close'],fastk_period=5, slowk_period=9 , slowk_matype=0, slowd_period=3, slowd_matype=0)
    #df['J'] = 3*df['d']-2*['k']
    return df

def OnBalanceVolume(df):
    df['OBV'] = ti.OBV(df['Close'],df['Volume'])
    return df

def SMAtest(df):
    df['10MA'] = pd.Series(df['Close']).rolling(10).mean()
    df['20MA'] = pd.Series(df['Close']).rolling(20).mean()
    df['50MA'] = pd.Series(df['Close']).rolling(50).mean()
    df['100MA'] = pd.Series(df['Close']).rolling(100).mean()
    df['135MA'] = pd.Series(df['Close']).rolling(135).mean()
    df['200MA'] = pd.Series(df['Close']).rolling(200).mean()
    return df





def SMA(value,days):
    return pd.Series(value).rolling(days).mean()


def computeallTI(df):
    SMAtest(df)
    Bollinger(df)
    bbp(df)
    rsi_14(df)
    CCI_14(df)
    MACD_12_26_9(df)
    williams(df)
    KDJ(df)
    OnBalanceVolume(df)
    return df