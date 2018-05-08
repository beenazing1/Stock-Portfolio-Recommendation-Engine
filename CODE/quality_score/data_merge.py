# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 19:31:39 2018

@author: RaghuramPC
"""

import pandas as pd

dsf = pd.read_csv("D:\\data_visual_analytics\\project\\dsf_1000.csv",parse_dates=['date'])
funda = pd.read_csv("D:\\data_visual_analytics\\project\\funda_1000.csv",parse_dates = ['datadate'])
funda = funda.rename(columns = {'datadate':'date'})
dsf = dsf.rename(columns = {'CUSIP':'cusip'})
funda = funda.rename(columns = {'tic':'TICKER'})
#############
dsf_tickers = dsf['TICKER'].unique().tolist()
funda_tickers = funda['TICKER'].unique().tolist()
common_tickers = list(set(dsf_tickers) & set(funda_tickers))
dsf = dsf[dsf['TICKER'].isin(common_tickers)]
funda = funda[funda['TICKER'].isin(common_tickers)]
############
dsf.to_csv("dsf_1000_edited.csv")
funda.to_csv("funda_1000_edited.csv")
dsf_funda =  pd.merge(dsf,funda,how='left',on=['TICKER','date'])
dsf_funda.to_csv("dsf_funda.csv")