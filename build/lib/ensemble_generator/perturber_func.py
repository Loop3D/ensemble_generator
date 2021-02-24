from os import path
import sys, glob, os
import pandas as pd
import scipy.stats as ss
import numpy as np
import rasterio
import pathlib
import pyproj

sys.path.append(path.abspath('./python'))
sys.path.append(path.abspath('C:/Users/Mark/Documents/GitHub/Loop3D/map2loop'))
from map2loop import m2l_utils

# this works but wants me to import all the packages listed in m2l_utils... not sure I want to do that.
from m2l_utils_egen import ddd2dircos  # this import can be linked to m2l_utils once these functions are linked i.e. in the same or linked repos
from m2l_utils_egen import dircos2ddd  # this import can be linked to m2l_utils once these functions are linked i.e. in the same or linked repos
from spherical_utils import sample_vMF  # thanks to https://github.com/jasonlaska/spherecluster/
# from egen_func import sample_vMF
import m2l_utils_egen

# from jetbrains://pycharm/navigate/reference?project=geol-model-egen&path=python/m2l_utils_egen.py import dd2dircos

# # TODO add this bit to location resampling
# The function
#
# value_from_raster(dataset,locations)
#
# in m2l_utils samples a rasterio raster (dataset) at a given xy location (locations)
#
# e.g.
#
# from map2loop import m2l_utils
# location=[(x,y)]
# dtm = rasterio.open(path_to_geotiff)
# height=m2l_utils.value_from_raster(dtm,location)

'''a script that perturbs the data exported from map2loop. This will conducted on the .csv files
- contacts_clean.csv
- orientations_clean.csv
- faults.csv
- fault_orientations.csv

Not done now but will be
- all_ign_contacts.csv
- ign_contacts.csv
- ign_orientations_domes.csv

A perturbed dataset will be produced for each model e.g.
contacts_clean.csv -> contacts_1.csv; contacts_clean_2.csv; etc
orientations_clean.csv -> contacts_orient_1.csv; orientations_clean_2.csv; etc
faults.csv -> faults_1.csv; faults_2.csv etc.
fault_orientations.csv -> faults_orient_1.csv; faults_orient_2.csv

There is very likely a more efficient way of doing this, but for the moment, this is how we do it.'''

'''Some outstanding issues
Re sampling elevation based on new coordinates. This can be done from the DEM easily enough for surface measurements. This cannot be done 
for measurements at depth (section interps, drillholes etc. A flag for depth constraints can be added so that they're not changed, 
but this complicates things a fair bit.'''


def perturb_interface(samples, error_gps, file_type='contacts', distribution='uniform', DEM=False, source_geomodeller=False):
    ''' samples is the number of draws, thus the number of models in the ensemble
    error_gps is the assumed error in the location, and will be the width of the distribution
    distribution is the sampling type - defaults to uniform, the other option is 'normal' '''
    # write out parameters for record
    output_location = './output'
    params_file = open(output_location + "/perturb_" + file_type + "_int_params.csv", "w")
    params_file.write("samples," + str(samples) + "\n")
    params_file.write("error_gps," + str(error_gps) + "\n")
    params_file.write("file_type," + file_type + "\n")
    params_file.write("distribution," + distribution + "\n")
    params_file.write("DEM," + str(DEM) + "\n")
    params_file.close()
    # todo navigate to data directory (should be {model_dir}/output
    if file_type == 'faults':
        input_file = pd.read_csv(output_location + "/faults.csv")  # load data
    else:
        input_file = pd.read_csv(output_location + "/contacts_clean.csv")  # load data

    if DEM is True:
        if source_geomodeller is True:
            load_this = glob.glob(f'''./MeshGrids/DTM.igmesh/*.ers''')
            dtm = rasterio.open(load_this[0])
        else:
            dtm = rasterio.open(f'''./dtm/{DTM_name}''')
            if dtm.crs.linear_units != 'metre':
                print("Warning: this DEM is not in a UTM projection.\n Please supply one and try again.")
                ''' this checks to see if the DTM projection is in metres (basic check for LoopS and geomodeller
                doesn't check that the DTM and contact/fault projections are the same. We don't input this data
                projections, so comparison isn't made at this point'''

    ''' check is needed here to make sure dtm is in the same projection as the contacts data. dtm.crs == projection of project '''

    '''set distribution type for sampling'''
    if distribution == 'normal':
        dist_func = ss.norm.rvs
    else:
        dist_func = ss.uniform.rvs

    # DEM = # import DEM here for sample new elevations for surface elevations. ISSUE: Don't want to resample elevations for interfaces at depth. Depth constraints needs to be flagged as such?
    for m in range(0, samples):
        new_coords = pd.DataFrame(np.zeros((len(input_file), 4)), columns=['X', 'Y', 'Z', 'formation'])  # uniform
        if DEM is True:
            for r in range(len(input_file)):
                start_x = input_file.loc[r, 'X']
                new_coords.loc[r, 'X'] = dist_func(size=1, loc=start_x - (error_gps), scale=error_gps)  # value error
                new_coords.loc[r, 'X'] = dist_func(size=1, loc=start_x - (error_gps), scale=error_gps)  # value error
                start_y = input_file.loc[r, 'Y']
                new_coords.loc[r, 'Y'] = dist_func(size=1, loc=start_y - (error_gps), scale=error_gps)
                elevation = m2l_utils.value_from_raster(dtm, [(new_coords.loc[r, 'X'], new_coords.loc[r, 'Y'])])
                if elevation == -999:  # points outside of the dtm will get a elevation of -999, this is to check for that. If outside, it uses the existing elevation
                    new_coords.loc[r, 'Z'] = input_file.loc[r, 'Z']
                else:
                    new_coords.loc[r, 'Z'] = elevation

        else:
            for r in range(len(input_file)):
                start_x = input_file.loc[r, 'X']
                new_coords.loc[r, 'X'] = dist_func(size=1, loc=start_x - (error_gps), scale=error_gps)  # value error
                start_y = input_file.loc[r, 'Y']
                new_coords.loc[r, 'Y'] = dist_func(size=1, loc=start_y - (error_gps), scale=error_gps)
                new_coords.loc[r, 'Z'] = input_file.loc[r, 'Z']

        new_coords["formation"] = input_file["formation"]
        file_name = file_type + "_" + str(m) + ".csv"
        #print(file_name)
        new_coords.to_csv(output_location + '/' + file_name, index=False)
    return


def perturb_orient_vMF(samples, kappa, error_gps, file_type='contacts', loc_distribution='uniform', DEM=False, source_geomodeller=False):
    # samples is the number of draws, thus the number of models in the ensemble
    # kappa is the assumed error in the orientation, and is roughly the inverse to the width of the distribution
    # i.e. higher numbers = tighter distribution
    # write out parameters for record
    output_location = './output'
    params_file = open(output_location + "/perturb_" + file_type + "_orient_params.csv", "w")
    params_file.write("samples," + str(samples) + "\n")
    params_file.write("kappa," + str(kappa) + "\n")
    params_file.write("error_gps," + str(error_gps) + "\n")
    params_file.write("file_type," + file_type + "\n")
    params_file.write("location_distribution," + loc_distribution + "\n")
    params_file.write("DEM," + str(DEM) + "\n")
    params_file.close()

    if file_type == 'faults':
        input_file = pd.read_csv(output_location + "/fault_orientations.csv")  # load data
    else:
        input_file = pd.read_csv(output_location + "/orientations_clean.csv")  # load data

    if DEM is True:
        if source_geomodeller is True:
            load_this = glob.glob(f'''./MeshGrids/DTM.igmesh/*.ers''')
            dtm = rasterio.open(load_this[0])
        else:
            dtm = rasterio.open(f'''{path_to_model}/dtm/{DTM_name}''')
            if dtm.crs.linear_units != 'metre':
                print("Warning: this DEM is not in a UTM projection.\n Please supply one and try again.")
                ''' this checks to see if the DTM projection is in metres (basic check for LoopS and geomodeller
                doesn't check that the DTM and contact/fault projections are the same. We don't input this data
                projections, so comparison isn't made at this point'''

    ''' check is needed here to make sure dtm is in the same projection as the contacts data. dtm.crs == projection of project '''

    '''set distribution type for location resampling'''
    if loc_distribution == 'normal':
        dist_func = ss.norm.rvs
    else:
        dist_func = ss.uniform.rvs

    for m in range(0, samples):
        new_coords = pd.DataFrame(np.zeros((len(input_file), 3)), columns=['X', 'Y', 'Z'])  # uniform
        for r in range(len(input_file)):
            start_x = input_file.loc[r, 'X']
            new_coords.loc[r, 'X'] = dist_func(size=1, loc=start_x - (error_gps), scale=error_gps)  # value error
            #new_coords.loc[r, 'X'] = dist_func(size=1, loc=start_x - (error_gps), scale=error_gps)  # value error
            start_y = input_file.loc[r, 'Y']
            new_coords.loc[r, 'Y'] = dist_func(size=1, loc=start_y - (error_gps), scale=error_gps)
            if DEM is True:
                elevation = m2l_utils.value_from_raster(dtm, [(new_coords.loc[r, 'X'], new_coords.loc[r, 'Y'])])
                if elevation == -999:  # points outside of the dtm will get a elevation of -999, this is to check for that. If outside, it uses the existing elevation
                    new_coords.loc[r, 'Z'] = input_file.loc[r, 'Z']
                else:
                    new_coords.loc[r, 'Z'] = elevation
            else:
                new_coords.loc[r, 'Z'] = input_file.loc[r, 'Z']



    #file_orient = pd.read_csv("orientations_clean.csv")
    # convert dip strike to vector normal
    # the mean vector has three elements, "l", "m" and "n", each a direction cosine wrt the three coordinate axes

    if file_type == 'faults':
        for s in range(samples):
            new_ori = []
            new_orient = input_file[["X", "Y", "Z", "DipDirection", "dip", "DipPolarity", "formation"]]
            for r in range(len(input_file)):
                [l, m, n] = (ddd2dircos(input_file.loc[r, 'dip'], input_file.loc[r, 'DipDirection']))
                samp_mu = sample_vMF(np.array([l, m, n]), kappa, 1)
                new_ori.append(dircos2ddd(samp_mu[0, 0], samp_mu[0, 1], samp_mu[0, 2]))
            new_ori = pd.DataFrame(new_ori)
            new_orient["X"], new_orient["Y"], new_orient["Z"] = new_coords["X"], new_coords["Y"], new_coords["Z"]
            new_orient["DipDirection"], new_orient["dip"] = new_ori[1], new_ori[0]
            file_name = file_type + "_orient_" + str(s) + ".csv"

            new_orient.to_csv(file_name)

    else:
        for s in range(samples):
            new_ori = []
            new_orient = input_file[["X", "Y", "Z", "azimuth", "dip", "polarity", "formation"]]
            for r in range(len(input_file)):
                [l, m, n] = (ddd2dircos(input_file.loc[r, 'dip'], input_file.loc[r, 'azimuth']))
                samp_mu = sample_vMF(np.array([l, m, n]), kappa, 1)
                new_ori.append(dircos2ddd(samp_mu[0, 0], samp_mu[0, 1], samp_mu[0, 2]))
            new_ori = pd.DataFrame(new_ori)
            new_orient["X"], new_orient["Y"], new_orient["Z"] = new_coords["X"], new_coords["Y"], new_coords["Z"]
            new_orient["azimuth"], new_orient["dip"] = new_ori[1], new_ori[0]
            new_orient.rename(columns={'azimuth' : 'dipdirection'}, inplace=True)
            file_name = file_type + "_orient_" + str(s) + ".csv"

            new_orient.to_csv(output_location + '/' + file_name, index=False)

    return


# dont think I need the one below any more
def perturb_fault_interface_vMF(samples, kappa):
    # convert dip strike to vector normal
    # samples is the number of draws, thus the number of models in the ensemble
    # kappa is the assumed error in the orientation, and is roughly the inverse to the width of the distribution
    # i.e. higher numbers = tighter distribution
    file_fault_orientation = pd.read_csv("fault_orientations.csv")
    # convert dip strike to vector normal
    # the mean vector has three elements, "l", "m" and "n", each a direction cosine wrt the three coordinate axes

    for s in range(samples):
        new_ori = []
        new_orient = file_fault_orientation[["X", "Y", "Z", "DipDirection", "dip", "DipPolarity", "formation"]]

        for r in range(len(file_fault_orientation)):
            [l, m, n] = (
                ddd2dircos(file_fault_orientation.loc[r, 'dip'], file_fault_orientation.loc[r, 'DipDirection']))
            samp_mu = sample_vMF(np.array([l, m, n]), kappa, 1)
            new_ori.append(dircos2ddd(samp_mu[0, 0], samp_mu[0, 1], samp_mu[0, 2]))
        new_ori = pd.DataFrame(new_ori)
        new_orient["azimuth"], new_orient["dip"] = new_ori[1], new_ori[0]
        params_file = open("perturb_fault_orient_params.csv", "w")
        params_file.write("samples," + str(samples) + "\n")
        params_file.write("kappa," + str(kappa) + "\n")
        #params_file.write("file_type," + file_type + "\n")
        #params_file.write("DEM," + str(DEM) + "\n")
        params_file.close()
        file_name = "fault_orientations_" + str(s) + ".csv"
        new_orient.to_csv(file_name)
