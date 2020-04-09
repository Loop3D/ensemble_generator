from os import path
import sys
import pandas as pd
import scipy.stats as ss
import numpy as np
import rasterio

sys.path.append(path.abspath('./python'))
sys.path.append(path.abspath('C:/Users/Mark/Documents/GitHub/Loop3D/map2loop'))
from map2loop import m2l_utils

# this works but wants me to import all the packages listed in m2l_utils... not sure I want to do that.
from m2l_utils_egen import \
    ddd2dircos  # this import can be linked to m2l_utils once these functions are linked i.e. in the same or linked repos
from m2l_utils_egen import \
    dircos2ddd  # this import can be linked to m2l_utils once these functions are linked i.e. in the same or linked repos
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
import rasterio

# from map2loop import m2l_utils
# location=[(x,y)]
# dtm = rasterio.open(path_to_geotiff)
# height=m2l_utils.value_from_raster(dtm,location)

# TODO add code to resample orientation locations


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
contacts_clean.csv -> contacts_clean_1.csv; contacts_clean_2.csv; etc
orientations_clean.csv -> orientations_clean_1.csv; orientations_clean_2.csv; etc

There is very likely a more efficient way of doing this, but for the moment, this is how we do it.'''

'''Some outstanding issues
Re sampling elevation based on new coordiantes. This can be done from the DEM easily enough for surface measurements. This cannot be done 
for measurements at depth (section interps, drillholes etc. A flag for depth constraints can be added so that they're not changed, 
but this complicates things a fair bit. The impact of slightly different elevations for surface measurments is not great enough right now to
spend a lot of time on it. For the moment, Z elevations won't be resampled for simplicity.'''


def perturb_interface(samples, error_gps, file_input='contacts', distribution='uniform', DEM=None):
    ''' samples is the number of draws, thus the number of models in the ensemble
    error_gps is the assumed error in the location, and will be the width of the distribution
    distribution is the sampling type - defaults to uniform, the other option is 'normal' '''

    if file_input == 'faults':
        input_file = pd.read_csv("faults.csv")  # load data
    else:
        input_file = pd.read_csv("contacts_clean.csv")  # load data

    if DEM is True:
        dtm = rasterio.open("C:/Users/Mark/Cloudstor/EGen/test_data3/dtm/hammersley_sheet_dtm.ers")
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
        file_name = file_input + "_" + distribution + "_" + str(m) + ".csv"
        print(file_name)
        new_coords.to_csv(file_name)
    return

# TODO finish this thing
def perturb_contact_orient_vMF(samples, kappa, error_gps, file_input='contacts', loc_distribution='uniform', DEM=None):
    # samples is the number of draws, thus the number of models in the ensemble
    # kappa is the assumed error in the orientation, and is roughly the inverse to the width of the distribution
    # i.e. higher numbers = tighter distribution
    if file_input == 'faults':
        input_file = pd.read_csv("faults.csv")  # load data
    else:
        input_file = pd.read_csv("contacts_clean.csv")  # load data

    if DEM is True:
        dtm = rasterio.open("C:/Users/Mark/Cloudstor/EGen/test_data3/dtm/hammersley_sheet_dtm.ers")
    ''' check is needed here to make sure dtm is in the same projection as the contacts data. dtm.crs == projection of project '''

    '''set distribution type for sampling'''
    if distribution == 'normal':
        dist_func = ss.norm.rvs
    else:
        dist_func = ss.uniform.rvs

    file_orient = pd.read_csv("orientations_clean.csv")
    # convert dip strike to vector normal
    # the mean vector has three elements, "l", "m" and "n", each a direction cosine wrt the three coordinate axes

    for s in range(samples):
        new_ori = []
        new_orient = file_orient[["X", "Y", "Z", "azimuth", "dip", "polarity", "formation"]]
        for r in range(len(file_orient)):
            [l, m, n] = (ddd2dircos(file_orient.loc[r, 'dip'], file_orient.loc[r, 'azimuth']))
            samp_mu = sample_vMF(np.array([l, m, n]), kappa, 1)
            new_ori.append(dircos2ddd(samp_mu[0, 0], samp_mu[0, 1], samp_mu[0, 2]))
        new_ori = pd.DataFrame(new_ori)
        new_orient["azimuth"], new_orient["dip"] = new_ori[1], new_ori[0]
        file_name = "contact_orientations_" + str(s) + ".csv"

        new_orient.to_csv(file_name)


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
        file_name = "fault_orientations_" + str(s) + ".csv"
        new_orient.to_csv(file_name)
