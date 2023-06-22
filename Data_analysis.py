from select import select
import seaborn as sns
import pandas as pd
import matplotlib.pyplot  as plt

df = pd.read_csv('stat_raw.csv', delimiter=',')
selection1 = ['Equity Final [$]','Equity Peak [$]']
selection2 = ['Return [%]','Buy & Hold Return [%]',
            'Max. Drawdown [%]','Avg. Drawdown [%]','Win Rate [%]','Best Trade [%]','Worst Trade [%]','Avg. Trade [%]']


print (df[selection1])

sns.boxplot(x="variable", y="value", data=pd.melt(df[selection1]))
sns.boxplot(x="variable", y="value", data=pd.melt(df[selection2]))
plt.show()
