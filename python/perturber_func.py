from os import path
import sys
import pandas as pd
import scipy.stats as ss
import numpy as np
import rasterio
from map2loop import m2l_utils


sys.path.append(path.abspath('./python'))
sys.path.append(path.abspath('C:/Users/Mark/Documents/GitHub/Loop3D/map2loop'))

# this works but wants me to import all the packages listed in m2l_utils... not sure I want to do that.
from m2l_utils_egen import ddd2dircos # this import can be linked to m2l_utils once these functions are linked i.e. in the same or linked repos
from m2l_utils_egen import dircos2ddd # this import can be linked to m2l_utils once these functions are linked i.e. in the same or linked repos
from spherical_utils import sample_vMF # thanks to https://github.com/jasonlaska/spherecluster/
# from egen_func import sample_vMF
import m2l_utils_egen

#from jetbrains://pycharm/navigate/reference?project=geol-model-egen&path=python/m2l_utils_egen.py import dd2dircos

# TODO add this bit to location resampling
The function

value_from_raster(dataset,locations)

in m2l_utils samples a rasterio raster (dataset) at a given xy location (locations)

e.g.

import rasterio
from map2loop import m2l_utils
location=[(x,y)]
dtm = rasterio.open(path_to_geotiff)
height=m2l_utils.value_from_raster(dtm,location)

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

def perturb_geol_interface_uniform(samples, error_gps, DEM = None):
    # samples is the number of draws, thus the number of models in the ensemble
    # error is the assumed error in the location, and will be the width of the distribution
    file_contacts = pd.read_csv("contacts_clean.csv")
    # DEM = # import DEM here for sample new elevations for surface elevations. ISSUE: Don't want to resample elevations for interfaces at depth. Depth constraints needs to be flagged as such?
    for m in range(0, samples):
        new_coords_u = pd.DataFrame(np.empty((len(file_contacts), 4)),
                                columns=['X', 'Y', 'Z', 'formation'])  # uniform
        for r in range(len(file_contacts)):
            start_x = file_contacts.loc[r, 'X']
            new_coords_u.loc[r, 'X'] = ss.uniform.rvs(size=1, loc=start_x-(error_gps/2), scale=error_gps)
            start_y = file_contacts.loc[r, 'Y']
            new_coords_u.loc[r, 'Y'] = ss.uniform.rvs(size=1, loc=start_y-(error_gps/2), scale=error_gps)
            new_coords_u.loc[r, 'Z'] = file_contacts.loc[r, 'Z']  # placeholder for the moment
            # TODO line to map new Z value based on sampling the DEM at the new X,Y location
            new_coords_u.loc[r, 'formation'] = file_contacts.loc[r, 'formation']
        file_name = "contacts_clean_uniform_" + str(m) + ".csv"
        new_coords_u.to_csv(file_name)
        # add line to export perturbation parameters as txt
        return

def perturb_geol_interface_normal(samples, std_gps, DEM = None):
    # samples is the number of draws, thus the number of models in the ensemble
    # error is the assumed error in the location, and will be the width of the distribution
    file_contacts = pd.read_csv("contacts_clean.csv")
    # DEM = # import DEM here for sample new elevations for surface elevations. ISSUE: Don't want to resample elevations for interfaces at depth. Depth constraints needs to be flagged as such?
    # The DEM issue is not that important right now, but can be addressed in the future. For the time being, Z elevations will remain unchanged given they will have little influence if they do.
    for m in range(0, samples):
        new_coords_n = pd.DataFrame(np.empty((len(file_contacts), 4)),
                                columns=['X', 'Y', 'Z', 'formation'])  # normal
        for r in range(len(file_contacts)):
            start_x = file_contacts.loc[r, 'X']
            new_coords_n.loc[r, 'X'] = ss.norm.rvs(size=1, loc=start_x, scale=std_gps)
            start_y = file_contacts.loc[r, 'Y']
            new_coords_n.loc[r, 'Y'] = ss.norm.rvs(size=1, loc=start_y, scale=std_gps)
            new_coords_n.loc[r, 'Z'] = file_contacts.loc[r, 'Z']  # placeholder for the moment
            # TODO line to map new Z value based on sampling the DEM at the new X,Y location
            new_coords_n.loc[r, 'formation'] = file_contacts.loc[r, 'formation']
        file_name = "contacts_clean_norm_" + str(m) + ".csv"
        new_coords_n.to_csv(file_name)
        #add line to export perturbation parameters as txt
        return

def perturb_fault_interface_uniform(samples, error_gps, DEM = None):
    # samples is the number of draws, thus the number of models in the ensemble
    # error is the assumed error in the location, and will be the width of the distribution
    file_fault = pd.read_csv("faults.csv")
    # DEM = # import DEM here for sample new elevations for surface elevations. ISSUE: Don't want to resample elevations for interfaces at depth. Depth constraints needs to be flagged as such?
    for m in range(0, samples):
        new_coords_f_u = pd.DataFrame(np.empty((len(file_fault), 4)),
                                columns=['X', 'Y', 'Z', 'formation'])  # uniform
        for r in range(len(file_fault)):
            start_x = file_fault.loc[r, 'X']
            new_coords_f_u.loc[r, 'X'] = ss.uniform.rvs(size=1, loc=start_x-(error_gps/2), scale=error_gps)
            start_y = file_fault.loc[r, 'Y']
            new_coords_f_u.loc[r, 'Y'] = ss.uniform.rvs(size=1, loc=start_y-(error_gps/2), scale=error_gps)
            new_coords_f_u.loc[r, 'Z'] = file_contacts.loc[r, 'Z']  # placeholder for the moment
            # TODO line to map new Z value based on sampling the DEM at the new X,Y location
            new_coords_f_u.loc[r, 'formation'] = file_fault.loc[r, 'formation']
        file_name = "faults_uniform_new" + str(m) + ".csv"
        new_coords_f_u.to_csv(file_name)
        # add line to export perturbation parameters as txt
        return

def perturb_fault_interface_normal(samples, std_gps, DEM = None):
    # samples is the number of draws, thus the number of models in the ensemble
    # error is the assumed error in the location, and will be the width of the distribution
    file_fault = pd.read_csv("faults.csv")
    # DEM = # import DEM here for sample new elevations for surface elevations. ISSUE: Don't want to resample elevations for interfaces at depth. Depth constraints needs to be flagged as such?
    # The DEM issue is not that important right now, but can be addressed in the future. For the time being, Z elevations will remain unchanged given they will have little influence if they do.
    for m in range(0, samples):
        new_coords_f_n = pd.DataFrame(np.empty((len(file_fault), 4)),
                                columns=['X', 'Y', 'Z', 'formation'])  # normal
        for r in range(len(file_fault)):
            start_x = file_fault.loc[r, 'X']
            new_coords_f_n.loc[r, 'X'] = ss.norm.rvs(size=1, loc=start_x, scale=std_gps)
            start_y = file_fault.loc[r, 'Y']
            new_coords_f_n.loc[r, 'Y'] = ss.norm.rvs(size=1, loc=start_y, scale=std_gps)
            new_coords_f_n.loc[r, 'Z'] = file_fault.loc[r, 'Z']  # placeholder for the moment
            # TODO line to map new Z value based on sampling the DEM at the new X,Y location
            new_coords_f_n.loc[r, 'formation'] = file_fault.loc[r, 'formation']
        file_name = "faults_norm_" + str(m) + ".csv"
        new_coords_f_n.to_csv(file_name)
        #add line to export perturbation parameters as txt
        return


def perturb_contact_orient_vMF(samples, kappa):
    # samples is the number of draws, thus the number of models in the ensemble
    # kappa is the assumed error in the orientation, and is roughly the inverse to the width of the distribution
    # i.e. higher numbers = tighter distribution
    file_orient = pd.read_csv("orientations_clean.csv")
    # convert dip strike to vector normal
    # the mean vector has three elements, "l", "m" and "n", each a direction cosine wrt the three coordinate axes

    for s in range(samples):
        new_ori =  []
        new_orient = file_orient[["X", "Y", "Z", "azimuth", "dip", "polarity", "formation"]]
        for r in range(len(file_orient)):
            [l, m, n] = (ddd2dircos(file_orient.loc[r, 'dip'], file_orient.loc[r, 'azimuth']))
            samp_mu = sample_vMF(np.array([l, m, n]), kappa, 1)
            new_ori.append(dircos2ddd(samp_mu[0,0], samp_mu[0,1], samp_mu[0,2]))
        new_ori = pd.DataFrame(new_ori)
        new_orient["azimuth"], new_orient["dip"] = new_ori[1], new_ori[0]
        file_name = "contact_orientations_" + str(s) + ".csv"

        new_orient.to_csv(file_name)


def perturb_fault_interface_vMF(samples, kappa):
    #convert dip strike to vector normal
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
            [l, m, n] = (ddd2dircos(file_fault_orientation.loc[r, 'dip'], file_fault_orientation.loc[r, 'DipDirection']))
            samp_mu = sample_vMF(np.array([l, m, n]), kappa, 1)
            new_ori.append(dircos2ddd(samp_mu[0, 0], samp_mu[0, 1], samp_mu[0, 2]))
        new_ori = pd.DataFrame(new_ori)
        new_orient["azimuth"], new_orient["dip"] = new_ori[1], new_ori[0]
        file_name = "fault_orientations_" + str(s) + ".csv"
        new_orient.to_csv(file_name)

