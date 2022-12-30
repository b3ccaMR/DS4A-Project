# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 19:19:36 2022

@author: Becca
"""

import pandas as pd

def fedData():
    """Federal HVI Data 100 = $100,000
    Cleaning data more and turning it from index values into $"""
    df = pd.read_excel('Stlouisfedcleaned.xlsx')
    #cleaning
    df.drop(columns= ['Unnamed: 0'] , inplace=True)
    column_names = {'West Batonrouge Parish':'West Baton Rouge Parish','Batonrouge Parish':'East Baton Rouge Parish','New Orleans Metairie Parish':'Orleans Parish'}
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
    
    df = df[df["RegionName"].isin(keyCounty)]
    df.rename(columns = {'RegionName':'County', 'Date':'Year'}, inplace = True)
    
    df["Year"] = pd.DatetimeIndex(df['Year']).year.astype(int)
    
    return df

def findMissing(df):
    """creates a dataframe of all null values"""
    #all the parish
    mask = df['Value'].isnull()
    missing = df[mask]
    #missing_parish_list = missing.County.unique()
    return missing


def fillNull():
    """Fills the null values with the $ value from the fed data"""
    df1 = fedData()
    df2 = findMissing(zillowData())
    
    # Use the melt function to reshape fed
    df1_melted = df1.melt(id_vars=["County"], value_vars=df1.columns[1:], var_name="Year", value_name="Value")
    
    # Iterate over the rows in missing
    for index, row in df2.iterrows():
        # Find the corresponding row in df1 based on the County and Year columns
        df1_row = df1_melted.loc[(df1_melted["County"] == row["County"]) & (df1_melted["Year"] == row["Year"])]
        # Check if the df1_row dataframe is empty
        if df1_row.empty:
            # Update the Value column in df2 with the default value if df1_row is empty
            df2.at[index, "Value"] = 0
        else:
            # Update the Value column in df2 with the corresponding value in df1
            df2.at[index, "Value"] = df1_row["Value"].values[0]
            
    finalMissing = df2[df2['Value'] == 0]
    finalMissing = finalMissing.County.unique().to_list()
    """
    ['Tangipahoa Parish', 'Ascension Parish', 'West Baton Rouge Parish','East Feliciana Parish'] 
    are missing from fedData, West Baton Rouge should not be missing???
    We can't delete West Baton Rouge because this is an important column'
    """
    
    return df2


def main():
    fed = fedData()
    zillow = zillowData()
    missing_parish_df = findMissing(zillow)
    
    """
    What to do:
    fillNull- need to fix the zeros issue from missing data (delete Tangipahoa and Ascension Parish
    and fix the errors.
    Errors- For some reason West Baton Rouge is not being filled in even though it is in fedData
    we need to keep west baton rouge this is an important column.... 
    
    Zillow- need to replace fillNull into the null values in the zillow data
    """
#main()