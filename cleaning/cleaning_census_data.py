# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 15:15:09 2022

@author: Becca
"""

import pandas as pd
import glob

keyCounty = ["Washington Parish", "Orleans Parish", "St. Bernard Parish", "St. Charles Parish", "Jefferson Parish", "Plaquemines Parish", "St. James Parish", "St. John the Baptist Parish", "St. Tammany Parish", "Tangipahoa Parish", "Ascension Parish", "East Baton Rouge Parish", "East Feliciana Parish", "Iberville Parish", "Livingston Parish", "Pointe Coupee Parish", "St. Helena Parish", "West Baton Rouge Parish", "West Feliciana Parish", "Caddo Parish"]
unaffectedCounty = ["Ascension Parish", "East Baton Rouge Parish", "East Feliciana Parish", "Iberville Parish", "Livingston Parish", "Pointe Coupee Parish", "St. Helena Parish", "West Baton Rouge Parish", "West Feliciana Parish","Caddo Parish"]
affectedCounty = ["Washington Parish", "Orleans Parish", "St. Bernard Parish", "St. Charles Parish", "Jefferson Parish", "Plaquemines Parish", "St. James Parish", "St. John the Baptist Parish", "St. Tammany Parish", "Tangipahoa Parish"]

def cleanCensusPoverty():
    #read all the .dat files in the current folder
    files = glob.glob("*.dat")
    df_list = []
    
    headerNames = ['FIPS State Code','County FIPS Code', 'Poverty Estimate All Ages','90% CI Lower Bound','90% CI Upper Bound','Poverty Percent All Ages','90% CI Lower Bound.1', '90% CI Upper Bound.1','Poverty Estimate, Age 0-17', '90% CI Lower Bound.2','90% CI Upper Bound.2', 'Percent Poverty Estimate, Age 0-17', '90% CI Lower Bound.3','90% CI Upper Bound.3','Poverty Estimate, Age 5-17', '90% CI Lower Bound.4','90% CI Upper Bound.4','Percent Poverty Estimate, Age 5-17', '90% CI Lower Bound.5','90% CI Upper Bound.5','Median Household Income','90% CI Lower Bound.mh', '90% CI Upper Bound.mh','County Name','Postal Code','Tag','Creation Date']
    dropNames = ['FIPS State Code','County FIPS Code','90% CI Lower Bound','90% CI Upper Bound','90% CI Lower Bound.1', '90% CI Upper Bound.1','Poverty Estimate, Age 0-17', '90% CI Lower Bound.2','90% CI Upper Bound.2', 'Percent Poverty Estimate, Age 0-17', '90% CI Lower Bound.3','90% CI Upper Bound.3','Poverty Estimate, Age 5-17', '90% CI Lower Bound.4','90% CI Upper Bound.4','Percent Poverty Estimate, Age 5-17', '90% CI Lower Bound.5','90% CI Upper Bound.5','90% CI Lower Bound.mh', '90% CI Upper Bound.mh','Postal Code','Tag','Creation Date']
    # loop through the list of files
    for file in files:
        # .dat files are fixed with format, skip first row since it is state overall and has excess data we dont need
        df = pd.read_fwf(file, header=None, names = headerNames,skiprows=1, engine='python', encoding='latin1')
        df.drop(columns= dropNames , inplace=True)
        #only the important Counties
        df = df.loc[df['County Name'].isin(keyCounty)]
        #add df to list
        df_list.append(df)
        
        
    return df_list

def splitDF(df):
    #splitting the df into two new df's affected and unaffected 
    df_affected = df.loc[df['County'].isin(affectedCounty)]
    df_unaffected = df.loc[df['County'].isin(unaffectedCounty)]
    return df_affected, df_unaffected

def combineTotal(df_list):
    # Set the initial dataframe to merge
    result = df_list[0]
    year = 2000
    # Loop through the remaining dataframes and merge them one by one
    for i in range(1, len(df_list)):
        old_year = '_'+ str(year)
        year += 1
        new_year = '_'+ str(year)
        result = pd.merge(left=result, right=df_list[i], on='County', suffixes=[old_year, new_year])
    column_names = {'County Name':'RegionName','Poverty Estimate All Ages':'Poverty Estimate All Ages_2020','Poverty Percent All Ages':'Poverty Percent All Ages_2020', 'Median Household Income':'Median Household Income_2020'}
    result = result.rename(columns = column_names)
    return result

def cleanCensusPopulation():
    #clean Population df
    df = pd.read_csv('Population_FullClean.csv')
    df = df.loc[df['CTYNAME'].isin(keyCounty)]
    #drop 2000,2010,2020 and rename CITYNAME, CENSUS20XXPOP to 20XX
    drops = ['2000','2010','2020']
    df = df.drop(drops,axis=1)
    new_col = {'CTYNAME':'County', 'CENSUS2000POP':2000,'CENSUS2010POP':2010,'CENSUS2020POP':2020}
    df = df.rename(columns = new_col)
    df.to_csv('Population_FullClean2.csv', index=False)
    return df
    
def cleanedCombinedFrames(df_list):
    #starting year
    n = 2000
    #create new df's
    df_median_income =  pd.DataFrame()
    df_poverty_percent = pd.DataFrame()
    df_poverty = pd.DataFrame()
    #make county column
    df_median_income['County']= df_poverty_percent['County'] = df_poverty['County'] = df_list[0]['County Name']
    #seperate df's
    for df in df_list:
        year = str(n)
        df_poverty[year] = df['Poverty Estimate All Ages']
        df_poverty_percent[year] = df['Poverty Percent All Ages']
        df_median_income[year] = df['Median Household Income']
        n += 1
        
    df_clean_list = [df_poverty,df_poverty_percent,df_median_income]
    df_poverty.to_csv('Poverty_FullClean.csv', index=False)
    df_poverty_percent.to_csv('Poverty_Percent_FullClean.csv', index=False)
    df_median_income.to_csv('Median_Income_FullClean.csv', index=False)
    return df_clean_list
        

def main():
    #intial df_list
    df_list = cleanCensusPoverty()
    #clean all the lists
    clean_df_list = cleanedCombinedFrames(df_list)
    big_df = combineTotal(clean_df_list)
    #seperate affected and unaffected
    final = splitDF(big_df)
    df_affected = final[0]
    df_unaffected = final[1]
    
main()