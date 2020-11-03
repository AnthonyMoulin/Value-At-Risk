# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 00:59:43 2019

@author: MichaelRolleigh
"""
# This script enacts the crossover strategy in bt

import bt
# download data
#data = bt.get('vaw, vis, vcr, vdc, vht, vfh, vgt, vox, vpu, vnq, vde', start='2010-01-01')
data = bt.get('gsg', start='2010-01-01')
# calculate moving average DataFrame using pandas' rolling_mean
import pandas as pd
import matplotlib.pyplot as plt

# define the length of the short and long averages
short_s1 = 50
long_s1 = 200
short_s2 = 32
long_s2 = 248

# a rolling mean is a moving average, right?
sma_short_s1 = data.rolling(short_s1).mean()
sma_long_s1 = data.rolling(long_s1).mean()

sma_short_s2 = data.rolling(short_s2).mean()
sma_long_s2 = data.rolling(long_s2).mean()
# and compute sma_50 for replicating earlier strat
sma_50 = data.rolling(50).mean()
sma_200 = data.rolling(200).mean()
sma_32 = data.rolling(32).mean()
sma_248 = data.rolling(248).mean()


# let's see what the data looks like - this is by no means a pretty chart, but it does the job
#plot = bt.merge(data, sma_short_s1, sma_long_s1, sma_short_s2, sma_long_s2).plot(figsize=(15, 5))

# We need to set up our target weights. This will be the same size as sma_long
# weight = 1 means go long; weight = -1 means short

target_weights_s1 = sma_long_s1.copy()
target_weights_s2 = sma_long_s2.copy()


# set appropriate target weights 
target_weights_s1[sma_short_s1 > sma_long_s1] =  1 # you long, so positive 
target_weights_s1[sma_short_s1 <= sma_long_s1] = -1 # you short, so negative

target_weights_s2[sma_short_s2 > sma_long_s2] =  1 # you long, so positive 
target_weights_s2[sma_short_s2 <= sma_long_s2] = -1 # you short, so negative


# here we will set the weight to 0 - this is because the sma_long needs long data points before
# calculating its first point. Therefore, it will start with a bunch of nulls (NaNs).
# This fills up the Not a Numbers (NaNs) with 0.0 instead
# If we left the NaNs, we would get an error when we tried to do math without a number
target_weights_s1[sma_short_s1.isnull()] = 0.0
target_weights_s2[sma_short_s2.isnull()] = 0.0


# Now set up the MA_cross strategy for our moving average cross strategy
MA_cross = bt.Strategy('MA_cross', [bt.algos.WeighTarget(target_weights_s1),
                                    bt.algos.Rebalance()])

test_MA = bt.Backtest(MA_cross, data)
res_MA = bt.run(test_MA)

# plot security weights to test logic

res_MA.plot_security_weights()
plt.title(label = "SMA from 50 to 200", fontsize=25)


# signal = data > sma_32

MA_cross_2 = bt.Strategy('MA_cross_2', [bt.algos.WeighTarget(target_weights_s2),
                                    bt.algos.Rebalance()])

test_MA_2 = bt.Backtest(MA_cross_2, data)
res_MA_2 = bt.run(test_MA_2)

res2 = bt.run(test_MA, test_MA_2)

res2.display()
res2.plot()
plt.title(label = "SMA_50_200 vs SMA_32_248 | Equity Progression", fontsize=20)


# plot security weights to test logic
res_MA_2.plot_security_weights(color ="blue")
plt.title(label = "SMA from 32 to 248", fontsize=25)
params = {'legend.fontsize' :20}

####### exporting table with results

## Transforming backtest type objects generated from bt into tables

df_results_key_sma = res2.stats.assign()
df_results_key_sma.to_excel("table_sma.xlsx")

"""
###########################################################################
def above_sma(ticker, sma_per=50, start='2016-01-01', name='above_sma'):
    
    Long securities that are above their n period
    Simple Moving Averages with equal weights.

    # download data
    data = bt.get(ticker, start=start)
    # calc sma
    sma = data.rolling(sma_per).mean()

    # create strategy
    s = bt.Strategy(name, [bt.algos.SelectWhere(data > sma),
                           bt.algos.WeighEqually(),
                           bt.algos.Rebalance()])

    # now we create the backtest
    return bt.Backtest(s, data)

# simple backtest to test long-only allocation
def long_only_ew(ticker, start='2016-01-01', name='long_only_ew'):
    s = bt.Strategy(name, [bt.algos.RunOnce(),
                           bt.algos.SelectAll(),
                           bt.algos.WeighEqually(),
                           bt.algos.Rebalance()])
    data = bt.get(ticker, start=start)
    return bt.Backtest(s, data)

# create the backtests
ticker = '^GSPC'
sma10 = above_sma(ticker, sma_per=10, name='sma10')
sma20 = above_sma(ticker, sma_per=20, name='sma20')
sma32 = above_sma(ticker, sma_per=32, name='sma32')
sma40 = above_sma(ticker, sma_per=40, name='sma40')
sma50 = above_sma(ticker, sma_per=50, name='sma50')
benchmark = long_only_ew('^GSPC', name='^GSPC')

# run all the backtests!
res2 = bt.run(sma10, sma20, sma32, sma40, sma50, benchmark)

# Plot the equity positions of hte strats
res2.plot(freq='m')

# Display the stats for the 4 strats 
res2.display()



# commenting out the plots below because they are on later plots
#res_MA.plot()

#res_MA.display()
"""

"""
# define a signal to feed to the SelectWhere class to select securities to trade
# The signal is simple, data>sma_50 because data is price and sma_50 is moving average
signal = data > sma_32
bt.algos.SelectWhere(signal, include_no_data=False)

# first we create the Strategy
s = bt.Strategy('above32sma', [bt.algos.SelectWhere(signal),
                               bt.algos.WeighEqually(),
                               bt.algos.Rebalance()])

# now we create the Backtest
t = bt.Backtest(s, data)

# and let's run it!
res = bt.run(t, test_MA)

# what does the equity curve look like?
#res.plot()

# and some performance stats
res.display()

# Now create a function that will allow us to generate related backtests more quickly
# This step is not required, but it is good programming practice
def above_sma(tickers, sma_per=50, start='2010-01-01', name='above_sma'):
 
    # download data
    data = bt.get(tickers, start=start)
    # calc sma
    sma = data.rolling(sma_per).mean()

    # create strategy
    s = bt.Strategy(name, [bt.algos.SelectWhere(data > sma),
                           bt.algos.WeighEqually(),
                           bt.algos.Rebalance()])

    # now we create the backtest
    return bt.Backtest(s, data)

# simple backtest to test long-only allocation
def long_only_ew(tickers, start='2010-01-01', name='long_only_ew'):
    s = bt.Strategy(name, [bt.algos.RunOnce(),
                           bt.algos.SelectAll(),
                           bt.algos.WeighEqually(),
                           bt.algos.Rebalance()])
    data = bt.get(tickers, start=start)
    return bt.Backtest(s, data)

# Below is the code that tried different SMA averages from Simple_SMA
# Note that I commented it all out at once using triple """
"""
# create the backtests
tickers = 'aapl,msft,c,gs,ge'
sma10 = above_sma(tickers, sma_per=10, name='sma10')
sma20 = above_sma(tickers, sma_per=20, name='sma20')
sma40 = above_sma(tickers, sma_per=40, name='sma40')
benchmark = long_only_ew('spy', name='spy')

# run all the backtests!
res2 = bt.run(sma10, sma20, sma40, benchmark)

# Plot the equity positions of hte strats
res2.plot(freq='m')

# Display the stats for the 4 strats 
res2.display()
"""
