import pandas as pd

'''
Function for simulating the projected value of the portfolio over time,
according to return projections
Returns list of dates and projected portfolio values for those dates
'''

def portfolio_sim(predictfile, optimal_port, capital, dates, time):

    #Load return predictions
    df_predict = pd.read_csv(predictfile)
    df_predict = df_predict.set_index('Ticker')

    #List storing dates and portfolio values
    portvals = [[dates[0], capital]]

    #Get projcted returns and use them to calculate new portfolio values for each date
    if time == 5.0:
        for i in range(5):
            portval = 0
            for stock in optimal_port:
                portval += stock[2]*(df_predict.loc[stock[0]].iloc[i])
            portvals.append([dates[i+1], portval])

    else:
        for i in range(1, len(dates)):
            portret = 0
            for stock in optimal_port:
                portret += stock[1] * (df_predict.loc[stock[0]].iloc[i-1])

            portval = capital*(1 + portret)
            portvals.append([dates[i], portval])

    return portvals
        
    
