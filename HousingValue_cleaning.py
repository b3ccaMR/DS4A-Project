# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 19:19:36 2022

@author: Becca
"""

import pandas as pd

def fedData():
    df = pd.read_excel('Stlouisfedcleaned.xlsx')
    #cleaning
    df.drop(columns= ['Unnamed: 0'] , inplace=True)
    column_names = {'Batonrouge Parish':'East Baton Rouge Parish','New Orleans Metairie Parish':'Orleans Parish'}
    df = df.rename(columns = column_names)
    df['Date'] = df.Date.dt.year
    
    #Transpose the data so that the dframe has a header of years and 
    df2 = df.copy()
    df2 = df2.reset_index(drop=True).transpose().reset_index()
    df2.columns = df2.iloc[0]
    df2 = df2.iloc[1:]
    df2 = df2.rename(columns={"Date": "County"})
    df2 = df2.reset_index(drop = True)
    df2.iloc[:, 1:] = df2.iloc[:, 1:].apply(lambda x: x * 1000)
    #dropping Median House Income because other dataframes have this
    df2 = df2.drop(df.index[2])
    return df2

def zillowData():
    """@author: Eduardo
    
    """
    df = pd.read_csv("zillow_all_homes.csv")
    #drop useless columns: RegionID, RegionType, StateName, State, Metro, StateCodeFIPS, MunicipalCodeFIPS, tier
    df.drop(columns=["RegionID", "RegionType", "StateName", "State", "Metro", "StateCodeFIPS", "MunicipalCodeFIPS", "tier"], inplace=True)
    keyCounty = ["Washington Parish", "Orleans Parish", "St. Bernard Parish", "St. Charles Parish", "Jefferson Parish", "Plaquemines Parish", "St. James Parish", "St. John the Baptist Parish", "St. Tammany Parish", "Tangipahoa Parish", "Ascension Parish", "East Baton Rouge Parish", "East Feliciana Parish", "Iberville Parish", "Livingston Parish", "Pointe Coupee Parish", "St. Helena Parish", "West Baton Rouge Parish", "West Feliciana Parish", "Caddo Parish"]
    #keyCounty = pd.Series(keyCounty).str.replace("St.", "Saint", regex = False).tolist()
    
    df = df[df["RegionName"].isin(keyCounty)]
    df.rename(columns = {'RegionName':'County', 'Date':'Year'}, inplace = True)
    
    df["Year"] = pd.DatetimeIndex(df['Year']).year.astype(int)
    
    return df

def findMissing(df):
    #all the parish
    mask = df['Value'].isnull()
    missing = df[mask]
    #missing_parish_list = missing.County.unique()
    return missing

def main():
    fed = fedData()
    zillow = zillowData()
    missing_parish_df = findMissing(zillow)