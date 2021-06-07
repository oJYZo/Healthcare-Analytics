#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 21:48:09 2021

@author: 14830
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#inpatient = pd.read_csv('VTINP16_upd.csv')
df_in = pd.read_csv("VTINP16_upd.txt", low_memory = False)
df = df_in.copy()

df_in_4insurance = df[df['PPAY'].isin([1,6,7])]
df_in_4insurance['PPAY'].replace({1:'MEDICARE', 6: 'Commercial Payers',7: 'Commercial Payers'}, inplace=True)

df_in_4insurance_new = df_in_4insurance[['hnum2','intage','sex','CHRGS','PPAY','MDC','DRG','hsa']]
hospitalname= pd.read_excel("CaseStudy_O-D_HospMonopoly.xlsx",sheet_name='Hosp_Destination')
hospitalname.columns = ['hnum2','HospitalName Des','RR Des','RR Name Des']

hsaname = pd.read_excel("CaseStudy_O-D_HospMonopoly.xlsx",sheet_name='HSA_Pt_Origin')
hsaname.columns = ['hsa','HSA Name Org','RR Collapsed Referral Region Org','Name Org','RR Name Org']

#merge
#Hosp_Destination
df_with_des = pd.merge(df_in_4insurance_new ,hospitalname, how='left',on=['hnum2'])

#HSA_Pt_Origin
df_with_des_org = pd.merge(df_with_des ,hsaname ,how='left',on=['hsa'])


df_with_des_org['Care_Type'] = np.ones(len(df_with_des_org))
for i in range(len(df_with_des_org)):
    if  df_with_des_org['MDC'].iloc[i]== '5':
        df_with_des_org['Care_Type'].iloc[i] = 'High-end care'
    elif df_with_des_org['MDC'].iloc[i]== '8':
        df_with_des_org['Care_Type'].iloc[i] = 'Low-end care'
    else:  df_with_des_org['Care_Type'].iloc[i] = 'Other care'


df_with_des_org['Payer_Type'] = np.ones(len(df_with_des_org))
for i in range(len(df_with_des_org)):
    if  df_with_des_org['PPAY'].iloc[i]== 'MEDICARE':
        df_with_des_org['Payer_Type'].iloc[i] = 'Low-end Payer'
    elif df_with_des_org['PPAY'].iloc[i]== 'Commercial Payers':
         df_with_des_org['Payer_Type'].iloc[i] = 'High-end Payers'    
    else:  df_with_des_org['Payer_Type'].iloc[i] = 'Other Payers'

#print(df_with_des_org)

origin = df_with_des.copy()
destination = df_with_des_org.copy()

origin['hsa'].replace({1:'RR2', 2:'RR1', 3:'RR2', 4:'RR4', 5:'RR3', 6:'RR3', 7:'RR1', 8:'RR1', \
                       9:'RR5', 10:'RR5', 11:'RR4', 12:'RR4', 13: 'RR4', 98:'Z_OutState', 99:'Missing'}, inplace=True)
    
origin['hnum2'].replace({1:'RR1', 2:'RR3', 3:'RR3', 4:'RR2', 5:'RR1', 6:'RR2', 8:'RR5', \
                         9:'RR1', 10:'RR4', 11:'RR4', 12:'RR4', 14: 'RR4', 15:'RR4', 16:'RR5'}, inplace=True)

origin = origin.rename(columns = {'hsa':'RRName'}, inplace = False) 
    
def piechart(df,regionname):
    table = df[df['RR Des'].isin([regionname])]
    bd = pd.crosstab(index = table['RRName'], columns = table['HospitalName Des'])
    sumRow = bd.sum(axis = 1)
    bd['Total Admission'] = sumRow
    sumCol = bd.sum(axis = 0)
    bd.loc['Destination Hosp SubTotal'] = sumCol
    print(bd)
    
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


#High-end care(circulatory) * High-end Payers(commercial)
#origin['MDC'].unique()
highcare_highpayer = origin[(origin['MDC'] == '5') & origin['PPAY'].isin(['Commercial Payers'])]
table1 = pd.crosstab(index = highcare_highpayer['RRName'], columns = highcare_highpayer['RR Name Des'])

table1 = table1.loc[['RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'Z_OutState', 'Missing'], :]
#or drop these two rows
#table1 = table1.drop(['Missing', 'Z_OutState'])
sumRow = table1.sum(axis = 1)
table1['Total Admission'] = sumRow
sumCol = table1.sum(axis = 0)
table1.loc['Destination Hosp SubTotal:'] = sumCol
print(table1)

a_bd1 = piechart(highcare_highpayer,'RR1')
print(a_bd1)


#Low-end care(musculoskeletal) * High-end Payers(commercial)
lowcare_highpayer = origin[(origin['MDC'] == '8') & origin['PPAY'].isin(['Commercial Payers'])]
table2 = pd.crosstab(index = lowcare_highpayer['RRName'], columns = lowcare_highpayer['RR Name Des'])
table2 = table2.loc[['RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'Z_OutState', 'Missing'], :]
#or drop these two rows
#table2 = table2.drop(['Missing', 'Z_OutState'])

sumRow2 = table2.sum(axis = 1)
table2['Total Admission'] = sumRow2
sumCol2 = table2.sum(axis = 0)
table2.loc['Destination Hosp SubTotal:'] = sumCol2
print(table2)

a_bd2 = piechart(lowcare_highpayer,'RR1')
print(a_bd2)


#High-end care(circulatory) * Low-end Payers(medicare)
highcare_lowpayer = origin[(origin['MDC'] == '5') & origin['PPAY'].isin(['MEDICARE'])]
table3 = pd.crosstab(index = highcare_lowpayer['RRName'], columns = highcare_lowpayer['RR Name Des'])
table3 = table3.loc[['RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'Z_OutState'], :]
#or drop this row
#table3 = table3.drop(['Z_OutState'])

sumRow3 = table3.sum(axis = 1)
table3['Total Admission'] = sumRow3
sumCol3 = table3.sum(axis = 0)
table3.loc['Destination Hosp SubTotal:'] = sumCol3
print(table3)

a_bd3_1 = piechart(highcare_lowpayer,'RR1')
print(a_bd3_1)

## RR5 Breakdown
a_bd3_5 = piechart(highcare_lowpayer,'RR5')
print(a_bd3_5)


#Low-end care(musculoskeletal) * Low-end Payers(medicare)
lowcare_lowpayer = origin[(origin['MDC'] == '8') & origin['PPAY'].isin(['MEDICARE'])]
table4 = pd.crosstab(index = lowcare_lowpayer['RRName'], columns = lowcare_lowpayer['RR Name Des'])
#table4 = table4.loc[['RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'Z_OutState'], :]
#or drop these two rows
table4 = table4.drop(['Z_OutState'])

sumRow4 = table4.sum(axis = 1)
table4['Total Admission'] = sumRow4
sumCol4 = table4.sum(axis = 0)
table4.loc['Destination Hosp SubTotal:'] = sumCol4
print(table4)

a_bd4 = piechart(lowcare_lowpayer,'RR1')
print(a_bd4)


#%% Optional DRG
def piechart_DRG(df,regionname):
    table = df[df['RR Des'].isin([regionname])]
    bd = pd.crosstab(index = table['RRName'], columns = table['DRG'])
    #bd = table.sort_values(by='RR1--Burlington', ascending = False).head(10)
    sumRow = bd.sum(axis = 1)
    bd['Total Admission'] = sumRow
    sumCol = bd.sum(axis = 0)
    bd.loc['Destination Hosp SubTotal'] = sumCol
    #print(bd)
    
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

#%% High-end care(circulatory) * High-end Payers(commercial)
#origin['MDC'].unique()
#origin['DRG'].unique()
#By Areas
highcare_highpayer1 = origin[(origin['MDC'] == '5') & origin['PPAY'].isin(['Commercial Payers'])]
table_drg1 = pd.crosstab(index = highcare_highpayer1['DRG'], columns = highcare_highpayer1['RR Name Des'])
table_drg1  = table_drg1.sort_values(by= 'RR1--Burlington', ascending = False).head(10)

sumRow5 = table_drg1.sum(axis = 1)
table_drg1['Total Admission'] = sumRow5
sumCol5 = table_drg1.sum(axis = 0)
table_drg1.loc['Destination DRG SubTotal:'] = sumCol5
print(table_drg1)

## RR1 Breakdown
#a_bd5 = piechart_DRG(highcare_highpayer1,'RR1')
#print(a_bd5)


#By Hopsital
highcare_highpayer1 = origin[(origin['MDC'] == '5') & origin['PPAY'].isin(['Commercial Payers'])]
table_drg1 = pd.crosstab(index = highcare_highpayer1['DRG'], columns = highcare_highpayer1['HospitalName Des'])
table_drg1 = pd.DataFrame(table_drg1, columns=['Northwestern Medical Center',
       'Porter Medical Center', 'University of Vermont Medical Center (as of 2014)', 
       'Rutland Regional Medical Center', 'Southwestern Vermont Medical Center'])

sumRow5 = table_drg1.sum(axis = 1)
table_drg1['Total Admission'] = sumRow5
table_drg1 = table_drg1.sort_values(by= 'Total Admission', ascending = False).head(10)
sumCol5 = table_drg1.sum(axis = 0)
table_drg1.loc['Destination DRG SubTotal:'] = sumCol5
print(table_drg1)


#%% Low-end care(musculoskeletal) * High-end Payers(commercial)
#By Areas
lowcare_highpayer1 = origin[(origin['MDC'] == '8') & origin['PPAY'].isin(['Commercial Payers'])]
table_drg2 = pd.crosstab(index = lowcare_highpayer1['DRG'], columns = lowcare_highpayer1['RR Name Des'])
table_drg2  = table_drg2.sort_values(by= 'RR1--Burlington', ascending = False).head(10)

sumRow6 = table_drg2.sum(axis = 1)
table_drg2['Total Admission'] = sumRow6
sumCol6 = table_drg2.sum(axis = 0)
table_drg2.loc['Destination DRG SubTotal:'] = sumCol6
print(table_drg2)

## RR1 Breakdown
#a_bd6 = piechart_DRG(lowcare_highpayer1,'RR1')
#print(a_bd6)

#By Hopsital
lowcare_highpayer1 = origin[(origin['MDC'] == '8') & origin['PPAY'].isin(['Commercial Payers'])]
table_drg2 = pd.crosstab(index = lowcare_highpayer1['DRG'], columns = lowcare_highpayer1['HospitalName Des'])
table_drg2 = pd.DataFrame(table_drg2, columns=['Northwestern Medical Center',
       'Porter Medical Center', 'University of Vermont Medical Center (as of 2014)', 
       'Rutland Regional Medical Center', 'Southwestern Vermont Medical Center'])

sumRow6 = table_drg2.sum(axis = 1)
table_drg2['Total Admission'] = sumRow6
table_drg2 = table_drg2.sort_values(by= 'Total Admission', ascending = False).head(10)
sumCol6 = table_drg2.sum(axis = 0)
table_drg2.loc['Destination DRG SubTotal:'] = sumCol6
print(table_drg2)


#%% High-end care(circulatory) * Low-end Payers(medicare)
#By Areas
highcare_lowpayer1 = origin[(origin['MDC'] == '5') & origin['PPAY'].isin(['MEDICARE'])]
table_drg3 = pd.crosstab(index = highcare_lowpayer1['DRG'], columns = highcare_lowpayer1['RR Name Des'])
table_drg3  = table_drg3.sort_values(by= 'RR1--Burlington', ascending = False).head(10)
#table_drg3  = table_drg3.sort_values(by= 'RR5--Rutland', ascending = False).head(10)

sumRow7 = table_drg3.sum(axis = 1)
table_drg3['Total Admission'] = sumRow7
sumCol7 = table_drg3.sum(axis = 0)
table_drg3.loc['Destination DRG SubTotal:'] = sumCol7
print(table_drg3)

## RR1 Breakdown
#a_bd7_1 = piechart_DRG(highcare_lowpayer1,'RR1')
#print(a_bd7_1)
## RR5 Breakdown
#a_bd7_5 = piechart_DRG(highcare_lowpayer1,'RR5')
#print(a_bd7_5)

#By Hopsital
highcare_lowpayer1 = origin[(origin['MDC'] == '5') & origin['PPAY'].isin(['MEDICARE'])]
table_drg3 = pd.crosstab(index = highcare_lowpayer1['DRG'], columns = highcare_lowpayer1['HospitalName Des'])
table_drg3 = pd.DataFrame(table_drg3, columns=['Northwestern Medical Center',
       'Porter Medical Center', 'University of Vermont Medical Center (as of 2014)', 
       'Rutland Regional Medical Center', 'Southwestern Vermont Medical Center'])

sumRow7 = table_drg3.sum(axis = 1)
table_drg3['Total Admission'] = sumRow7
table_drg3 = table_drg3.sort_values(by= 'Total Admission', ascending = False).head(10)
sumCol7 = table_drg3.sum(axis = 0)
table_drg3.loc['Destination DRG SubTotal:'] = sumCol7
print(table_drg3)


#%% Low-end care(musculoskeletal) * Low-end Payers(medicare)
#By Areas
lowcare_lowpayer1 = origin[(origin['MDC'] == '8') & origin['PPAY'].isin(['MEDICARE'])]
table_drg4 = pd.crosstab(index = lowcare_lowpayer1['DRG'], columns = lowcare_lowpayer1['RR Name Des'])
table_drg4  = table_drg4.sort_values(by= 'RR1--Burlington', ascending = False).head(10)

sumRow8 = table_drg4.sum(axis = 1)
table_drg4['Total Admission'] = sumRow8
sumCol8 = table_drg4.sum(axis = 0)
table_drg4.loc['Destination DRG SubTotal:'] = sumCol8
print(table_drg4)

## RR1 Breakdown
#a_bd8 = piechart_DRG(lowcare_lowpayer1,'RR1')
#print(a_bd8)

#By Hopsital
lowcare_lowpayer1 = origin[(origin['MDC'] == '8') & origin['PPAY'].isin(['MEDICARE'])]
table_drg4 = pd.crosstab(index = lowcare_lowpayer1['DRG'], columns = lowcare_lowpayer1['HospitalName Des'])
table_drg4 = pd.DataFrame(table_drg4, columns=['Northwestern Medical Center',
       'Porter Medical Center', 'University of Vermont Medical Center (as of 2014)', 
       'Rutland Regional Medical Center', 'Southwestern Vermont Medical Center'])

sumRow8 = table_drg4.sum(axis = 1)
table_drg4['Total Admission'] = sumRow8
table_drg4 = table_drg4.sort_values(by= 'Total Admission', ascending = False).head(10)
sumCol8 = table_drg4.sum(axis = 0)
table_drg4.loc['Destination DRG SubTotal:'] = sumCol8
print(table_drg4)

