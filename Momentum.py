# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 18:54:38 2020

@author: 15106

"""

import bt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

########### Getting S&P data ###########
beginning = '2016-01-04'
data_spgsg = bt.get('^GSPC', start=beginning)


s_spgsg = bt.Strategy('S&P gsg only', 
                       [bt.algos.RunMonthly(),
                       bt.algos.SelectAll(),
                       bt.algos.WeighEqually(),
                       bt.algos.Rebalance()])
                    
b_spgsg = bt.Backtest(s_spgsg, data_spgsg)
result = bt.run(b_spgsg)
result.plot()

########### Getting Risk Free Rate ###########
riskfree =  bt.get('^IRX', start=beginning)
riskfree_rate = float(riskfree.mean()) / 100
print(riskfree_rate)



########### Selecting Algos ###########


### Random 5 strategies ###
equity_list = ['vaw', 'vis', 'vcr', 'vdc','vht', 'vfh', 'vgt', 'vox', 'vpu', 'vnq', 'vde']
data = bt.get(equity_list, start=beginning)
data.head()

s_random = bt.Strategy('Random 5', 
                       [bt.algos.RunMonthly(),
                       bt.algos.SelectRandomly(5),
                       bt.algos.WeighEqually(),
                       bt.algos.Rebalance()])

b_random = bt.Backtest(s_random, data)

result = bt.run(b_random, b_spgsg)

result.set_riskfree_rate(riskfree_rate)
result.plot()
result.display()

#### best 5 securities with a lookback period of 3 months
s_best = bt.Strategy('Best 5', 
                       [bt.algos.RunMonthly(),
                       bt.algos.SelectAll(),
                       bt.algos.SelectMomentum(5, lookback=pd.DateOffset(months=3)),
                       bt.algos.WeighEqually(),
                       bt.algos.Rebalance()])

b_best = bt.Backtest(s_best, data)

result = bt.run(b_random, b_best, b_spgsg)

result.set_riskfree_rate(riskfree_rate)
result.plot()
result.display()

# comparing the statostics for the 3 strategies 
df_results_key = result.stats.assign()


#### using weights strategies #####

### Inverse of Volatility | bt.algos.WeighInvVol()
s_inv = bt.Strategy('Inverse of Volatility', 
                       [bt.algos.RunMonthly(),
                       bt.algos.SelectAll(),
                       bt.algos.WeighInvVol(),
                       bt.algos.Rebalance()])

b_inv = bt.Backtest(s_inv, data)
result = bt.run(b_inv, b_random, b_best, b_spgsg)
result.set_riskfree_rate(riskfree_rate)
result.plot()
result.display()

df_results_key_2 = result.stats.assign()

### Using Markowitz
##s_mark = bt.Strategy('Markowitz', 
                       #[bt.algos.RunEveryNPeriods(10, 3),
                       #bt.algos.SelectAll(),
                       #bt.algos.WeighMeanVar(),
                       #bt.algos.Rebalance()])

##b_mark = bt.Backtest(s_mark, data)

result = bt.run(b_mark, b_inv, b_random, b_best, b_spgsg)
result.set_riskfree_rate(riskfree_rate)
result.plot()
plt.title(label = "SMA_50_200 vs SMA_32_248 | Equity Progression", fontsize=20)








