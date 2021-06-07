# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 17:25:40 2021

@author: 14830
"""
import csv
import numpy as np
import pandas as pd
import scipy.stats as stats


#read text files and transform to CSV format and load CSV file
df = pd.read_csv("VTINP16_upd.txt") 
df.to_csv('VTINP16_upd.csv', index = None) 
inpatient = pd.read_csv('VTINP16_upd.csv')


df2 = pd.read_csv("VTREVCODE16.txt") 
df2.to_csv('VTREVCODE16.csv', index = None) 
REVCODE = pd.read_csv('VTREVCODE16.csv')

#Only need to print this three lines below for Q3
df3 = pd.read_csv("VTED16.txt") 
df3.to_csv('VTED16.csv', index = None)
Emergency = pd.read_csv('VTED16.csv', low_memory = False)

#%% Q1 ED
patient1 = Emergency[Emergency['UNIQ'].isin(['507033'])]
patient2 = Emergency[Emergency['UNIQ'].isin(['40436'])]
patient3 = Emergency[Emergency['UNIQ'].isin(['859382'])]
patient4 = Emergency[Emergency['UNIQ'].isin(['1585831'])]
patient5 = Emergency[Emergency['UNIQ'].isin(['200760'])]
patient6 = Emergency[Emergency['UNIQ'].isin(['3692'])]
patient7 = Emergency[Emergency['UNIQ'].isin(['690326'])]

#R7 = df3[df3['Uniq'].isin(['690326'])]
#DX = Emergency[Emergency['DX1'].isin(['1585831'])]
#df = pd.read_csv("VTINP16_upd.txt", delimiter="\t")
#df.to_csv("VTINP16_upd.csv", encoding='utf-8', index=False)


#%% 3.1 
#filter columns with DX1-20
Emergency['DX1'].unique()
dx = Emergency.loc[:, Emergency.columns.str.startswith("DX")].astype(str)
#dx1 = Emergency.filter(regex='^DX',axis=1).astype(str)
print(dx)

#filter codes with T40|T41|T42|T43 and add new column in ED
#a = dx.DX1.str.startswith(('T40', 'T41', 'T42', 'T43'))
a = ['T40', 'T41', 'T42', 'T43']
flag = np.zeros(len(dx))
for i in range(len(dx)) :
    for j in range(dx.shape[1]):
        temp = dx.iloc[i,j]
        for k in a:
            if temp.startswith(k):
                flag[i] = 1

#Numbers of ED visits exactly have been diagnosed as drug user/abuser
flag = pd.DataFrame(flag)
sumflag = sum(flag[0])
print(sumflag)

#if dx.iloc[i,j].str.contains(('T40', 'T41', 'T42', 'T43')).any() :
#flag[i] = 1


#%% 3.2
#filter gender
Emergency['flag'] = flag
emg = Emergency[Emergency['sex'].isin(['1','2'])]

#2*2 table
table1=pd.crosstab(index = emg['sex'], columns = emg['flag'])
table1 = table1.reindex(columns=[1,0])
#table1 = table1.reindex([1,0], axis = 1)
table1.index = ['Male', 'Female']
table1.columns =['Drug User', 'Non-Drug User'] 
#table1 = table1.rename(columns={1:'Drug User', 0:'Non-Drug User'}, index={'1':'Male', '2':'Female'}) 
print(table1)
#fisher test: 1009/123149 > 1141/140553 that means male are likely to be drug users than female
oddsratio,pvalue = stats.fisher_exact(table1, alternative='greater')
print(pvalue)
print(oddsratio)


#%% 3.3
#Exact dollar amount for your identified patients
drugab = Emergency[Emergency['flag'] ==1]
sumcharge = drugab.CHRGS.astype(float).sum()
print(sumcharge)

#Of the three insurances in Question 2, what was share of each of the total payments?
medicare = drugab[drugab.PPAY.isin([1])]
medicare_sum = medicare.CHRGS.astype(float).sum()/sumcharge
medicaid = drugab[drugab.PPAY.isin([2])]
medicaid_sum = medicaid.CHRGS.astype(float).sum()/sumcharge
comm = drugab[drugab.PPAY.isin([6,7])]
comm_sum = comm.CHRGS.astype(float).sum()/sumcharge
print("Medicare, Medicaid, Comm's perc are:", medicare_sum,medicaid_sum,comm_sum)


#%% 3.4
#filter code start with T404|T4362 and add new column in ED
i = 0
j = 0
b = 'T404'
c = 'T4362'
#b = ['T404', 'T4362']
flag1 = np.zeros(len(dx))

for i in range(len(dx)):
    for j in range(dx.shape[1]):
        temp1 = dx.iloc[i,j]
        if temp1.startswith(b):
                flag1[i] = 1
        elif temp1.startswith(c):
                flag1[i] = 2

"""
#original
for i in range(len(dx)):
    for j in range(dx.shape[1]):
        temp1 = dx.iloc[i,j]
        for m in b:
            if temp1.startswith(m):
                flag1[i] = 1
flag1 = pd.DataFrame(flag1)
sumflag1 = int(sum(flag1[0]))
print(sumflag1)
"""

flag1 = pd.DataFrame(flag1)
sumflag1 = flag1[flag1[0] == 1]
sumflag2 = flag1[flag1[0] == 2]

Emergency['flag1'] = flag1
emg1 = Emergency[Emergency['flag1'].isin(['1','2'])]
T404 = emg1[emg1['flag1'] == 1]
T4362 = emg1[emg1['flag1'] == 2]

#emergency and urgent
emg_urgent = emg1[emg1['ATYPE'].isin(['1' , '2'])]

#Patient and their diagnosis code for ED
table2 = pd.DataFrame({'ICD-10 Codes':['T404xxx and T4362xxx', 'T404xxx and T4362xxx, ATYPE: Emergency and Urgent', 'T404xxx', 'T4362xxx'],
                       'Numbers of Patient':[len(sumflag1)+len(sumflag2), len(emg_urgent), len(T404), len(T4362)]}) 
print(table2)


#%% 3.5  
#extract columns with zipcode and DX1-20
drugab1 = drugab.iloc[:,3:29]
drugab1.columns
#drugab2 = drugab1.drop(['dstat', 'sex', 'PPAY', 'CHRGS'], axis = 1)
drugab2 = pd.concat(drugab1.iloc[:, l] for l in range(6, drugab1.shape[1]))

#filter codes with T40|T41|T42|T43
ziprank = drugab2.copy().to_frame().astype(str)
ziprank['TXTZIP'] = drugab['TXTZIP']
ziprank = ziprank[['TXTZIP', 0]]
ziprank = ziprank[ziprank[0].str.contains('T40|T41|T42|T43')]
ziprank.TXTZIP.unique()

#3 zip code regions with the highest numbers of drug use/abuse cases. 
top3_zip = ziprank.groupby('TXTZIP').count()
top3_zip.columns = ['Highest Numbers of Drug Users']
top3_zip = top3_zip.sort_values(by=['Highest Numbers of Drug Users'], ascending = False)
top3_zip = top3_zip.reset_index(level='TXTZIP', drop = False)
top3_zip.index = np.arange(1, len(top3_zip)+1)
print(top3_zip.head(3))

#age distirbution among top 3 zipcode
ziprank1 = ziprank.copy().astype(str)
ziprank1['Age'] = drugab1['intage']

age = ziprank1[ziprank1['TXTZIP'].isin(['054','057', '05701'])]
age = age.groupby(['TXTZIP', 'Age'])[0].count().to_frame().reset_index()
#age.TXTZIP.unique()
age.columns = ['TXTZIP', 'Age', 'Total Numbers']
#age = age.sort_values(by = ['TXTZIP', 'Age', 'Total Numbers'], ascending = [True, True, False])
age.index = np.arange(1, len(age)+1)
print(age)


#%%3.6
#10 most common diagnoses of drug use/abuse
#drugab1a = drugab.iloc[:,9:29]
drugab1.nunique()
#firstcolumnnum = list(set(drugab1.DX1))
drugab3 = pd.concat(drugab1.iloc[:,l] for l in range(6, drugab1.shape[1]))
coderank = drugab3.copy().to_frame().astype(str)
#series.str.startswith(tuple(a)).to_frame()
coderank['ICD-10 Codes'] = coderank[0]
coderank = coderank[coderank[0].str.contains('T40|T41|T42|T43')]
top10_code = coderank.groupby('ICD-10 Codes').count()
top10_code.columns = ['Numbers']
top10_code = top10_code.sort_values(by='Numbers', ascending = False)
top10_code = top10_code.reset_index(level='ICD-10 Codes', drop = False)
top10_code.index = np.arange(1, len(top10_code)+1)
print(top10_code.head(10))
