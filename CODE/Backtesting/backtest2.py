from optimization import *
from marketsim import *

#Backtesting 1-week predictions model
capital = 1000000.0
ret = 0.005
time = 5.0
date = '2018-03-27'
pricefile = './data/prices_short.csv'
predictfile = './data/predictions/short_term.csv'
title = 'Backtest of Portfolio made using 1-Week Projections'

optimal_port, port_ret, port_risk = optimize(pricefile, predictfile, ret, capital, date, time)


port_stats, bench_stats = market_sim('./data/prices_new.csv', optimal_port,
                                     sd='2018-03-27', ed='2018-04-04', plot_title=title)

display_stats(port_stats, bench_stats, ret, title)
