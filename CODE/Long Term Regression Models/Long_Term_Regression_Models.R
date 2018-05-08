
setwd("C:/Users/somri/Desktop/MS Analytics/Spring/CSE 6242/Project")


####################Loading Required Libraries##############################
library(glmnet)
library(car)
library(lubridate)
library(dplyr)


#######################Data Processing#####################################
###Steps performed:
###1. For each cusip (unique identifier for each stock) quarterly fundamental variables (EPS, Market Values, Income)
###   are collated with variables created for quality scoring (GPOA, ROE, ROA, CFOA, GMAR, Acc, Ivol, Bab, Lev)
###2. Price at the start of each quarter is also taken as a field.
###3. Dependent variable is created as price for the same cusip for 2 quarters (6 months) down the line 
###   and 4 quarters (12 months) down the line.

## Files required
quality_score <- read.csv("dsf_funda_quality_score_clean.csv", header=T)
cusip_ticker_mapping <- read.csv("cusip_ticker_mapping.csv", header=T)
fundamentals <- read.csv("funda_1000_edited.csv", header=T)

fundamentals=fundamentals[,c("TICKER",  "fyearq", "fqtr", "dlttq", "epsfxq", "mkvaltq", "piq", "prccq")]
#data_funda <- inner_join(fundamentals, cusip_ticker_mapping,by=c("TICKER"="Ticker"))
funda<-distinct(fundamentals)
colnames_funda <- c("Ticker", "Year","Qtr","LTDebt","EPS","MktValue","Income","Price")
colnames(funda) <- colnames_funda


data <- quality_score
data["Year"] <- year(quality_score$date)
data["Qtr"] <- quarter(quality_score$date)
data["concat"] <- paste(data$cusip,as.character(data$Year),as.character(data$Qtr))
data <- data[,c("concat", "Year", "Qtr", "cusip","gpoa", "roe", "roa", "cfoa", "gmar", "acc", "gpoa_delta_5", "roe_delta_5", "roa_delta_5",
                "cfoa_delta_5","gmar_delta_5", "acc_delta_5","bab", "ivol", "lev", "evol", "eiss", "diss", "npop")]

funda.v1 <- inner_join(funda, cusip_ticker_mapping, by = "Ticker")
funda.v2 <- funda.v1
funda.v2["concat"] <- paste(funda.v1$cusip,as.character(funda.v1$Year),as.character(funda.v1$Qtr))

data_comb <- merge(data,funda.v2, by=c("cusip","Year","Qtr"))
data_comb <- data_comb[,-c(24,30)]

data_comb_y = data_comb
data_comb_y["Year.y6"] <- ifelse(data_comb$Qtr %in% c(3,4), data_comb$Year + 1, data_comb$Year)
data_comb_y["Qtr.y6"] <- ifelse(data_comb$Qtr %in% c(3,4), data_comb$Qtr - 2, data_comb$Qtr + 2)
data_comb_y["Year.y12"] <- data_comb$Year + 1
data_comb_y["Qtr.y12"] <- data_comb$Qtr

data_comb_y <- data_comb_y[-c(2,3)]

####################6 months price prediction###############################

## Dependent variable created
data_comb_y.6m <- merge(data_comb, data_comb_y, by.x = c("cusip", "Year", "Qtr"), by.y = c("cusip", "Year.y6", "Qtr.y6"))
data_comb_y.6m <- data_comb_y.6m[-c(29:52,54:55)]
col_old <- colnames(data_comb_y.6m)
col_new <- gsub(pattern = ".x", replacement = "", x=col_old)
colnames(data_comb_y.6m) <- col_new


## Creating data 2012 onwards as train and 2011 as test
data_6m.train <- data_comb_y.6m[data_comb_y.6m$Year>2012,1:29]
data_6m.test <- data_comb_y.6m[data_comb_y.6m$Year<=2012,1:29]

## Creating predictors (X matrix) and response (y vector)
predictors_6m.train <- data_6m.train[,5:28]
response_6m.train <- data_6m.train[,29]

## Cross Validation to determine optimum lambda for LASSO
## Scaled X Matrix and Scaled Y Vector used as inputs to CV
## MSE used as error metric
cv.out <- cv.glmnet(as.matrix(scale(predictors_6m.train)), as.vector(scale(response_6m.train)), alpha = 1, type.measure = "mse")

##CV Plot
plot(cv.out)

## Lambda value that minimizes error metric MSE
cv.out$lambda.min

## Lambda value 1 standard deviation away from the value that minimizes MSE
cv.out$lambda.1se


##LASSO performed with lambda value that mnimizes MSE
model_6m.lasso=glmnet(as.matrix(predictors_6m.train), as.vector(scale(response_6m.train)), alpha=1, lambda=0.1, family = "mgaussian")

## Betas selected by LASSO
model_6m.lasso$beta

## Linear Regression Model Built
model_6m <- lm(Price.y~
                 #EPS+
                 Price+
                 #roa+
                 gmar+
                 roa_delta_5
               #gmar_delta_5
               , data = data_6m.train)

## Checking VIF
vif(model)

## Output of Linear Regression Model
summary(model_6m)

## Predictions on training set
Price_6m.pred <- predict(model_6m, data_6m.train[,5:28])

## Training MAPE Calculations
error <- abs(data_6m.train$Price.y - Price_6m.pred)/data_6m.train$Price.y
mean(error)

## Exporting train data with predictions
data_6m.train.pred <- cbind(data_6m.train,Price_6m.pred)
write.csv(data_6m.train.pred,file="6m_training_prediction.csv")


## Predictions on test set
Price_6m.pred <- predict(model_6m, data_6m.test[,5:28])

## Test MAPE Calculations
error <- abs(data_6m.test$Price.y - Price_6m.pred)/data_6m.test$Price.y
mean(error)

## Exporting test data with predictions
data_6m.test.pred <- cbind(data_6m.test,Price_6m.pred)
write.csv(data_6m.test.pred,file="6m_prediction.csv")



## COmbining all predictions and exporting
data_6m_pred <- rbind(data_6m.train.pred[,c("cusip","Price_6m.pred", "Price","Year","Qtr")],
                      data_6m.test.pred[,c("cusip","Price_6m.pred", "Price","Year","Qtr")])

data_6m_pred["Year.y12"] <- ifelse(data_6m_pred$Qtr %in% c(3,4), data_6m_pred$Year + 1, data_6m_pred$Year)
data_6m_pred["Qtr.y12"] <- ifelse(data_6m_pred$Qtr %in% c(3,4), data_6m_pred$Qtr - 2, data_6m_pred$Qtr + 2)


data_6m_pred <- data_6m_pred[,c("cusip","Price_6m.pred","Year.y12","Qtr.y12","Price","Year","Qtr")]
write.csv(data_6m_pred,file="6m_all_prediction.csv")

#####################12mahead#################

## Dependent Variable Created
data_comb_y.12m <- merge(data_comb, data_comb_y, by.x = c("cusip", "Year", "Qtr"), by.y = c("cusip", "Year.y12", "Qtr.y12"))
data_comb_y.12m <- data_comb_y.12m[-c(29:52,54:55)]
col_old <- colnames(data_comb_y.12m)
col_new <- gsub(pattern = ".x", replacement = "", x=col_old)
colnames(data_comb_y.12m) <- col_new


## Creating data 2012 onwards as train and 2011 as test
data_12m.train <- data_comb_y.12m[data_comb_y.12m$Year>2012,1:29]
data_12m.test <- data_comb_y.12m[data_comb_y.12m$Year<=2012,1:29]

## Creating predictors (X matrix) and response (y vector)
predictors_12m.train <- data_12m.train[,5:28]
response_12m.train <- data_12m.train[,29]


## Cross Validation to determine optimum lambda for LASSO
## Scaled X Matrix and Scaled Y Vector used as inputs to CV
## MSE used as error metric
cv.out <- cv.glmnet(as.matrix(scale(predictors_12m.train)), as.vector(scale(response_12m.train)), alpha = 1, type.measure = "mse")

#CV Plot
plot(cv.out)

## Lambda value that minimizes error metric MSE
cv.out$lambda.min

## Lambda value 1 standard deviation away from the value that minimizes MSE
cv.out$lambda.1se

##LASSO performed with lambda value that mnimizes MSE
model.lasso=glmnet(as.matrix(scale(predictors_12m.train)), as.vector(scale(response_12m.train)), alpha=1, lambda=cv.out$lambda.min, family = "mgaussian")

## Betas selected by LASSO
model.lasso$beta

## Linear Regression Model Built
model <- lm(Price.y~
              EPS+
              Price+
              acc
            #gmar
            #roa_delta_5
            #acc_delta_5
            #+
            #npop+
            #z_roe+
            #z_gmar
            #+
            #payout
            #z_safety
            ,data = data_12m.train)

## Checking VIF
vif(model)

## Output of Linear Regression Model
summary(model)


## Predictions on training set
Price_12m.pred <- predict(model, data_12m.train[,5:28])

## Training MAPE Calculations
error <- abs(data_12m.train$Price.y - Price_12m.pred)/data_12m.train$Price.y
mean(error)

## Exporting train data with predictions
data_12m.train.pred <- cbind(data_12m.train,Price_12m.pred)
write.csv(data_12m.train.pred,file="12m_training_prediction.csv")



## Predictions on test set
Price_12m.pred <- predict(model, data_12m.test[,5:28])


## MAPE Calculations
error <- abs(data_12m.test$Price.y - Price_12m.pred)/data_12m.test$Price.y
mean(error)


## Exporting test data with predictions
data_12m.test.pred <- cbind(data_12m.test,Price_12m.pred)
write.csv(data_12m.test.pred,file="12m_prediction.csv")



## COmbining all predictions and exporting
data_12m_pred <- rbind(data_12m.train.pred[,c("cusip","Price_12m.pred", "Price","Year","Qtr")],
                       data_12m.test.pred[,c("cusip","Price_12m.pred", "Price","Year","Qtr")])

data_12m_pred["Year.y12"] <- data_12m_pred$Year + 1
data_12m_pred["Qtr.y12"] <- data_12m_pred$Qtr


data_12m_pred <- data_12m_pred[,c("cusip","Price_12m.pred","Year.y12","Qtr.y12","Price","Year","Qtr")]
write.csv(data_12m_pred,file="12m_all_prediction.csv")