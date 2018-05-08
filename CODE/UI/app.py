from flask import Flask, render_template, request, redirect, url_for, session
from optimization import *
from portfoliosim import *
import datetime as dt

'''
Script controlling backend for UI - loads user preferences entered, runs
optimization to calculate optimal portfolio, and organizes data to use
for visualizations
'''

app = Flask(__name__)
app.secret_key = 'key'

@app.route("/", methods=['POST', 'GET'])
def start():
    error = None
    if request.method == 'POST':
        try:
            #Load preferences from user input
            session['capital'] = float(request.form['capital'])
            session['return'] = float(request.form['return'])
            session['time'] = float(request.form['time'])

            #Raise errors if investment amount or return are not positive
            if session['capital'] <= 0:
                error = 'Error: Investment amount must be positive'
            elif session['return'] <= 0:
                error = 'Error: Return must be positive'
            else:
                return redirect(url_for("portfolio"))

        #Raise error if non-numerical value entered
        except:
            error = 'Error: Non-numerical value entered'
        
    return render_template('start.html', error=error)


@app.route("/portfolio", methods=['POST', 'GET'])
def portfolio():

    #Collect and organize preferences information
    capital = session['capital']
    ret = 0.01*session['return']
    time = session['time']
    time_map = {5.0: "1 Week", 126.0: "6 Months", 252.0: "1 Year"}
    preferences = {'capital': capital, 'return': 100*ret, 'time': time_map[time]}

    #"Current" date
    date = '2018-03-27'

    
    if time == 5.0:
        predictfile = './data/predictions/short_term.csv'
        pricefile = './data/prices_short.csv'
    else:
        predictfile = './data/predictions/long_term.csv'
        pricefile = './data/prices_long.csv'


    #Run optimization, return list of stocks, weights, shares, price
    #Also returns portfolio return and risk
    stocks, port_ret, daily_risk = optimize(pricefile, predictfile, ret, capital, date, time)

    #Get risk for time period
    port_risk = round(np.sqrt(time)*daily_risk, 3)

    #Calculate sharpe ratio
    sr = round(port_ret/port_risk, 3)

    #Organize portfolio stats information
    portstats = {'return': 100*port_ret, 'risk': 100*port_risk, 'sr': sr}


    #Get dates for plotting performance
    d = dt.datetime.strptime(date, "%Y-%m-%d")
    dates = [date]
    if time == 5.0:
        delta = dt.timedelta(days = 1)
        d0 = d
        while len(dates) < 6:
            nextdate = d0 + delta
            if bool(len(pd.bdate_range(nextdate, nextdate))):
                dates.append((nextdate).strftime("%Y-%m-%d"))
            d0 = nextdate            
    elif time == 126.0:
        delta = dt.timedelta(days = 182)
        dates.append((d + delta).strftime("%Y-%m-%d"))
    else:
        delta1 = dt.timedelta(days = 182)
        delta2 = dt.timedelta(days = 364)
        dates.append((d + delta1).strftime("%Y-%m-%d"))
        dates.append((d + delta2).strftime("%Y-%m-%d"))

    

    #Run market simulator to calculate time series of portfolio value (past and projected)
    portvals = portfolio_sim(predictfile, stocks, capital, dates, time)


    #Pie chart data
    piecolors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
                 '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe',
                 '#008080', '#e6beff', '#aa6e28', '#fffac8', '#800000',
                 '#aaffc3', '#808000', '#ffd8b1', '#000080', '#808080',
                 '#000000']
    piedata = []
    for stock in stocks:
        piedata.append({"label": stock[0], "value": stock[1]})

    #Data for output to page
    data = { "preferences": preferences, "piedata": piedata,
             "piecolors": piecolors, "stockdata": stocks,
             "portvals": portvals, "portstats": portstats }
    
    return render_template('portfolio.html', data=data)

if __name__ == "__main__":
    app.run()
