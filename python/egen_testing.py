#%%
# generate 1 new model
'''
uses the loop2geomodeller function from m2l_export.py
def loop2geomodeller(test_data_path,tmp_path,output_path,dtm_file,bbox,save_faults,compute_etc,workflow)
test_data_path =  path to the data import to the model [orientations; contacts; all_sorts (?) - dunno what this is
                this is typically ../output/
tmp_path = path to the /tmp folder. Contains [all_sorts_clean.csv - defines the strat column]

output_path = path to where the model is output
dtm_file = path to the DTM
bbox = bounding box coords.
save_faults = flag for saving faults [True; False]?
compute_etc = compute model or just output task [True; False]?
workflow = this is inactive - no corresponding var in the function
'''

#%%
import os
import geopandas as gpd
import networkx
import sys

# path to map2loop and other imported functions
sys.path.append(os.path.abspath('./python'))
sys.path.append(os.path.abspath('C:/Users/Mark/Documents/GitHub/Loop3D/map2loop/map2loop'))

#egen imports
import egen_func

# l2gm_ensemble modules - debug
import networkx as nx
import random
import numpy as np
import pandas as pd
import time
import pyproj

# map2loop imports
from m2l_export import loop2geomodeller


#%%
import egen_func
#Windows
#path must not have '/' at the end
egen_func.egen_paths(geomodeller = r"C:\GeoModeller\GeoModeller4.0.8_x64_88b64e610d9" , model = r"C:/Users/Mark/Cloudstor/EGen/test_data3")
egen_func.egen_calc_original('model_0.task')
egen_func.egen_orig_model_voxets(30, 30, 30, litho=True)
egen_func.egen_create_batch('model_0_voxet.task', 'model_1_voxet.task', 'model_2_voxet.task', 'model_3_voxet.task', 'model_4_voxet.task', 'model_5_voxet.task')
test_data_name='test_data3'

test_data_path='C:/Users/Mark/Cloudstor/EGen/test_data3'

#os.chdir(test_data_path)
os.chdir(test_data_path)
%run -i "egen_config.py"

# print(os.getcwd())
#
# bbox2=str(minx)+","+str(miny)+","+str(maxx)+","+str(maxy)
# lat_point_list = [miny, miny, maxy, maxy, maxy]
# lon_point_list = [minx, maxx, maxx, minx, minx]
# bbox_geom = Polygon(zip(lon_point_list, lat_point_list))
# polygon = gpd.GeoDataFrame(index=[0], crs=dst_crs, geometry=[bbox_geom])
bbox=(minx,miny,maxx,maxy,model_top,model_base) #

#%% Running loop2geomodeller

#loop2geomodeller(model + "output/", model + "tmp/", )


import m2l_export_egen as egen


egen.l2gm_ensemble(11, 'C:/Users/Mark/Cloudstor/EGen/test_data3', './tmp/', './output/', './dtm/dtm_rp.tif', save_faults = True)

# debug parameters
samples = 1
test_data_path = 'C:/Users/Mark/Cloudstor/EGen/test_data3'
tmp_path = './tmp/'
output_path = './output/'
dtm_file = './dtm/dtm_rp.tif'
#bbox
save_faults = True
compute_etc = True

#%% calc_voxet_ensemble testing

import egen_func
import os, glob

# debug args
model_path = 'C:/Users/Mark/Cloudstor/EGen/test_data3'
path = test_data_path
nx = 25
ny = 25
nz = 25
model_from = 0
model_to = 10
litho = True
scalar=None
scalar_grads=None

egen_func.calc_voxet_ensemble(model_path, 25, 25, 25, litho = True)
egen_func.egen_create_batch('model_0_voxet.task', 'model_1_voxet.task', 'model_2_voxet.task', 'model_3_voxet.task', 'model_4_voxet.task', 'model_5_voxet.task')