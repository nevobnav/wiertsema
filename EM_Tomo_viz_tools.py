# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 21:34:05 2019

@author: ericv
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import math
import os

def Read2DCSV(input_file):
    try:
        #read values
        df = pd.read_csv(str(input_file), delim_whitespace = True,skiprows = [0, 1], engine = 'python', index_col = False, header = None, skipinitialspace = True)
        #read header
        df2 = pd.read_csv(str(input_file), sep = '    ',skiprows = [0], engine = 'python', index_col = False, header = 0, skipinitialspace = True)
        
        #combine headers and values in one df
        cols = list(df2.columns.values)
        df.columns = cols
        #remove spaces from column names 
        df.columns = df.columns.str.replace(' ', '')
        return df
    except:
        output = "CSV file does not matches the standard 2D csv layout"
        return output


def Read3DCSV(input_file):
    try:
        #read values
        df = pd.read_csv(str(input_file),  delim_whitespace=True, skiprows = [0, 1], engine = 'python', index_col = False, header = None, skipinitialspace = True)
        #read header
        df2 = pd.read_csv(str(input_file), sep = '     ',skiprows = [0], engine = 'python', index_col = False, header = 0, skipinitialspace = True)
        
        #fix column names 
        cols = [col for col in df2.columns if 'Unnamed' not in col]
        df.columns = cols
        #remove spaces from column names
        df.columns = df.columns.str.replace(' ', '')
        return df
    except:
        output = "CSV file does not matches the standard 3D csv layout"
        return output


#reformat dataframe
def CreateMasterSheet3D(df):
    try:
        #add ID column
        df['Punt_ID'] = range(1, len(df) + 1)
        df['Punt_ID'] = 'Meetlocatie_' + df['Punt_ID'].astype(str)
        #create master sheet
        master_sheet = pd.DataFrame(columns = ['Punt_ID','X', 'Y', 'Topo', 'elev', 'EC'])
        for i in range(1, 9):
            elev = 'ZLayer' + str(i)
            ec = 'EcLayer' + str(i)
            temp = df[['Punt_ID','X', 'Y', 'Elev', str(elev), str(ec)]]
            temp.columns = ['Punt_ID','X', 'Y', 'Topo', 'elev', 'EC']
            master_sheet = pd.merge(master_sheet, temp, how = 'outer')        
        return master_sheet
    except:
        output = "CSV file does not matches the standard 3D csv layout"
        return output

#reformat dataframe
def CreateMasterSheet2D(df):
    try:
        #add ID column
        df['Punt_ID'] = range(1, len(df) + 1)
        df['Punt_ID'] = 'Meetlocatie_' + df['Punt_ID'].astype(str)
        #create master sheet
        master_sheet = pd.DataFrame(columns = ['Punt_ID','X', 'Y', 'Lat', 'Long', 'Topo', 'dist', 'elev', 'EC', 'rho'])
        for i in range(1, 27):        
            elev = 'elev' + str(i)
            ec = 'EC' + str(i)
            rho = 'rho' + str(i)   
            temp = df[['Punt_ID','X', 'Y', 'Lat', 'Long', 'Topo', 'dist', str(elev), str(ec), str(rho)]]
            temp.columns = ['Punt_ID','X', 'Y', 'Lat', 'Long', 'Topo', 'dist', 'elev', 'EC', 'rho']
            master_sheet = pd.merge(master_sheet, temp, how = 'outer')
        return master_sheet        
    except:
        output = "CSV file does not matches the standard 2D csv layout"
        return output


def GetLaagDikte(master_sheet):
    func = master_sheet.groupby("Punt_ID").apply(lambda x: abs(x['elev'] - x['elev'].shift(+1)))
    temp = pd.DataFrame(index = func.index.get_level_values(1))
    temp['Dikte'] = func.values
    master_sheet = pd.merge(master_sheet, temp, how = 'outer', left_index = True, right_index = True)
    master_sheet['Dikte'] = master_sheet['Dikte'].fillna(value = master_sheet['Topo'] - master_sheet['elev'])
    master_sheet.rename(columns = {'elev':'elev_onderkant'}, inplace = True)
    master_sheet['elev_bovenkant'] = master_sheet['elev_onderkant'] + master_sheet['Dikte']
    return master_sheet    

def ReduceData(master_sheet, ondergrens, bovengrens, resolutie, reduction_factor):
    #calculate change in EC over depth
    func = master_sheet.groupby("Punt_ID").apply(lambda x:abs(x['EC'] - x['EC'].shift(-1)))
    temp = pd.DataFrame(index = func.index.get_level_values(1))
    temp['EC_diff'] = func.values
    temp['EC_diff'] = temp['EC_diff'].fillna(value = temp['EC_diff'].shift(+1))
    master_sheet = pd.merge(master_sheet, temp, how = 'outer', left_index = True, right_index = True)
    
    #define grouping criterium (kan nog verbeterd worden)
    master_sheet['verwaarloosbaar'] = pd.Series((master_sheet['EC'] < ondergrens) | (master_sheet['EC'] > bovengrens) | (master_sheet['EC_diff'] < resolutie))
    
    #create groups                
    master_sheet['temp'] = np.where(master_sheet['verwaarloosbaar'] == False, 1, 0)
    func3 = master_sheet.groupby('Punt_ID').apply(lambda x:x['temp'].cumsum())
    temp = pd.DataFrame(index = func3.index.get_level_values(1))
    temp['groups'] = func3.values
    master_sheet = pd.merge(master_sheet, temp, how = 'outer', left_index = True, right_index = True)
    groups = master_sheet.groupby(['Punt_ID', 'groups'])
    
    #calculate avg values for aggregated data and put in new df
    simplified_df = pd.DataFrame(columns = ['Punt_ID','X', 'Y', 'Topo', 'elev_bovenkant', 'EC', 'EC_diff', 'Dikte'])
    simplified_df.Punt_ID = groups.Punt_ID.first()
    simplified_df.X = groups.X.max()
    simplified_df.Y = groups.Y.max()
    simplified_df.Topo = groups.Topo.max()
    simplified_df.elev_bovenkant = groups.elev_bovenkant.max()
    simplified_df.EC = groups.EC.mean()
    simplified_df.EC_diff = groups.EC_diff.mean()
    simplified_df.Dikte = groups.Dikte.sum()*-1
    
    #optional, reduce data with a defined factor
    decimal, integer = math.modf(reduction_factor)
    if integer >= 2:
        temp = pd.Series(simplified_df.index.get_level_values(0).drop_duplicates())
        temp = temp.unique()
        temp = temp[::int(integer)]
        simplified_df = (simplified_df.loc[simplified_df.Punt_ID.isin(temp)])
        if decimal > 0:
            temp = pd.Series(simplified_df.index.get_level_values(0).drop_duplicates())
            temp = temp.unique()
            temp = temp[::round(1/decimal)]
            simplified_df = simplified_df.drop(temp)
    elif reduction_factor < 2.0 and reduction_factor > 1.0:
        temp = pd.Series(simplified_df.index.get_level_values(0).drop_duplicates())
        temp = temp.unique()
        temp = temp[::round(1/decimal)]
        simplified_df = simplified_df.drop(temp)
    return simplified_df    

def CreateGeodf(master_sheet):
    #create geodataframe
    master_sheet['Coordinates'] = list(zip(master_sheet.X, master_sheet.Y))
    master_sheet['Coordinates'] = master_sheet['Coordinates'].apply(Point)
    #Mogelijk optie inbouwen om crs te kunnen kiezen
    gdf = gpd.GeoDataFrame(master_sheet, geometry = 'Coordinates', crs = {'init': 'epsg:32631'})
    #create ID column for filtering in qgis
    gdf['ID'] = range(0, len(gdf))
    return gdf

def WriteGDF2Shp(gdf, output_file):   
    #write files to disk
    gdf.to_file(driver = 'ESRI Shapefile', filename = output_file )
    
def Processing_2D(input_files, output_file, reduce, params):
    try:
        if len(input_files) > 1:
            for input_file in input_files:
                merged_df = pd.DataFrame()
                merged_df = merged_df.append(Read2DCSV(input_file))
            #test if reading csv files succeeded
            if isinstance(merged_df, str):
                output_msg = "CSV file does not matches the standard 2D csv layout"
                return output_msg 
            else:    
                df = CreateMasterSheet2D(merged_df)
                if isinstance(df, str):
                    output_msg = "CSV file does not matches the standard 2D csv layout"
                    return output_msg 
                else:
                    df = GetLaagDikte(df)
                    if reduce == True:
                        EC_min, EC_max, resolution, data_reduction_factor = params
                        df = ReduceData(df, EC_min, EC_max, resolution, data_reduction_factor)
                    gdf = CreateGeodf(df)
                    WriteGDF2Shp(gdf, output_file)
                    output_msg = "succes!"
        else:
            input_files = str(input_files[0])
            df = Read2DCSV(input_files)
            #test if reading csv files succeeded
            if isinstance(df, str):
                output_msg = "CSV file does not matches the standard 2D csv layout"
                return output_msg
            else:
                df = CreateMasterSheet2D(df)
                if isinstance(df, str):
                    output_msg = "CSV file does not matches the standard 2D csv layout"
                    return output_msg
                else:
                    df = GetLaagDikte(df)
                    if reduce == True:
                        EC_min, EC_max, resolution, data_reduction_factor = params
                        df = ReduceData(df, EC_min, EC_max, resolution, data_reduction_factor)
                    gdf = CreateGeodf(df)
                    WriteGDF2Shp(gdf, output_file)
                    output_msg = "succes!"
        return output_msg
    except:
        output_msg = "Encountered error, please review settings and try again. If this error remains contact Kaz or Eric"#, please send "+ os.path.dirname(RAW_files[0]) + "/log.txt " +" to kaz.vermeer@watermappers.com."
        return output_msg

def Processing_3D(input_files, output_file, reduce, params):
    try:
        if len(input_files) > 1:
            for input_file in input_files:
                merged_df = pd.DataFrame()
                merged_df = merged_df.append(Read3DCSV(input_file))
            #test if reading csv files succeeded 
            if isinstance(merged_df, str):
                output_msg = "CSV file does not matches the standard 3D csv layout"
                return output_msg
            else:
                df = CreateMasterSheet3D(merged_df)
                if isinstance(df, str):
                    output_msg = "CSV file does not matches the standard 3D csv layout"
                    return output_msg
                else:
                    df = GetLaagDikte(df)
                    if reduce == True:
                        EC_min, EC_max, resolution, data_reduction_factor = params
                        df = ReduceData(df, EC_min, EC_max, resolution, data_reduction_factor)
                    gdf = CreateGeodf(df)
                    WriteGDF2Shp(gdf, output_file)
                    output_msg = "succes!"
        else:
            input_files = str(input_files[0])
            df = Read3DCSV(input_files)            
            #test if reading csv files succeeded            
            if isinstance(df, str):
                output_msg = "CSV file does not matches the standard 3D csv layout"
                return output_msg
            else:     
                df = CreateMasterSheet3D(df)
                if isinstance(df, str):
                        output_msg = "CSV file does not matches the standard 3D csv layout"
                        return output_msg
                else:

                    df = GetLaagDikte(df)
                    if reduce == True:
                        EC_min, EC_max, resolution, data_reduction_factor = params
                        df = ReduceData(df, EC_min, EC_max, resolution, data_reduction_factor)
                    gdf = CreateGeodf(df)
                    WriteGDF2Shp(gdf, output_file)
                    output_msg = "succes!"
        return output_msg
    except:
        output_msg = "Encountered error, please review settings and try again. If this error remains contact Kaz or Eric"#, please send "+ os.path.dirname(RAW_files[0]) + "/log.txt " +" to kaz.vermeer@watermappers.com."
        return output_msg
