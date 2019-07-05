# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 17:13:14 2019

@author: VanBoven
"""

# -*- coding: utf-8 -*-

"""

Created on Mon Jun 24 17:13:14 2019



@author: VanBoven

"""

import geopandas as gpd
import shapely
from shapely.geometry import Polygon, MultiPolygon
import numpy as np

def create_grid(gdf):
    gdf_rd = gdf.to_crs(epsg=28992)
    
    xmin,ymin,xmax,ymax = gdf_rd.total_bounds
    
    #must be an int
    lenght = 5
    wide = 5
    
    
    cols = list(range(int(np.floor(xmin)), int(np.ceil(xmax)), wide))
    rows = list(range(int(np.floor(ymin)), int(np.ceil(ymax)), lenght))
    rows.reverse()
    
    polygons = []
    for x in cols:
        for y in rows:
            polygon = Polygon([(x,y), (x+(wide/factor), y), (x+(wide/1000), y-(lenght/factor)), (x, y-(lenght/factor))])
            polygons.append(polygon)  
    
    angle = 0 # counter-clockwise! set crop row angle         
    #rotate
    polygon_group = MultiPolygon(polygons)
    polygon_group = shapely.affinity.rotate(polygon_group, angle)
    #create grid
    grid = gpd.GeoDataFrame({'geometry':polygon_group[:]})
    #optional, write grid to file
    #grid.to_file(r"C:\Users\ericv\Desktop\Technodag/GRID_rotated.shp")
    return grid





