# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 21:34:05 2019

@author: ericv
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point,Polygon
import math
import os
from collections import OrderedDict
pd.options.mode.chained_assignment = None


crs = {'init': 'epsg:32631'}

#defining an output schema is a nice addition to the tool but for now it is too much work because there are differences between 2D, 3D and simplified df's.
# =============================================================================
# output_schema = {'properties': OrderedDict([('Punt_ID', 'str:80'),
#               ('X', 'float:24.6'),
#               ('Y', 'float:24.6'),
#               ('Topo', 'float:24.2'),
#               ('dist', 'float:24.2'),
#               ('elev_onder', 'float:24.2'),
#               ('EC', 'float:24.2'),
#               ('rho', 'float:24.2'),
#               ('Dikte', 'float:24.2'),
#               ('elev_boven', 'float:24.2'),
#               ('ID', 'int:18')]),
#                 'geometry': 'Point'}
# =============================================================================

def read_shapefile(input_file):
    try:
        gdf = gpd.read_file(input_file)
    except:
        output = "An error occurred whilst reading the shapefile"
        return output
    return gdf

def filter_data(criteria, gdf):
    filter_result_list = []
    ec_greater = -9999
    ec_smaller = 99999
    elev_greater = -9999
    elev_smaller = 99999
    for criterium in criteria:
        if '' in criterium:
            for i, crit in enumerate(criterium):
                if (i == 0) and (crit != ''):
                    try:
                        ec_greater = float(crit)
                    except:
                        output = "Input is not a valid number, please use numbers with . as decimal separator"
                        return output
                if (i == 1) and (crit != ''):
                    try:
                        ec_smaller = float(crit)
                    except:
                        output = "Input is not a valid number, please use numbers with . as decimal separator"
                        return output
                if (i == 2) and (crit != ''):
                    try:
                        elev_greater = float(crit)
                    except:
                        output = "Input is not a valid number, please use numbers with . as decimal separator"
                        return output
                if (i == 3) and (crit != ''):
                    try:
                        elev_smaller = float(crit)
                    except:
                        output = "Input is not a valid number, please use numbers with . as decimal separator"
                        return output
        else:
            ec_greater, ec_smaller, elev_greater, elev_smaller = criterium
            ec_greater = float(ec_greater)
            ec_smaller = float(ec_smaller)
            elev_greater = float(elev_greater)
            elev_smaller = float(elev_smaller)
        try:
            subset = gdf[(gdf['EC'] > ec_greater) & (gdf['EC'] < ec_smaller) & (gdf['elev_boven'] > elev_greater) & (gdf['elev_boven'] < elev_smaller)]
        except:
            output = "EC or elev column not present or renamed, please make sure the shapefile matches the right format"
            return output
        filter_result_list.append(subset)
        ec_greater = -9999
        ec_smaller = 99999
        elev_greater = -9999
        elev_smaller = 99999
    filtered_df = gpd.GeoDataFrame(pd.concat(filter_result_list), crs = crs)
    filtered_df = filtered_df[filtered_df.index.duplicated(keep = 'first') == False]
    if len(filtered_df) < 1:
        output = "no records match specified selection criteria"
        return output
    return filtered_df

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
        master_sheet = master_sheet.drop(['Lat', 'Long'], axis = 1)
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
    master_sheet.rename(columns = {'elev':'elev_onder'}, inplace = True)
    master_sheet['elev_boven'] = master_sheet['elev_onder'] + master_sheet['Dikte']
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
    simplified_df = pd.DataFrame(columns = ['Punt_ID','X', 'Y', 'Topo', 'elev_boven', 'EC', 'EC_diff', 'Dikte'])
    simplified_df.Punt_ID = groups.Punt_ID.first()
    simplified_df.X = groups.X.max()
    simplified_df.Y = groups.Y.max()
    simplified_df.Topo = groups.Topo.max()
    simplified_df.elev_boven = groups.elev_boven.max()
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

def CreateGeodf(master_sheet, crs = crs):
    #create geodataframe
    master_sheet['Coordinates'] = list(zip(master_sheet.X, master_sheet.Y))
    master_sheet['Coordinates'] = master_sheet['Coordinates'].apply(Point)
    #Mogelijk optie inbouwen om crs te kunnen kiezen
    gdf = gpd.GeoDataFrame(master_sheet, geometry = 'Coordinates', crs = crs)
    #create ID column for filtering in qgis
    gdf['ID'] = range(0, len(gdf))
    return gdf

def WriteGDF2Shp(gdf, output_file, crs = crs):
    #write files to disk
    #extra check:
    if 'Lat' in gdf.columns:
        gdf = gdf.drop(['Lat', 'Long'], axis = 1)
    gdf.crs = crs
    gdf.to_file(driver = 'ESRI Shapefile', filename = output_file)

def Processing_2D(input_files, output_file, reduce, params):
    try:
        if len(input_files) > 1:
            merged_df = pd.DataFrame()
            for input_file in input_files:
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
                    output_msg = "Succes!"
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
                    output_msg = "Succes!"
        return output_msg
    except:
        output_msg = "Encountered error, please review settings and try again. If this error remains contact Kaz or Eric"#, please send "+ os.path.dirname(RAW_files[0]) + "/log.txt " +" to kaz.vermeer@watermappers.com."
        return output_msg

def Processing_3D(input_files, output_file, reduce, params):
    try:
        if len(input_files) > 1:
            merged_df = pd.DataFrame()
            for input_file in input_files:
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
                    output_msg = "Succes!"
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
                    output_msg = "Succes!"
        return output_msg
    except:
        output_msg = "Encountered error, please review settings and try again. If this error remains contact Kaz or Eric"#, please send "+ os.path.dirname(RAW_files[0]) + "/log.txt " +" to kaz.vermeer@watermappers.com."
        return output_msg

def create_filtered_layer(input_file2, output_file2, criteria):
    gdf = read_shapefile(input_file2)
    if isinstance(gdf, str):
        output_msg = 'Error reading shapefile'
        return output_msg
    else:
        filtered_df = filter_data(criteria, gdf)
    if isinstance(filtered_df, str):
        if filtered_df != "no records match specified selection criteria":
            output_msg = 'Error with filtering shapefile based on selection criteria'
        else:
            output_msg = filtered_df
        return output_msg
    else:
        try:
            WriteGDF2Shp(filtered_df, output_file2)
            output_msg = "Succes!"
            return  output_msg
        except:
            output_msg = 'Error writing shapefile to disk'
            return output_msg






def create_cross_section(window,input_file, output_folder, elevations, grid_size = 0):
    #Read shapefile to gdf
    gdf = read_shapefile(input_file)
    if isinstance(gdf,str):
        output_msg = "Error reading shapefile"
        return output_msg

    # try:
    #set no data value
    no_data_value = float('Nan')

    #Register number of shapefiles that turn out empty
    results = []

    #get original filename for use in saving output
    original_filename = os.path.basename(os.path.splitext(input_file)[0])

    #Determine the top and bottom elevation
<<<<<<< HEAD


=======
    gdf['top'] = gdf.elev_boven
    gdf['bottom'] = gdf.elev_boven+gdf.Dikte
    elevations = np.unique(elevations)
>>>>>>> 66bd33f91f8e50674526a238a229c37ed274e0c4
    for elevation in elevations:
        window.status_msg.set('Creating XY grid at {}m...'.format(str(elevation)))
        #Filter for the right depth and create new GDF with 'Meetlocatie' ID as index
        gdf_filtered = gdf[(gdf.elev_boven> elevation) & (gdf.elev_onder <= elevation)]
        if len(gdf_filtered) == 0:
            print('broken out at '+str(elevation))
            results.append({'elevation':elevation,'succes':'No values found'})
            continue
        gdf_filtered['Punt_ID_num'] = gdf_filtered.Punt_ID.apply(lambda x: int(x[x.find('_')+1::]))
        gdf_filtered.sort_values('Punt_ID_num', inplace=True)
        gdf_filtered.set_index('Punt_ID_num', drop=True, inplace=True)
        gdf_filtered.drop('Punt_ID',1,inplace=True)

        #Render grid at automatically rendered grid size
        grid = create_grid_from_gdf(gdf_filtered, grid_size = grid_size)
        #Join raster with measurement points to find out which points are present in every raster element
        joined_raster_data = gpd.sjoin(grid,gdf_filtered, how="left")

        #Create GPD
        grid_data = gpd.GeoDataFrame()
        #Fill columns of grid_data gpd
        grid_data['geometry'] = grid.geometry
        #Create list of measurement point IDs present in each raster element
        grid_data['IDs'] = joined_raster_data.groupby(joined_raster_data.index).index_right.apply(list)
        grid_data['has_data'] = grid_data.IDs.apply(lambda x: x[0] == x[0])
        grid_data['EC'] = no_data_value #Set EC data to default no-data value
        grid_data['elevation'] = elevation
        grid_data.crs = gdf_filtered.crs #Pass over CRS from gdf_filtered

        active_grid_data = grid_data[grid_data.has_data]

        #Determine EC value for each grid element
        for ii in range(1,len(active_grid_data)):
            grid_element_data = active_grid_data.iloc[ii]  #select data from this specific grid element
            if grid_element_data.has_data:
                id_list = grid_element_data.IDs
                #Get all measurements within the square
                this_square_df =gdf_filtered[gdf_filtered.index.isin(id_list)]
                #determine location of centroid of grid element
                centroid = grid_element_data.geometry.centroid
                #Determine distance (and inverse) to centroid
                this_square_df['dist_to_centroid'] = this_square_df.geometry.distance(centroid)
                this_square_df['closeness'] = 1/this_square_df.dist_to_centroid
                #take weighted average of EC with respect to closeness to centroid.
                #The closer the higher its weighted in a linear fashion.
                this_square_df['weighted_EC'] = this_square_df.EC * this_square_df.closeness
                weighted_avg_EC = this_square_df.weighted_EC.sum()/this_square_df.closeness.sum()
                #Update EC value in grid_data gpd
                active_grid_data.loc[active_grid_data.index[ii],'EC'] = weighted_avg_EC

        #Generate output
        output = active_grid_data[['geometry','EC','elevation']] #Only create output if the element has data.
        output.crs = gdf_filtered.crs   #give correct CRS
        elevation_cm_string= str(abs(int(elevation*100)))
        filename = original_filename + '_XYgrid_' + elevation_cm_string + '.shp'
        output_file = os.path.join(output_folder, filename)
        window.status_msg.set('Writing XY grid at {}m...)'.format(str(elevation)))
        output.to_file(driver = 'ESRI Shapefile', filename = output_file) #Create shapefile
        results.append({'elevation':elevation,'succes':'Executed succesfully'})

    output_msg = 'Finished! Results:\n'


    for i in range(len(elevations)):
        dict = results[i]
        line  = "Elevation {}m: {} \n".format(dict['elevation'], str(dict['succes']))
        output_msg = output_msg+line

    # output_msg = "Succesfully generated {} out of {} shape files".format(succes,len(elevations))

    # except:
    #     output_msg = "Error occured whilst generating XY grids."

    return output_msg


def create_grid_from_gdf(gdf, grid_size = 0):
    gdf['dist_to_next'] = gdf.distance(gdf.shift(1))
    #Assumed measurement distances are quite constant, automatically detect grid size
    #In case where function is called with specified grid_size, that number is used
    base_grid_size = int(gdf.dist_to_next.median())+1 #+1 to make sure our grid is slightly larger than the true spacing between measurements
    if grid_size == 0:
        grid_size = base_grid_size

    grid_size = max(grid_size, np.ceil(base_grid_size/10))
    grid_size = min(grid_size, np.ceil(base_grid_size * 10))
    grid_size = int(grid_size)

    #Create the grid
    xmin,ymin,xmax,ymax = gdf.geometry.total_bounds

    #Assuming a grid of squares
    length = grid_size
    wide = grid_size

    cols = list(range(int(np.floor(xmin)-wide), int(np.ceil(xmax)+wide), wide))
    rows = list(range(int(np.floor(ymin)-length), int(np.ceil(ymax)+length), length))
    rows.reverse()

    #create Polygon shapes for each grid element
    polygons = []
    for x in cols:
        for y in rows:
            polygons.append( Polygon([(x,y), (x+wide, y), (x+wide, y-length), (x, y-length)]) )

    #Cobine grid Polygons to single gdf
    grid = gpd.GeoDataFrame({'geometry':polygons})
    grid.crs = gdf.crs  #Copy CRS settings
    #Give grid half an element offset to make sure (the initial) points lay in the center.
    grid.geometry = grid.geometry.translate(xoff=int(grid_size/2), yoff=int(grid_size/2))
    return grid
