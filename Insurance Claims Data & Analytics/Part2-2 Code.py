#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 21:15:24 2021

@author: qunist
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_in= pd.read_csv("VTINP16_upd.txt")
df_in = df_in.apply(pd.to_numeric,errors='coerce')
df_in["CHRGS"] = pd.to_numeric(df_in["CHRGS"])
df = df_in.copy()

df_in_4insurance = df[df['PPAY'].isin([1,6,7])]
df_in_4insurance['PPAY'].replace({1:'MEDICARE',6: 'Commercial Payers',7: 'Commercial Payers'}, inplace=True)

df_in_4insurance_new = df_in_4insurance[['hnum2','intage','sex','CHRGS','PPAY','MDC','DRG','hsa']]
hospitalname= pd.read_excel("CaseStudy_O-D_HospMonopoly.xlsx",sheet_name='Hosp_Destination')
hospitalname.columns = ['hnum2','HospitalName Des','RR Des','RR Name Des']

hsaname = pd.read_excel("CaseStudy_O-D_HospMonopoly.xlsx",sheet_name='HSA_Pt_Origin')
hsaname.columns = ['hsa','HSA Name Org','RR Collapsed Referral Region Org','Name Org','RR Name Org']
df_with_des = pd.merge(df_in_4insurance_new ,hospitalname ,how='left',on=['hnum2'])
df_with_des_org = pd.merge(df_with_des ,hsaname ,how='left',on=['hsa'])
#df_with_des_org = pd.merge(df_in_4insurance_new ,hsaname ,how='left',on=['hsa'])

#df_with_des_org = df[df['PPAY'].isin([1,6,7])]


df_with_des_org['Care_Type'] = np.ones(len(df_with_des_org))
for i in range(len(df_with_des_org)):
    if  df_with_des_org['MDC'].iloc[i]== 5:
        df_with_des_org['Care_Type'].iloc[i] = 'High-end care'
    elif df_with_des_org['MDC'].iloc[i]== 8:
        df_with_des_org['Care_Type'].iloc[i] = 'Low-end care'
    else:  df_with_des_org['Care_Type'].iloc[i] = 'Other care'

df_with_des_org['Payer_Type'] = np.ones(len(df_with_des_org))
for i in range(len(df_with_des_org)):
    if  df_with_des_org['PPAY'].iloc[i]== 'MEDICARE':
        df_with_des_org['Payer_Type'].iloc[i] = 'Low-end Payer'
    elif df_with_des_org['PPAY'].iloc[i]== 'Commercial Payers':
         df_with_des_org['Payer_Type'].iloc[i] = 'High-end Payers'    
    else:  df_with_des_org['Payer_Type'].iloc[i] = 'Other Payers'

df_with_des_org["CHRGS"]= df_with_des_org["CHRGS"].fillna(0)

#%%
def piechart_chrgs(df,regionname):
    table = df[df['RR Des'].isin([regionname])]
    bd = table.groupby(['RR Name Org','HospitalName Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
    sumRow = bd.sum(axis = 1)
    bd['Total Charges'] = sumRow
    sumCol = bd.sum(axis = 0)
    bd = bd.set_index(bd['RR Name Org']) 
    bd = bd.iloc[:,1:]
    bd.loc['Destination Hosp SubTotal:'] = sumCol
    
    perc_bd = bd.iloc[-1,0:len(bd.columns)-1]/sumCol[-1]
    fig, ax = plt.subplots(figsize=(5, 5))
 
    theme = plt.get_cmap('bwr')
    ax.set_prop_cycle("color", [theme(1. * i / len(perc_bd))
                             for i in range(len(perc_bd))])
    ax.pie(perc_bd, labels=perc_bd.index, autopct='%1.2f%%', pctdistance=0.6, explode=(0,0.2,0.2),
        shadow=True, startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()
    return bd
                  
    
#table 1
low_low = df_with_des_org[(df_with_des_org['Care_Type'] == 'Low-end care') & df_with_des_org['Payer_Type'].isin(['Low-end Payer'])]
ctable1 = low_low.groupby(['RR Name Org','RR Name Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
sumRow = ctable1.sum(axis = 1)
ctable1['Total Charges'] = sumRow
sumCol = ctable1.sum(axis = 0)
ctable1 = ctable1.set_index(ctable1['RR Name Org']) 
ctable1 = ctable1.iloc[:,1:]
ctable1.loc['Destination Hosp SubTotal:'] = sumCol

c_bd1 = piechart_chrgs(low_low,'RR1')
print(c_bd1)

#table 2
low_high = df_with_des_org[(df_with_des_org['Care_Type'] == 'Low-end care') & df_with_des_org['Payer_Type'].isin(['High-end Payers'])]
ctable2 = low_high.groupby([ 'RR Name Org','RR Name Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
sumRow = ctable2.sum(axis = 1)
ctable2['Total Charges'] = sumRow
sumCol = ctable2.sum(axis = 0)
ctable2 = ctable2.set_index(ctable2['RR Name Org']) 
ctable2 = ctable2.iloc[:,1:]
ctable2.loc['Destination Hosp SubTotal:'] = sumCol

c_bd2 = piechart_chrgs(low_high,'RR1')
print(c_bd2)

#table 3
high_low = df_with_des_org[(df_with_des_org['Care_Type'] == 'High-end care') & df_with_des_org['Payer_Type'].isin(['Low-end Payer'])]
ctable3 = high_low.groupby([ 'RR Name Org','RR Name Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
sumRow = ctable3.sum(axis = 1)
ctable3['Total Charges'] = sumRow
sumCol = ctable3.sum(axis = 0)
ctable3 = ctable3.set_index(ctable3['RR Name Org']) 
ctable3 = ctable3.iloc[:,1:]
ctable3.loc['Destination Hosp SubTotal:'] = sumCol

c_bd3 = piechart_chrgs(high_low,'RR1')
print(c_bd3)

#table 4
high_high = df_with_des_org[(df_with_des_org['Care_Type'] == 'High-end care') & df_with_des_org['Payer_Type'].isin(['High-end Payers'])]
ctable4 = high_high.groupby([ 'RR Name Org','RR Name Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
sumRow = ctable4.sum(axis = 1)
ctable4['Total Charges'] = sumRow
sumCol = ctable4.sum(axis = 0)
ctable4 = ctable4.set_index(ctable4['RR Name Org']) 
ctable4 = ctable4.iloc[:,1:]
ctable4.loc['Destination Hosp SubTotal:'] = sumCol

c_bd4 = piechart_chrgs(high_high,'RR1')
print(c_bd4)


#%% Optional DRG

def piechart_DRG_chrgs(df,regionname):
    table = df[df['RR Des'].isin([regionname])]
    bd = table.groupby(['RR Name Org', 'DRG'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
    sumRow = bd.sum(axis = 1)
    bd['Total Charges'] = sumRow
    sumCol = bd.sum(axis = 0)
    bd = bd.set_index(bd['RR Name Org']) 
    bd = bd.iloc[:,1:]
    #bd = table.sort_values(by= 'CHRGS', ascending = False).head(10)
    bd.loc['Destination Hosp SubTotal:'] = sumCol
    
    perc_bd = bd.iloc[-1,0:len(bd.columns)-1]/sumCol[-1]
    fig, ax = plt.subplots(figsize=(5, 5))
 
    theme = plt.get_cmap('bwr')
    ax.set_prop_cycle("color", [theme(1. * i / len(perc_bd))
                             for i in range(len(perc_bd))])
    ax.pie(perc_bd, labels=perc_bd.index, autopct='%1.1f%%',
        shadow=True, startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()
    return bd


#table 1 #HospitalName Des
#By Areas
low_low1 = df_with_des_org[(df_with_des_org['Care_Type'] == 'Low-end care') & df_with_des_org['Payer_Type'].isin(['Low-end Payer'])]
ctable_drg1 = low_low1.groupby(['DRG','RR Name Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
                  
sumRow = ctable_drg1.sum(axis = 1)
ctable_drg1['Total Charges'] = sumRow
ctable_drg1 = ctable_drg1.set_index(ctable_drg1['DRG']) 
ctable_drg1 = ctable_drg1.iloc[:,1:]
ctable_drg1  = ctable_drg1.sort_values(by= 'Total Charges', ascending = False).head(10)
#ctable_drg1  = ctable_drg1.sort_values(by= 'RR1--Burlington', ascending = False).head(10)
sumCol = ctable1.sum(axis = 0)
ctable_drg1.loc['Destination DRG SubTotal:'] = sumCol
print(ctable_drg1)

#c_bd5 = piechart_DRG_chrgs(low_low,'RR1')
#print(c_bd5)


#By Hopsital
low_low1 = df_with_des_org[(df_with_des_org['Care_Type'] == 'Low-end care') & df_with_des_org['Payer_Type'].isin(['Low-end Payer'])]
ctable_drg1 = low_low1.groupby(['DRG','HospitalName Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
                  
ctable_drg1 = pd.DataFrame(ctable_drg1, columns=['DRG', 'Northwestern Medical Center',
       'Porter Medical Center', 'University of Vermont Medical Center (as of 2014)', 
       'Rutland Regional Medical Center', 'Southwestern Vermont Medical Center'])
                  

sumRow = ctable_drg1.sum(axis = 1)
ctable_drg1['Total Charges'] = sumRow
ctable_drg1 = ctable_drg1.set_index(ctable_drg1['DRG']) 
ctable_drg1 = ctable_drg1.iloc[:,1:]
ctable_drg1  = ctable_drg1.sort_values(by= 'Total Charges', ascending = False).head(10)
#ctable_drg1  = ctable_drg1.sort_values(by= 'RR1--Burlington', ascending = False).head(10)
#ctable_drg1 = ctable_drg1.sort_values(by = [470.0, 460.0], axis = 1, ascending = False).head(10)
sumCol = ctable_drg1.sum(axis = 0)
ctable_drg1.loc['Destination DRG SubTotal:'] = sumCol
#ctable_drg1  = ctable_drg1.sort_values(by= 'Destination DRG SubTotal:', axis = 1, ascending = False).head(10)
print(ctable_drg1)

#c_bd5 = piechart_DRG_chrgs(low_low,'RR1')
#print(c_bd5)


#%%table 2
#By Areas
low_high1 = df_with_des_org[(df_with_des_org['Care_Type'] == 'Low-end care') & df_with_des_org['Payer_Type'].isin(['High-end Payers'])]
ctable_drg2 = low_high1.groupby(['DRG','RR Name Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
                  
sumRow = ctable_drg2.sum(axis = 1)
ctable_drg2['Total Charges'] = sumRow
ctable_drg2 = ctable_drg2.set_index(ctable_drg2['DRG']) 
ctable_drg2 = ctable_drg2.iloc[:,1:]
ctable_drg2 = ctable_drg2.sort_values(by= 'Total Charges', ascending = False).head(10)
##ctable_drg2  = ctable_drg2.sort_values(by= 'RR1--Burlington', ascending = False).head(10)
#ctable_drg2 = ctable_drg2.sort_values(by = [470.0, 460.0], axis = 1, ascending = False).head(10)
sumCol = ctable_drg2.sum(axis = 0)
ctable_drg2.loc['Destination DRG SubTotal:'] = sumCol
print(ctable_drg2)

#c_bd6 = piechart_DRG_chrgs(low_high1,'RR1')
#print(c_bd6)


#By Hopsital
low_high1 = df_with_des_org[(df_with_des_org['Care_Type'] == 'Low-end care') & df_with_des_org['Payer_Type'].isin(['High-end Payers'])]
ctable_drg2 = low_high1.groupby(['DRG','HospitalName Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)

ctable_drg2 = pd.DataFrame(ctable_drg2, columns=['DRG', 'Northwestern Medical Center',
       'Porter Medical Center', 'University of Vermont Medical Center (as of 2014)', 
       'Rutland Regional Medical Center', 'Southwestern Vermont Medical Center'])


sumRow = ctable_drg2.sum(axis = 1)
ctable_drg2['Total Charges'] = sumRow
ctable_drg2 = ctable_drg2.set_index(ctable_drg2['DRG']) 
ctable_drg2 = ctable_drg2.iloc[:,1:]
ctable_drg2 = ctable_drg2.sort_values(by= 'Total Charges', ascending = False).head(10)
#ctable_drg2  = ctable_drg2.sort_values(by= 'RR1--Burlington', ascending = False).head(10)
#ctable_drg2 = ctable_drg2.sort_values(by = [470.0, 460.0], axis = 1, ascending = False).head(10)
sumCol = ctable_drg2.sum(axis = 0)
ctable_drg2.loc['Destination DRG SubTotal:'] = sumCol
#ctable_drg2  = ctable_drg2.sort_values(by= 'Destination DRG SubTotal:', axis = 1, ascending = False).head(10)
print(ctable_drg2)

#c_bd6 = piechart_DRG_chrgs(low_high1,'RR1')
#print(c_bd6)


#%%table 3
#By Areas
high_low1 = df_with_des_org[(df_with_des_org['Care_Type'] == 'High-end care') & df_with_des_org['Payer_Type'].isin(['Low-end Payer'])]
ctable_drg3 = high_low1.groupby(['DRG','RR Name Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
                  
sumRow = ctable_drg3.sum(axis = 1)
ctable_drg3['Total Charges'] = sumRow
ctable_drg3 = ctable_drg3.set_index(ctable_drg3['DRG']) 
ctable_drg3 = ctable_drg3.iloc[:,1:]
ctable_drg3 = ctable_drg3.sort_values(by= 'Total Charges', ascending = False).head(10)
#ctable_drg3  = ctable_drg3.sort_values(by= 'RR1--Burlington', ascending = False).head(10)  
sumCol = ctable_drg3.sum(axis = 0)
ctable_drg3.loc['Destination DRG SubTotal:'] = sumCol
print(ctable_drg3)

c_bd7 = piechart_DRG_chrgs(high_low1,'RR1')
print(c_bd7)

#By Hopsital
high_low1 = df_with_des_org[(df_with_des_org['Care_Type'] == 'High-end care') & df_with_des_org['Payer_Type'].isin(['Low-end Payer'])]
ctable_drg3 = high_low1.groupby(['DRG','HospitalName Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
                  
ctable_drg3 = pd.DataFrame(ctable_drg3, columns=['DRG', 'Northwestern Medical Center',
       'Porter Medical Center', 'University of Vermont Medical Center (as of 2014)', 
       'Rutland Regional Medical Center', 'Southwestern Vermont Medical Center'])
                  
sumRow = ctable_drg3.sum(axis = 1)
ctable_drg3['Total Charges'] = sumRow
ctable_drg3 = ctable_drg3.set_index(ctable_drg3['DRG']) 
ctable_drg3 = ctable_drg3.iloc[:,1:]
ctable_drg3 = ctable_drg3.sort_values(by= 'Total Charges', ascending = False).head(10)
#ctable_drg3  = ctable_drg3.sort_values(by= 'RR1--Burlington', ascending = False).head(10)
#ctable_drg3 = ctable_drg3.sort_values(by = [470.0, 460.0], axis = 1, ascending = False).head(10)  
sumCol = ctable_drg3.sum(axis = 0)
ctable_drg3.loc['Destination DRG SubTotal:'] = sumCol
#ctable_drg3  = ctable_drg3.sort_values(by= 'Destination DRG SubTotal:', axis = 1, ascending = False).head(10)
print(ctable_drg3)

#c_bd7 = piechart_DRG_chrgs(high_low1,'RR1')
#print(c_bd7)


#%%table 4
#By Areas
high_high1 = df_with_des_org[(df_with_des_org['Care_Type'] == 'High-end care') & df_with_des_org['Payer_Type'].isin(['High-end Payers'])]
ctable_drg4 = high_high1.groupby(['DRG','RR Name Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
sumRow = ctable_drg4.sum(axis = 1)
ctable_drg4['Total Charges'] = sumRow
ctable_drg4 = ctable_drg4.set_index(ctable_drg4['DRG']) 
ctable_drg4 = ctable_drg4.iloc[:,1:]
ctable_drg4 = ctable_drg4.sort_values(by= 'Total Charges', ascending = False).head(10)
#ctable_drg4  = ctable_drg4.sort_values(by= 'RR1--Burlington', ascending = False).head(10)
sumCol = ctable_drg4.sum(axis = 0)  
ctable_drg4.loc['Destination DRG SubTotal:'] = sumCol
print(ctable_drg4)

#c_bd8 = piechart_DRG_chrgs(high_high1,'RR1')
#print(c_bd8)


#By Hopsital
high_high1 = df_with_des_org[(df_with_des_org['Care_Type'] == 'High-end care') & df_with_des_org['Payer_Type'].isin(['High-end Payers'])]
ctable_drg4 = high_high1.groupby(['DRG','HospitalName Des'])["CHRGS"].apply(lambda x : x.astype(int).sum()) \
                  .unstack(fill_value=0) \
                  .reset_index() \
                  .rename_axis(None, axis=1)
                  
ctable_drg4 = pd.DataFrame(ctable_drg4, columns=['DRG', 'Northwestern Medical Center',
       'Porter Medical Center', 'University of Vermont Medical Center (as of 2014)', 
       'Rutland Regional Medical Center', 'Southwestern Vermont Medical Center'])
#'North Country Hospital And Health Center'

sumRow = ctable_drg4.sum(axis = 1)
ctable_drg4['Total Charges'] = sumRow
ctable_drg4 = ctable_drg4.set_index(ctable_drg4['DRG']) 
ctable_drg4 = ctable_drg4.iloc[:,1:]
ctable_drg4 = ctable_drg4.sort_values(by= 'Total Charges', ascending = False).head(10)
#ctable_drg4  = ctable_drg4.sort_values(by= 'RR1--Burlington', ascending = False).head(10)
#ctable_drg4 = ctable_drg4.sort_values(by = [470.0, 460.0], axis = 1, ascending = False).head(10) 
sumCol = ctable_drg4.sum(axis = 0)
ctable_drg4.loc['Destination DRG SubTotal:'] = sumCol
#ctable_drg4  = ctable_drg4.sort_values(by= 'Destination DRG SubTotal:', axis = 1, ascending = False).head(10)
print(ctable_drg4)

#c_bd8 = piechart_DRG_chrgs(high_high1,'RR1')
#print(c_bd8)
