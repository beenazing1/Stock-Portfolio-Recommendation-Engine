import pandas as pd
import numpy as np
import datetime
import time

# function to calculate z scoreos
def z_score_calc(dsf_funda,parameter): 
    temp1 = dsf_funda.groupby("date")[parameter].mean()
    temp1 = temp1.to_frame()
    temp1["date"] = temp1.index
    temp1 = temp1.rename(columns={parameter:"mean_"+parameter})
    dsf_funda = pd.merge(dsf_funda, temp1, how = "left", on="date")
    
    temp1 = dsf_funda.groupby("date")[parameter].std()
    temp1 = temp1.to_frame()
    temp1["date"] = temp1.index
    temp1 = temp1.rename(columns={parameter:"std_"+parameter})
    dsf_funda = pd.merge(dsf_funda, temp1, how = "left", on="date")
    
    dsf_funda["z_"+parameter] = (dsf_funda[parameter] - dsf_funda["mean_"+parameter])/dsf_funda["std_"+parameter]
    
    return dsf_funda

if __name__ == "__main__":
    
    init_time = time.time()
    
    # loading the data
    funda = pd.read_csv("funda_1000_edited.csv") # read the compustat funda data
    dsf = pd.read_csv("dsf_1000_edited.csv") # read the crsp dsf data
    df_cpi = pd.read_csv("cpi.csv") # read the consumer price index data
    df_cpi['date'] =  pd.to_datetime(df_cpi['date'])
    df_cpi['date'] = df_cpi['date'] + datetime.timedelta(days=-1)
    
    # calculation of low beta(BAB) and Idiosyncratic vol(IVOL) from dsf data (doesn't need funda data)
    dsf['RET'] = np.where(dsf['RET']=="C", 0, dsf["RET"])
    dsf.RET = dsf.RET.astype("float")
    dsf["RET_3D"] = (1+dsf.RET)*(1+dsf.RET.shift(1))*(1+dsf.RET.shift(2)) -1 
    dsf["SPY_3D"] = (1+dsf.sprtrn)*(1+dsf.sprtrn.shift(1))*(1+dsf.sprtrn.shift(2)) -1 
    dsf = dsf.groupby('cusip').apply(lambda group: group.iloc[2:,:])
    
    dsf["vol_1y"] = dsf.rolling(250)["RET"].std()
    dsf["vol_spy_1y"] = dsf.rolling(250)["sprtrn"].std()
    dsf["corr_5y"] = dsf.rolling(1250)["RET_3D"].corr(dsf["SPY_3D"])
    
    "BAB is -beta"
    dsf["bab"] = (-dsf.corr_5y * dsf.vol_1y)/(dsf.vol_spy_1y)
    
    "dropping the nan values"
    dsf["alpha"]= -(dsf["RET_3D"] + dsf["bab"]*dsf["SPY_3D"])
    dsf["ivol"] = dsf.rolling(250)["alpha"].std()
    dsf = dsf.groupby('cusip').apply(lambda group: group.iloc[1250:,:])
    
    # merging the datasests (dsf, funda and cpi)
    funda = funda.sort_values(by=['cusip','date'])
    dsf = dsf.sort_values(by=['cusip','date'])
    dsf['cusip'] = dsf['cusip'].astype(str)
    funda['cusip'] = funda['cusip'].astype(str).str[:-1]
    dsf_funda = pd.merge(funda,dsf,how='left',on=['cusip','date']) # merge the dsf and funda data
    dsf_funda['date'] =  pd.to_datetime(dsf_funda['date'])
    dsf_funda = pd.merge(dsf_funda,df_cpi,how='left',on=['date']) # merege the dsf_funda and cpi data
    dsf_funda = dsf_funda.sort_values(by=['cusip','date'])
    del dsf,funda,df_cpi
    
    # profitability and growth parameters
    dsf_funda["gp"] = dsf_funda["revtq"] - dsf_funda["cogsq"] # growth profit (gp)
    dsf_funda["gpoa"] = (dsf_funda["gp"])/(dsf_funda["atq"]) # growth profit over assets (gpoa)
    dsf_funda["gpoa_delta_5"] = (dsf_funda["gp"] - dsf_funda["gp"].shift(20))/dsf_funda["atq"].shift(20) # growth of gpoa over the last 5 years
    
    dsf_funda["be"] = dsf_funda["seqq"] - dsf_funda["pstkq"] # book equity (be)
    dsf_funda["roe"] = dsf_funda["niq"]/dsf_funda["be"] # return on equity (roe)
    dsf_funda["roe_delta_5"] = (dsf_funda["roe"] - dsf_funda["roe"].shift(20))/dsf_funda["be"].shift(20) # growth of roe over the last 5 years
    
    dsf_funda["roa"] = dsf_funda.niq/dsf_funda.atq # return on assets (roa)
    dsf_funda["roa_delta_5"] = (dsf_funda["roa"] - dsf_funda["roa"].shift(20))/dsf_funda["atq"].shift(20) # growth of roa over the last 5 years
    
    dsf_funda["delta_wcapq"] = dsf_funda["wcapq"] - dsf_funda["wcapq"].shift(1) # change in working capital
    dsf_funda["cf"] = dsf_funda["niq"] + dsf_funda["dpq"] - dsf_funda["delta_wcapq"] - dsf_funda["capxy"] # cash flow
    dsf_funda["cfoa"] = dsf_funda["cf"]/dsf_funda["atq"] # cash flow over assets
    dsf_funda["cfoa_delta_5"] = (dsf_funda["cf"] - dsf_funda["cf"].shift(20))/dsf_funda["atq"].shift(20) # growth of cfoa over the last 5 years
    
    dsf_funda["gmar"] = dsf_funda["gp"]/dsf_funda["saleq"] # gross margin
    dsf_funda["gmar_delta_5"] = (dsf_funda["gp"] - dsf_funda["gp"].shift(20))/dsf_funda["saleq"].shift(20) # growth of gmar over the last 5 years
    
    dsf_funda["acc_num"] = dsf_funda["dpq"] - dsf_funda["delta_wcapq"] # accruals 
    dsf_funda["acc"] = dsf_funda["acc_num"]/dsf_funda["atq"] # accruals over assets
    dsf_funda["acc_delta_5"] = (dsf_funda["acc_num"] - dsf_funda["acc_num"].shift(20))/dsf_funda["atq"].shift(20) # growth of acc over the last 5 years
    
    # safety_parameters
    
    dsf_funda["lev"] = (dsf_funda["dlttq"] + dsf_funda["dlcq"] + dsf_funda["mibtq"] + dsf_funda["pstkq"])/dsf_funda["atq"] # leverage
    dsf_funda["me"] = dsf_funda["PRC"]*dsf_funda["SHROUT"] # market equity
    dsf_funda["adjasset"] = dsf_funda["atq"] + 0.1*(dsf_funda["me"] - dsf_funda["be"]) # Adjusted total assets (Total assets plus 10% of the difference between book equity and market equity)
    dsf_funda["tlta"] = (dsf_funda["dlcq"] + dsf_funda["dlttq"])/dsf_funda["adjasset"] # book value of debt/Adjusted total assets
    dsf_funda["wcta"] = (dsf_funda["actq"] + dsf_funda["lctq"])/dsf_funda["adjasset"] # Current assets - Current liabilities scaled by adjusted assets
    dsf_funda["clca"] = dsf_funda["lctq"]/dsf_funda["actq"] # Current liabilities/Current assets
    dsf_funda['oeneg'] = np.where(dsf_funda["ltq"]>dsf_funda["atq"], 1, 0) # A dummy variable which is equal to 1 if total liabilities exceed total assets
    dsf_funda["nita"] = dsf_funda["niq"]/dsf_funda["atq"] # Net Income/Total Assets
    dsf_funda["pt"] = dsf_funda["revtq"] - (dsf_funda["cogsq"] + dsf_funda["xsgaq"] \
                      + dsf_funda["dpq"] + dsf_funda["txtq"])   # pre tax income
    dsf_funda["futl"] = dsf_funda["pt"]/dsf_funda["ltq"] # pre tax income/total liabilities
    dsf_funda["niq_delta"] = dsf_funda.groupby("cusip")["niq"].shift(1) # Previous quarter's net income
    dsf_funda["intwo"] = np.where(((dsf_funda["niq"]<0) & (dsf_funda["niq_delta"]<0)), 1, 0) # A dummy equal to 1 if net income over the last two quarters is negative
    dsf_funda["chin"] = (dsf_funda["niq"] - dsf_funda["niq_delta"])/(np.abs(dsf_funda["niq"]) + np.abs(dsf_funda["niq_delta"])) # Change in net income (NI(t) - NI(t-1))/(NI(t) + NI(t-1))
    
    dsf_funda["o-score"] = -(-1.32 -0.407*np.log(dsf_funda["adjasset"]/dsf_funda["cpi"]) \
                            + 6.03*dsf_funda["tlta"] -1.43*dsf_funda["wcta"] +0.0076*dsf_funda["clca"] \
                            -1.72*dsf_funda["oeneg"] -2.37*dsf_funda["nita"] -1.83*dsf_funda["futl"] \
                            +0.285*dsf_funda["intwo"] -0.521*dsf_funda["chin"])
    
    
    dsf_funda["ebit"] = dsf_funda["revtq"] - (dsf_funda["cogsq"] + dsf_funda["xsgaq"] + dsf_funda["dpq"]) # Earnings before income tax
    dsf_funda["z-score"] = (1.2*dsf_funda["wcapq"] + 1.4*dsf_funda["req"] + 3.3*dsf_funda["ebit"] \
                           + 0.6*dsf_funda["me"]+ dsf_funda["saleq"])/dsf_funda["atq"] # Altman's Z-Score
    
    dsf_funda["evol"] = dsf_funda.groupby("cusip")["roe"].apply(pd.rolling_std, 20) # Standard Deviation of return on equity over the past 60 quarters
    
    
    # payout_parameters    
    dsf_funda["cshoq_delta_4"] = dsf_funda["cshoq"].shift(4) # Adjusted number of shares with a lag of 1 year
    dsf_funda["eiss"] = -np.log(dsf_funda["cshoq"]/dsf_funda["cshoq_delta_4"]) # Net equity issuance
    
    dsf_funda["total_debt"] = dsf_funda["dlttq"] + dsf_funda["dlcq"] + dsf_funda["mibtq"] + dsf_funda["pstkq"] # total debt
    dsf_funda["total_debt_delta_4"] = dsf_funda["total_debt"].shift(4) # Total debt with a lag of 1 year
    dsf_funda["diss"] = dsf_funda["total_debt"]/dsf_funda["total_debt_delta_4"] # One year percent change in total debt
    
    dsf_funda["teqq_delta_20"] = dsf_funda["teqq"].shift(20) # book equity
    dsf_funda["delta_be_5yr"] = dsf_funda["teqq"] - dsf_funda["teqq_delta_20"] # changes in book equity
    dsf_funda["npop"] = (dsf_funda["ibq"] - dsf_funda["delta_be_5yr"])/(dsf_funda["revtq"] - dsf_funda["cogsq"]) # sum of total net payout over the past 5 years/total profits
    
    dsf_funda = dsf_funda.groupby('cusip').apply(lambda group: group.iloc[20:,:]) # removing the corrupted data(the first few elements which doens't belong to a particular cusip)
    
    parameters = ["date","cusip","gpoa","roe","roa","cfoa","gmar","acc","gpoa_delta_5","roe_delta_5","roa_delta_5" \
                  ,"cfoa_delta_5","gmar_delta_5","acc_delta_5","bab","ivol","lev","o-score","z-score", \
                  "evol","eiss","diss","npop"] # collecting all the necessary parameters
    dsf_funda = dsf_funda[parameters] # substetting the data
    dsf_funda = dsf_funda.dropna(how='all') # dropping off the nan values
        
    # z_scores
    # calculating the z scores for all the parameters
    for item in parameters[2:]:
        dsf_funda = z_score_calc(dsf_funda,item) 

    # calculating the profitability parameter
    dsf_funda["profitability"] = dsf_funda["z_gpoa"] + dsf_funda["z_roe"] + dsf_funda["z_roa"] + \
                                dsf_funda["z_cfoa"] + dsf_funda["z_gmar"] + dsf_funda["z_acc"]
     
    # calculating the growth parameter                           
    dsf_funda["growth"] = dsf_funda["z_gpoa_delta_5"] + dsf_funda["z_roe_delta_5"] + \
                          dsf_funda["z_roa_delta_5"] + dsf_funda["z_cfoa_delta_5"] + \
                          dsf_funda["z_gmar_delta_5"] + dsf_funda["z_acc_delta_5"]
    
    # calculating the safety parameter                      
    dsf_funda["safety"] = dsf_funda["z_bab"] + dsf_funda["z_ivol"] + dsf_funda["z_lev"] \
                          + dsf_funda["z_o-score"] + dsf_funda["z_z-score"] + dsf_funda["z_evol"]
    
    # calculating the payout parameter
    dsf_funda["payout"] = dsf_funda["z_eiss"] + dsf_funda["z_diss"] + dsf_funda["z_npop"]
    
    final_parameters = ["profitability","growth","safety","payout"]
    
    # calculating z scores for the final parameters
    for item in final_parameters:
        dsf_funda = z_score_calc(dsf_funda,item)
    
    # calculating the quality score
    dsf_funda["quality"] = dsf_funda["z_profitability"] + dsf_funda["z_growth"] \
                           + dsf_funda["z_safety"] + dsf_funda["z_payout"]
    
    # z-score of quality score
    dsf_funda = z_score_calc(dsf_funda,"quality")
    
    # exporting the raw data
    dsf_funda = dsf_funda.sort_values(["date","cusip"]).reset_index(drop=True)
    dsf_funda.to_csv("dsf_funda_quality_score_raw.csv")
    
    # cleaning the data
    dsf_funda_clean = dsf_funda.dropna().reset_index(drop=True)
    dsf_funda_clean = dsf_funda_clean.sort_values(["date","cusip"]).reset_index(drop=True)
    dsf_funda_clean.to_csv("dsf_funda_quality_score_clean.csv")
    
    print ("Total time taken: ", time.time() - init_time)