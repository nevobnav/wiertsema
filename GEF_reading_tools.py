import pandas as pd
import geopandas as gpd
import numpy as np
import math
import os
from shapely.geometry import Point

pd.options.mode.chained_assignment = None

def GEF_to_gdf(GEF):
    #Read lines
    with open(GEF, 'r', encoding='utf-8',errors='ignore') as fdata:
        contents = fdata.readlines()

    #Get info from GEF file metadata
    columnsep = [s for s in contents if "#COLUMNSEPARATOR" in s][0].split(' ')[1][0]
    XYID = [s for s in contents if "#XYID" in s][0].split(' ')
    ZID = [s for s in contents if "#ZID" in s][0].split(' ')
    x = float(XYID[2][:-1])
    y = float(XYID[3][:-1])
    AHN_height = float(ZID[2][:-1])

    test_ID = [s for s in contents if "#TESTID" in s][0].split('=')[1][1:-1]
    EOH_line = [s for s in contents if "#EOH=" in s] #Last line before data starts
    start_line = contents.index(EOH_line[0])+1#line where data starts

    #Create dataframe from GEF file

    df = pd.DataFrame(x.split(columnsep) for x in contents[start_line::])
    #Drop last column, which only holds line seperators
    df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)


    #Set column names
    col_info = [s for s in contents if "#COLUMNINFO= " in s]
    col_void_info = [s for s in contents if "COLUMNVOID= " in s]
    col_void = float(col_void_info[0].split(',')[1])#assuming column voids are always constant

    cols = []
    for info in col_info:
        info_split = info.split(',')
        unit = info_split[1].strip()
        quantity = info_split[2].strip()
        col_name = quantity+' [{}]'.format(unit)
        cols.append(col_name)

    df.columns = cols

    #Make all values numeric, instead of strings
    df = df[cols].apply(pd.to_numeric, errors='coerce')

    #Remove void values and replace by nans
    df = df.replace(col_void, float('nan'))

    df.dropna(how='all',subset=['Gecorrigeerde conusweerstand [MPa]'],inplace=True)

    #Add test_ID column (can be used later for grouping purposes on measurement location)
    df['TESTID'] = test_ID

    #Add thickness based on Sondeerlengte
    #This should be moved one further down, such that thickness is with respec to next layer instead of previous layer.
    df['Dikte [m]']=df['Sondeerlengte [m]'].diff(1)


    #Get AHN height of sondeersection bottom
    df['AHN'] = AHN_height - df['Gecorrigeerde diepte [m]']


    #Convert to GeoDataFrame and add geometry
    gdf = gpd.GeoDataFrame(df)
    gdf.crs = {'init': 'epsg:28992'}
    gdf['geometry']= Point(x,y)

    return gdf


def reduce_gdf (gdf, no_of_buckets):
    initial_data_length = len(gdf)

    data_types = ['Elektrische geleidbaarheid [S/m]','Gecorrigeerde conusweerstand [MPa]','Plaatselijke wrijving [MPa]']
    quantiles = np.linspace(0,1,no_of_buckets+1)
    grouped_gdfs = {}

    for data_type in data_types:

        specific_gdf = gdf[['Sondeerlengte [m]',data_type,'Dikte [m]','AHN','geometry']]
        bin_averages = []
        bins = specific_gdf[data_type].quantile(quantiles)
        bins = bins.values

        for x in range(1,no_of_buckets+1):
            if x == 0:
                values = specific_gdf[specific_gdf[data_type]<bins[x]]
                bin_averages.append(values[data_type].mean())
            else:
                values = specific_gdf[((specific_gdf[data_type]>bins[x-1]) & (specific_gdf[data_type]<bins[x]))]
                bin_averages.append(values[data_type].mean())

        labels = bin_averages

        specific_gdf['bins'] = pd.cut(specific_gdf[data_type], bins=bins, labels=labels)
        specific_gdf['bin_steps']=specific_gdf.bins.diff(1)
        specific_gdf['group_ID'] = 0
        specific_gdf['group_ID'][specific_gdf['bin_steps']!=0]=1
        specific_gdf['group_ID'] = specific_gdf['group_ID'].cumsum()


        grouped_specific_gdf = specific_gdf.groupby('group_ID').agg({data_type:'mean',
                                       'Sondeerlengte [m]':'max',
                                       'Dikte [m]':'sum',
                                       'AHN': 'min',
                                       'geometry':'first'})

        grouped_specific_gdf.dropna(how='all',subset=[data_type],inplace=True)

        grouped_specific_gdf['Dikte [m]'] = grouped_specific_gdf['Dikte [m]']*-1
        grouped_specific_gdf['Dikte [m]'] = grouped_specific_gdf['Dikte [m]'].shift(-1)
        grouped_gdfs[data_type]=grouped_specific_gdf[['Sondeerlengte [m]',data_type,'Dikte [m]','AHN','geometry']]

        final_data_length = len(grouped_specific_gdf)

    return grouped_gdfs

def process_GEFs(input_folder, output_file, no_of_buckets = 5):
    try:
        # Gather file list
        file_list = os.listdir(input_folder)
        valid_files = [x for x in file_list if x.endswith('.gef')]

        # Initiate geopandas dataframe (gdf)
        gdf = gpd.GeoDataFrame([])

        #Loop through GEF files, read them, and add to 'gdf'. Every GEF file holds data for several dephts on a single point.
        #By combining we get a large gdf containing all measurements for every point.
        for file in valid_files:
            GEF = os.path.join(input_folder, file)
            gdf_new = GEF_to_gdf(GEF)
            gdf = gdf.append(gdf_new, sort=False)

        #Downsample GDF using quantile/equal count buckets:
        reduced_dfs_dict = reduce_gdf(gdf, no_of_buckets)

        data_types = {'Elektrische geleidbaarheid [S/m]':'EC',
                      'Gecorrigeerde conusweerstand [MPa]':'Qc',
                      'Plaatselijke wrijving [MPa]':'Wr'}

        #Create output for each data type
        for data_type in data_types.keys():
            df = reduced_dfs_dict[data_type]
            gdf = gpd.GeoDataFrame(df)
            gdf.crs = {'init': 'epsg:28992'}
            filename = output_file[:-4] + '_'+data_types[data_type] + output_file[-4:]
            gdf.to_file(driver = 'ESRI Shapefile', filename = filename)

        error_msg = ''
        success = True

    except Exception as error:
        success = False
        error_msg = error

    logging = {'no_GEFs':len(valid_files),'success':success, 'error':error_msg}
    return logging
