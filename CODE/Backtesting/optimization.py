import pandas as pd
import numpy as np
from gurobipy import *

'''
Function that runs portfolio optimization, by minimizing the total portfolio
risk subject to constraints that the weights must sum to 1, the expected
portfolio return must match the desired return, and the number of stocks with
nonzero weights is no more than 10
Outputs list of stocks with weights, shares, and prices, as well as expected
portfolio return and risk
'''

def optimize(pricefile, predictfile, ret, capital, date, time):

    #Number of stocks portfolio is limited to
    numstocks = 10
    
    #Daily stock prices
    df_prices = pd.read_csv(pricefile)
    df_prices = df_prices.set_index('Date')
    
    #Expected returns
    df_predict = pd.read_csv(predictfile)
    df_predict = df_predict.set_index('Ticker')

    #List of stock names
    stocks = df_prices.columns.values.tolist()
    
    df_prices = df_prices[stocks]

    #Calculate daily returns
    df_returns = df_prices.copy()
    df_returns[1:] = (df_prices[1:] / df_prices[:-1].values) - 1
    df_returns = df_returns[1:]   
    returns = df_returns.values
   

    #Variance-covariance matrix
    Q = np.cov(returns.transpose())

    #Return vector
    r = []
    if time == 252.0:    
        for stock in stocks:
            r.append(df_predict['Return_12month'].loc[stock])
    elif time == 126.0:
        for stock in stocks:
            r.append(df_predict['Return_6month'].loc[stock])
    else:
        for stock in stocks:
            r.append((df_predict['5'].loc[stock]/df_prices[stock].loc[date] - 1))


    #Number of stocks
    n = len(stocks)


    #Initialize model
    m = Model("portfolio")
    m.setParam('OutputFlag', 0) #Mute gurobi output

    #Initialize decision variables
    x = {} #Portfolio weights of each stock
    y = {} #Binary variables used to restrict number of stocks invested in
    for j in range(n):
        x[j] = m.addVar(lb=0.0, name="x["+stocks[j]+"]")
        y[j] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name="y["+stocks[j]+"]")
    m.update()

    #Set up objective function
    risk = 0
    for i in range(n):
        for j in range(n):
            risk = risk + x[i]*Q[i][j]*x[j]

    m.setObjective(risk, GRB.MINIMIZE)
    m.addConstr(sum([x[j] for j in range(n)]) == 1.0) #Investment constraint
    m.addConstr(sum([x[j]*r[j] for j in range(n)]) == ret) #Target return constraint

    #Constraints restricting number of stocks invested in to at most 10
    for j in range(n):
        m.addConstr(x[j] <= y[j])
    m.addConstr(sum([y[j] for j in range(n)]) <= numstocks)

    m.update()

    #Run optimization
    m.optimize()

    #Get optimization solution
    xsol = m.getAttr('x', x)

    #Calculate shares of each stock to buy and format output
    optimal_port = []
    shares = []
    prices = []
    for j in range(n):
        weight = xsol[j]
        price = df_prices[stocks[j]].loc[date] #Most recent price
        prices.append(price)
        shares.append(int(capital*weight/price))

    #Calculate true portfolio weights
    weights = []
    for j in range(n):
        weight = prices[j]*shares[j]/capital
        weights.append(weight)

    #Calculate return of minumum risk portfolio
    port_ret = 0
    for j in range(n):
        port_ret += r[j]*weights[j]  
    port_ret = round(port_ret, 3)

    #Calculate total portfolio risk
    port_var = 0
    for i in range(n):
        for j in range(n):
            port_var = port_var + weights[i]*Q[i][j]*weights[j]
    port_risk = np.sqrt(port_var)

    #Get optimal portfolio output
    for j in range(n):
        if shares[j] > 0:
            optimal_port.append((stocks[j], round(weights[j], 3), shares[j], prices[j]))

    return optimal_port, port_ret, port_risk

if __name__=="__main__":
    optimal_port, port_ret, port_risk = optimize('./data/prices_long.csv',
                                                 './data/predictions/long_term.csv',
                                                 0.15, 10000.0, '2018-03-27')
