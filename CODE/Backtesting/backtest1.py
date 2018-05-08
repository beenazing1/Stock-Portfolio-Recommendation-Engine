from optimization import *
from marketsim import *

#Backtesting 1-year predictions model
capital = 1000000.0
ret = 0.40
time = 252.0
date = '2017-01-03'
pricefile = './data/backtest/prices_long_back.csv'
predictfile = './data/backtest/long_term_back.csv'
title = 'Backtest of Portfolio made using 1-Year Projections'

optimal_port, port_ret, port_risk = optimize(pricefile, predictfile, ret, capital, date, time)


port_stats, bench_stats = market_sim('./data/prices_portfoliosim.csv', optimal_port,
                                     sd='2017-01-03', ed='2018-01-03', plot_title=title)


display_stats(port_stats, bench_stats, ret, title)
