
#This code will provide long term (6/12 month) stock return prediction for all the stocks with quality score

#Loading Libraries
install.packages("aod")
install.packages("zoo")
install.packages("forecast")
install.packages("tseries")
install.packages("vars")
install.packages("dplyr")
library(forecast)
library(tseries)
library(vars)
library(aod)
library(zoo)
library(dplyr)

#Reading Data

#For every ticker with a quality score, fetch year, quarter, long term debt, eps, market value, price and income
cusip_ticker_mapping <- read.csv("cusip_ticker_mapping.csv", header=T)
fundamentals <- read.csv("funda_1000_edited.csv", header=T)
fundamentals=fundamentals[,c("TICKER",  "fyearq", "fqtr", "dlttq", "epsfxq", "mkvaltq", "piq", "prccq")]
funda.v1 <- inner_join(fundamentals, cusip_ticker_mapping,by=c("TICKER"="Ticker"))
data<-distinct(funda.v1)
names(data) <- c("Ticker", "Year","Quarter","LTDebt","EPS","MktValue","Income","Price")

#data consists of tickers and corresponding quarterly Long Term Debt (LTDebt), Market Value (MktValue), Income and Price 

listOfTickers=unique(as.vector(data[["Ticker"]]))

#Handling Missing values
data["LTDebt"]=na.locf(data["LTDebt"], fromLast = TRUE)
data["EPS"]=na.locf(data["EPS"], fromLast = TRUE)
data["MktValue"]=na.locf(data["MktValue"], fromLast = TRUE)
data["Income"]=na.locf(data["Income"], fromLast = TRUE)
data["Price"]=na.locf(data["Price"], fromLast = TRUE)

#Creating dataframe for final results
colname=c("Ticker","MAPE_6month","Return_6month","MAPE_12month","Return_12month")
df <- data.frame(matrix(ncol = 5))
colnames(df)=colname
levelsOfTicker=listOfTickers

#Run the code for all the tickers
for (nameTicker in levelsOfTicker){
if (nameTicker!="PAYX"){  

#Filter relevant data for the ticker
filteredData=data[data["Ticker"]==nameTicker,]
years=data[,"Year"] 

#Coverting the training data columns into time series: Start indicates the year and freq=4 indicates that the data is quarterly
ts_ltdebt=ts(filteredData[,"LTDebt"],start=2005, freq=4)
ts_mktvalue=ts(filteredData[,"MktValue"],start=2005, freq=4)
ts_income=ts(filteredData[,"Income"],start=2005, freq=4)
ts_price=ts(filteredData[,"Price"],start=2005, freq=4)

############################################################### 1 Year Return Prediction ###############################################
#########################################################################################################################################

# Preparing Data

n = nrow(filteredData)

#Dividing the data into training set and testting/validation set
data.train=filteredData[1:(n-4),c("Price","LTDebt","MktValue","Income")]
data.test=filteredData[(n-3):n,c("Price","LTDebt","MktValue","Income")]

#Coverting the training data columns into time series: Start indicates the year and freq=4 indicates that the data is quarterly
ts_train_price=ts(data.train[,"Price"],start=2005, freq=4)
ts_train_ltdebt=ts(data.train[,"LTDebt"],start=2005, freq=4)
ts_train_mktvalue=ts(data.train[,"MktValue"],start=2005, freq=4)
ts_train_income=ts(data.train[,"Income"],start=2005, freq=4)

#Differencing the time series to make it stationary
diff_train_price= diff(ts_train_price)
diff_train_ltdebt= diff(ts_train_ltdebt)
diff_train_mktvalue= diff(ts_train_mktvalue)
diff_train_income= diff(ts_train_income)

#Combine all the data in one dataframe
train_data=cbind(diff_train_price,diff_train_ltdebt,diff_train_mktvalue,diff_train_income)

###################################################################### Modeling #########################################################

###################################################################### ARIMAX model######################################################
#ARIMAX model to predict stock price/returns after 4 quarters. Exogeneous variables (variable that help in predicting stock price/return) included are Long Term Debt, Market Value and Income


#Find the right order for the model  
final.aic = Inf
final.order = c(0,0,0,0)
for (p in 1:6) for (d in 0:1) for (q in 1:6){
  current.aic = AIC(arima(diff_train_price, order=c(p, d, q), method="ML",xreg=data.frame(diff_train_ltdebt,diff_train_mktvalue,diff_train_income)))
  if (current.aic < final.aic) {
    final.aic = current.aic
    final.order = c(p, d, q)
    
  }
}

# > final.order gives the final order of the model

# Build ARIMAX with the best order obtained above
model.arima2 = arima(diff_train_price, order = c(final.order[1],final.order[2],final.order[3]), method="ML",xreg=data.frame(diff_train_ltdebt,diff_train_mktvalue,diff_train_income))


#Prepare testing/validation data such that it is consistent in format with the data on which model was trained
data2=diff(ts(data.test[,2],start=2017, freq=4))
data3=diff(ts(data.test[,3],start=2017, freq=4))
data4=diff(ts(data.test[,4],start=2017, freq=4))


#Forecasting price/returns after 4 quarters
fore = forecast(model.arima2,h=4,xreg=data.frame(data2,data3,data4))
fore=data.frame(fore)
fore=diffinv(fore[,1],xi=as.numeric(data.test[,1][1]))

#Accuracy Measure

#Mean Absolute Percentage Error (MAPE)
mape_12month=mean(abs(fore - data.test[,1])/data.test[,1])
return_12month=(fore[4]-tail(data.train[,1],1))/tail(data.train[,1],1)

############################################################## 6 Month Return Prediction ###############################################
#######################################################################################################################################
# Preparing Data

n = nrow(filteredData)
data.train=filteredData[1:(n-2),c("Price","LTDebt","MktValue","Income")]
data.test=filteredData[(n-1):n,c("Price","LTDebt","MktValue","Income")]

ts_train_price=ts(data.train[,"Price"],start=2005, freq=4)
ts_train_ltdebt=ts(data.train[,"LTDebt"],start=2005, freq=4)
ts_train_mktvalue=ts(data.train[,"MktValue"],start=2005, freq=4)
ts_train_income=ts(data.train[,"Income"],start=2005, freq=4)

diff_train_price= diff(ts_train_price)
diff_train_ltdebt= diff(ts_train_ltdebt)
diff_train_mktvalue= diff(ts_train_mktvalue)
diff_train_income= diff(ts_train_income)

train_data=cbind(diff_train_price,diff_train_ltdebt,diff_train_mktvalue,diff_train_income)

###################################################################### Modeling #########################################################

###################################################################### ARIMAX model######################################################
#ARIMAX model to predict stock price/returns after 2 quarters. Exogeneous variables (variable that help in predicting stock price/return) included are Long Term Debt, Market Value and Income
  
final.aic = Inf
final.order = c(0,0,0,0)
for (p in 1:6) for (d in 0:1) for (q in 1:6){
  current.aic = AIC(arima(diff_train_price, order=c(p, d, q), method="ML",xreg=data.frame(diff_train_ltdebt,diff_train_mktvalue,diff_train_income)))
  if (current.aic < final.aic) {
    final.aic = current.aic
    final.order = c(p, d, q)
    
  }
}
  
# > final.order gives the final order of the model

# Build ARIMAX with the best order obtained above
model.arima2 = arima(diff_train_price, order = c(final.order[1],final.order[2],final.order[3]), method="ML",xreg=data.frame(diff_train_ltdebt,diff_train_mktvalue,diff_train_income))
  
#Prepare testing/validation data such that it is consistent in format with the data on which model was trained
data2=diff(ts(data.test[,2],start=2017, freq=4))
data3=diff(ts(data.test[,3],start=2017, freq=4))
data4=diff(ts(data.test[,4],start=2017, freq=4))
  

#Forecasting price/returns after 2 quarters
fore = forecast(model.arima2,h=2,xreg=data.frame(data2,data3,data4))
fore=data.frame(fore)
fore=diffinv(fore[,1],xi=as.numeric(data.test[,1][1]))

#Accuracy Measures

### Mean Absolute Percentage Error (MAPE)
mape_6month=mean(abs(fore - data.test[,1])/data.test[,1])
return_6month=(fore[2]-tail(data.train[,1],1))/tail(data.train[,1],1)

acc_measures=c(nameTicker,mape_6month,return_6month,mape_12month,return_12month)
result.data.frame=as.data.frame(t(acc_measures))
colnames(result.data.frame)=colname

#Combine all the accuracy measures and corresponding returns in the dataframe - df
df=rbind(df,result.data.frame)
}
}
# Remove NAs from the dataframe
df=df[complete.cases(df),]
rownames(df) <- 1:nrow(df)
#Write the result into a new csv file - result.csv
write.csv(df,file="result.csv")
