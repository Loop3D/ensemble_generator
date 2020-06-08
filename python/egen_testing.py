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
egen_func.egen_paths(geomodeller = r"C:\GeoModeller\GeoModeller4.0.8_x64_88b64e610d9" , model = r"C:/Users/Mark/Cloudstor/EGen/Geomodel_demo")
egen_func.egen_calc_original('model_0.task')
egen_func.egen_orig_model_voxets(30, 30, 30, litho=True)
egen_func.egen_create_batch('model_0.task', 'model_1.task', 'model_2.task', 'model_3.task', 'model_4.task', 'model_5.task', 'model_6.task', 'model_7.task', 'model_8.task', 'model_9.task', 'model_10.task')
egen_func.egen_create_batch('model_0_voxet.task', 'model_1_voxet.task', 'model_2_voxet.task', 'model_3_voxet.task', 'model_4_voxet.task', 'model_5_voxet.task', 'model_6_voxet.task', 'model_7_voxet.task', 'model_8_voxet.task', 'model_10_voxet.task')
#create model and voxet calc batch file
model_path = 'C:/Users/Mark/Cloudstor/EGen/test_data3'
egen_func.calc_voxet_ensemble(model_path, 25, 25, 25, litho = True)
egen_func.egen_create_voxet_ensemble_batch(11)

test_data_name='test_data3'

test_data_path='C:/Users/Mark/Cloudstor/EGen/test_data3'

task_list = list(np.zeros(100))
for x in range(100):
    task_list[x] = f'Geomodel_demo_{x}.task'
egen_func.egen_create_batch(task_list)

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

# timing the function
import multiprocessing as mp

import m2l_export_egen as egen
series_c = (['Turee_Creek_Group', 'Hamersley_Group', 'Fortescue_Group'])
fault_calc = (['Fault_12644', 'Fault_2235', 'Fault_11442', 'Fault_3496', 'Fault_5298', 'Fault_12647'])
fault
egen.l2gm_ensemble('C:/Users/Mark/Cloudstor/EGen/test_data3', './tmp/', './output/', './dtm/dtm_rp.tif', save_faults = True, model_from=0, model_to=5, series_calc=series_c, fault_calc=fault_selection)

# series_c selection
pool = mp.Pool()
start_time = time.time()
pool.map(egen.l2gm_ensemble('C:/Users/Mark/Cloudstor/EGen/test_data3', './tmp/', './output/', './dtm/dtm_rp.tif', save_faults = True, model_from=0, model_to=5, series_calc=series_c))
print(time.time() - start_time))
pool.close()

#
p1 = mp.Process(target=egen.l2gm_ensemble('C:/Users/Mark/Cloudstor/EGen/test_data3', './tmp/', './output/', './dtm/dtm_rp.tif', save_faults = True, model_from=0, model_to=5, series_calc=series_c))
p1.start()
p2 = mp.Process(target=egen.l2gm_ensemble('C:/Users/Mark/Cloudstor/EGen/test_data3', './tmp/', './output/', './dtm/dtm_rp.tif', save_faults = True, model_from=6, model_to=10, series_calc=series_c))
p2.start()

# timeit.timeit(egen.l2gm_ensemble('C:/Users/Mark/Cloudstor/EGen/test_data3', './tmp/', './output/', './dtm/dtm_rp.tif', save_faults = True, model_from=0, model_to=5, series_calc=series_c))
# series_c selection, models 5-10
egen.l2gm_ensemble('C:/Users/Mark/Cloudstor/EGen/test_data3', './tmp/', './output/', './dtm/dtm_rp.tif', save_faults = True, model_from=5, model_to=10, series_calc=series_c)

#all series
egen.l2gm_ensemble('C:/Users/Mark/Cloudstor/EGen/test_data3', './tmp/', './output/', './dtm/dtm_rp.tif', save_faults = True)



# debug parameters
samples = 1
model_path = 'C:/Users/Mark/Cloudstor/EGen/test_data3'
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

#%%

def test_func(model_from=None, model_to=None):
    if model_from is None:
        model_from = 2
    if model_to is None:
        model_to = 22
    print('model from:' + str(model_from))
    print('model_to:' + str(model_to))

test_func(1, 10)
test_func()

#%% testing voxet import /export

#directory = "C:/Users/Mark/Cloudstor/EGen/test_data3/Models_Prelim/CURE"
directory = "C:/CURE/3D-Paterson-FDS-Model2-UCert/CURE"
type = "GOCAD_LITHO"

import egen_summary_stats as es

propor_data, litho_df, card_df, ent_df = es.stats_gocad_voxet(directory, type, model_label='Yeneena', card=True, ent=True, propor = True)

# debug
model_label='test_1'
card=True
ent=True
propor = True


# convert
card_export = np.array(card, '>f4')

# write
card_export.tofile('./test_card.vop1')# , '>f4')
data.tofile('./data_test.vop1', format='>f4')


# read output binary

test_data = np.fromfile('./test_card.vop1', '>f4')
test_data = np.fromfile('./data_test.vop1', '>f4')

# difference

np.mean(data - test_data)

#%%
# testing run_egen


import run_egen_func as re
#class_file = 'realInit_parameters'  # don't add the .py file extension dummy
class_file = 'Geomodel_parameters'
re.run_egen(class_file)

#debug
par_file = ('../test_data3/EGen_par.py')

#%% testing task builder
import pathlib
from egen_func import task_builder
from Geomodel_parameters import egen_project

#filename = 'realInit.task'
#path = pathlib.Path('C:/Users/Mark/Cloudstor/EGen/ObjFunc_model') / filename

filename = 'Geomodel_demo.task'
path = 'C:/Users/Mark/Cloudstor/EGen/Geomodel_demo/' # / filename
#par_file = path.parent / 'Geomodel_par.py'
class_file = 'Geomodel_parameters'
# exec(open(par_file).read())
# series_calc = series_list

task_builder(egen_project.path_to_model, egen_project.model_task, 'Geomodel_parameters')
#
# egen_runs = 10
# series_calc = None
# krig_range = None
# interface = None
# orientation = None
# drift = None
# fault_calc = 'all'
#
# litho = True # True or comment out
# scalar = False# True or comment out
# scalar_grads = False # True or comment out
#
# # Voxet parameters
# nx = 50
# ny = 50
# nz = 50
# task_builder(path, filename, egen_runs)

#%% Parse task testing

import egen_parse_geomodeller as ep
ep.parse_gm_task('C:/Users/Mark/Cloudstor/EGen/Geomodel_demo/Geomodel_demo.task')
model_task = 'C:/Users/Mark/Cloudstor/EGen/Geomodel_demo/Geomodel_demo.task'

#%%
import egen_func as ef
ef.egen_xml_to_task(path_to_model, model_xml=model_xml, model_task=model_task)