# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 19:19:36 2022

@author: Becca
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


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
    df2.iloc[:, 1:] = df2.iloc[:, 1:].apply(lambda x: x * 1)#000)
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


def fillNull(df1_melted,df2):
    """df1_melted: fed data melted to match zillow
    df2 is zillow data
    Fills the null values with the $ value from the fed data"""
    # df1 = fedData()
    df2 = findMissing(df2)

    # Iterate over the rows in missing
    for index, row in df2.iterrows():
        # Find the corresponding row in df1 based on the County and Year columns
        df1_row = df1_melted.loc[(df1_melted["County"] == row["County"]) & (df1_melted["Year"] == row["Year"])]
        # Check if the df1_row dataframe is empty
        if df1_row.empty:
            continue
            # # Update the Value column in df2 with the default value if df1_row is empty
            # df2.at[index, "Value"] = 0
        else:
            # Update the Value column in df2 with the corresponding value in df1
            df2.at[index, "Value"] = df1_row["Value"].values[0]
           
    return df2

def fedEq(df_z, df_f):
    """ 
    creates a coef value which is calculated from the mean of zillow data and the fed Index at the same year,
    creating a linear slope to multiply fed index by to change it to from a value index to $USD
    
    """
    df_f = df_f.melt(id_vars=["County"], value_vars=df_f.columns[1:], var_name="Year", value_name="Value")
    #creating a column of coefficients where each one is 1000 to change 100's to 100,000 value if it remains the same
    df_f['coef'] = 1000
    county_list = df_f.County.unique().tolist()
    for parish in county_list:
        ind = df_z[df_z.County == parish].Value.first_valid_index()
        if ind is None:# or not isinstance(ind, (int, float)):
            continue
        year = df_z.iloc[ind].Year
        #mean value of the parish and year with first valid non null value from zillow data
        dy2 = df_z.loc[(df_z.County == parish) & (df_z.Year == year)].Value.mean()
        #hvi number for that same year
        dy1 = df_f.loc[(df_f.County == parish) & (df_f.Year == year)].Value
        if dy1.shape[0] == 0:
            continue
        dy1 = dy1.iloc[0]
        if pd.isna(dy2) or pd.isna(dy1):
            continue
        m = dy2 / dy1
        df_f.loc[df_f.County == parish, 'coef'] = m
        
    df_f['Value'] = df_f['Value'] * df_f['coef']
    return df_f


def main():
    oldZillow = zillowData()
    oldFed = fedData()

    fed = fedEq(oldZillow,oldFed)
    #update
    missingZillow = fillNull(fed,oldZillow)
    zillow = oldZillow.copy()
    zillow.update(missingZillow['Value'])

    # #cound not get data for these parish's so they are removed
    remove = ['Tangipahoa Parish', 'Ascension Parish','East Feliciana Parish'] 
    #keep the parishes that are not these
    zillow = zillow[~zillow.County.isin(remove)]

    #zillow['Value'] = zillow.groupby(['County'])['Value'].apply(lambda x: x.bfill())

    return zillow
#print(main())

unaffected = ["Ascension Parish", "East Baton Rouge Parish", "East Feliciana Parish", "Iberville Parish", "Livingston Parish", "Pointe Coupee Parish", "St. Helena Parish", "West Baton Rouge Parish", "West Feliciana Parish","Caddo Parish"]
affected = ["Washington Parish", "Orleans Parish", "St. Bernard Parish", "St. Charles Parish", "Jefferson Parish", "Plaquemines Parish", "St. James Parish", "St. John the Baptist Parish", "St. Tammany Parish", "Tangipahoa Parish"]

df_plot = main()

df_plot = df_plot.groupby(by=['County','Year'], dropna=False).mean()
df_plot = df_plot.drop(columns=['SizeRank']).reset_index()

#split up into affected and unaffected areas
df_unaffected = df_plot.loc[~df_plot['County'].isin(affected)]
df_affected = df_plot.loc[~df_plot['County'].isin(unaffected)]

#plot of Zillow Median Home Value
fig, ax = plt.subplots(figsize=(30,10))
ax.set(xlabel='Years', ylabel='Home Value in $USD',xlim=(2000,2020.1))
ax.set_title( label='Home Value of Counties over Time', fontsize=30)
plt.axvline(x=2005,color = 'm',label = 'Katrina Hit')
plt.axvline(x=2008,color = 'r',label = "'08 Recession")
sns.lineplot(x='Year',y='Value',data = df_plot, hue = 'County', palette="Paired", ax=ax)
plt.legend(bbox_to_anchor=(1.005, 1), loc='upper left', borderaxespad=0., fontsize=17)
   
