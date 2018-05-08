import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

'''
Function to simulate the performance of the portfolio of stocks generated
through our prediction and optimization methods using historical price data,
and compare performance to a benchmark index
Inputs: Takes Dataframe of historical prices, list of stocks and weights
recommended for investment, start date and end date for investment time
horizon, and title for plot of performance
Outputs: Plot of performance and returns statistics on portfolio and benchmark
(Cumulative return, Average daily return, risk, sharpe ratio)
'''

def market_sim(pricefile, optimal_port, sd, ed, plot_title = 'Backtest'):
    
    #Get list of stocks
    stocks = list(zip(*optimal_port)[0])

    #Get price data
    df_prices = pd.read_csv(pricefile, parse_dates=['Date'])
    df_prices = df_prices.set_index('Date')
    df_prices = df_prices[stocks].loc[sd:ed]

    #Get shares held in each stock
    shares = list(zip(*optimal_port)[2])

    #Dataframe of value of portfolio at each time
    df_holdings = df_prices*shares
    df_holdings['Portfolio'] = df_holdings.sum(1)


    #Calculate portfolio daily returns
    port_returns = df_holdings[['Portfolio']].copy()
    port_returns[1:] = df_holdings[1:][['Portfolio']] / df_holdings[:-1][['Portfolio']].values - 1
    port_returns.ix[0] = 0.0

    #Compute statistics on portfolio performance

    #Cumulative return
    cr = (df_holdings.ix[-1][['Portfolio']] / df_holdings.ix[0][['Portfolio']]) - 1

    #Average Daily return
    adr = port_returns[1:].mean()

    #Standard deviation of daily returns
    sddr = port_returns[1:].std()

    #Total risk
    risk = port_returns[1:].std() * (df_holdings.shape[0])**0.5

    #Sharpe ratio
    sr = ((df_holdings.shape[0])**0.5)*(adr/sddr)

    #Normalize portfolio values
    df_holdings['Portfolio'] = df_holdings['Portfolio']/df_holdings['Portfolio'].iloc[0]

    #Get SPY values
    df_spy = pd.read_csv('./data/backtest/SPY.csv', parse_dates=['Date'])
    df_spy = df_spy.rename(columns={'Adj Close': 'SPY'})
    df_spy = df_spy.set_index('Date')
    df_spy = df_spy.loc[sd:ed]

    #Compute statistics for SPY for comparison
    spy_returns = df_spy.copy()
    spy_returns[1:] = df_spy[1:] / df_spy[:-1].values - 1
    spy_returns.ix[0] = 0.0

    cr_bench = df_spy.ix[-1] / df_spy.ix[0] - 1
    adr_bench = spy_returns[1:].mean()
    sddr_bench = spy_returns[1:].std()
    risk_bench = spy_returns[1:].std() * (df_spy.shape[0])**0.5
    sr_bench = ((df_spy.shape[0])**0.5)*(adr_bench/sddr_bench)
    
    #Normalize SPY
    df_spy['SPY'] = df_spy['SPY']/df_spy['SPY'].iloc[0]
    

    #Plot portfolio value (normalized) as well as SPY
    df_compare = pd.concat([df_holdings, df_spy], axis=1)
    df_compare = df_compare.fillna(method='ffill')
    df_compare[['Portfolio', 'SPY']].plot()
    myFmt = DateFormatter("%d/%m/%y")
    plt.xlabel('Date')
    plt.ylabel('Normalized Value')
    plt.xticks(rotation=30)
    plt.title(plot_title)
    plt.show()


    #Organize stats for output
    portfolio_stats = {'cr': float(cr), 'adr': float(adr),
                       'risk': float(risk), 'sr': float(sr)}

    bench_stats = {'cr': float(cr_bench), 'adr': float(adr_bench),
                   'risk': float(risk_bench), 'sr': float(sr_bench)}


    return portfolio_stats, bench_stats


#Function to print out portfolio and benchmark stats
def display_stats(port_stats, bench_stats, ret, title):
    print title
    print
    print 'Portfolio Stats:'
    print 'Target Return: {}'.format(ret)
    print 'Cumulative Return: {}'.format(port_stats['cr'])
    print 'Average Daily Return: {}'.format(port_stats['adr'])
    print 'Risk (Standard Deviation): {}'.format(port_stats['risk'])
    print 'Sharpe Ratio: {}'.format(port_stats['sr'])
    print
    print 'Benchmark (SPY) Stats:'
    print 'Cumulative Return: {}'.format(bench_stats['cr'])
    print 'Average Daily Return: {}'.format(bench_stats['adr'])
    print 'Risk (Standard Deviation): {}'.format(bench_stats['risk'])
    print 'Sharpe Ratio: {}'.format(bench_stats['sr'])
    
        
    
