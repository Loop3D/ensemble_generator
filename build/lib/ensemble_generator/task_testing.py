#%%
from egen_func import egen_paths
from egen_func import egen_xml_to_task
from egen_func import egen_calc_original
from egen_func import egen_orig_model_voxets
from egen_func import egen_create_batch
from egen_func import egen_MC_cokrig_params


#%%
#egen_paths("c:\gemodeller", "c:\data")
#Geomodel demo
egen_paths(geomodeller = r"C:\GeoModeller\GeoModeller4.0.8_x64_88b64e610d9" , model = r"C:\Users\Mark\Cloudstor\EGen\models\Geomodel_demo")
egen_xml_to_task("Geomodel_demo.xml")

#%%
# MPM_Test_3 - update mid Feb 2020
egen_paths(geomodeller = r"C:\GeoModeller\GeoModeller4.0.8_x64_88b64e610d9" , model = r"C:\Users\Mark\Cloudstor\EGen\test_data3\Models_Prelim")
egen_xml_to_task("Models_UWA.xml")

#%%
#Yerrida prospectivity
egen_paths(geomodeller = r"C:\GeoModeller\GeoModeller4.0.8_x64_88b64e610d9" , model = r"E:/Projects/Capricorn/3Dmodels/Yerrida/YerridaBasin_masked_10Oct2017")
egen_xml_to_task("YerridaBasin_masked_10Oct2017.xml")
egen_orig_model_voxets(234, 188, 88, litho=1, scalar=0, scalar_grads=0)
#egen_orig_model_voxets(234, 188, 88, litho=1)

#%%
# Hamersley with petro assigned, c:\CURE\Models....
egen_paths(geomodeller = r"C:\GeoModeller\GeoModeller4.0.7_x64_27eee3dc31ba", model = r"C:/CURE/Models_Prelim_geophys")
egen_xml_to_task("Models_Prelim_geophys.xml")
egen_calc_original()
egen_orig_model_voxets(103, 113, 33, litho=1)
egen_create_batch("orig_model_voxet.task")

#%%
# Hamersley with petro assigned,
egen_paths(geomodeller = r"C:\GeoModeller\GeoModeller4.0.8_x64_88b64e610d9" , model = r"C:/Users/Mark/Cloudstor/EGen/test_data3_MDL/Models_Prelim_geophys")
egen_xml_to_task("Models_Prelim_geophys.xml")
egen_calc_original()
egen_orig_model_voxets(50, 50, 25, litho=1)
egen_create_batch("xml_to_task.task", "calc_orig_model.task", "orig_model_voxet.task")


#%%
# Fabiele Paterson
egen_paths(geomodeller = r"C:\GeoModeller\GeoModeller4.0.8_x64_88b64e610d9" , model = r"C:\Users\Mark\Cloudstor\EGen\3D-Paterson-FDS-Model2-16Mar20")
egen_xml_to_task("3D-Paterson-FDS-Model2-16Mar20.xml")
egen_calc_original()
egen_orig_model_voxets(50, 50, 25, litho=1)
egen_create_batch("xml_to_task.task", "calc_orig_model.task", "orig_model_voxet.task")


egen_MC_cokrig_params()

#egen_create_batch("orig_model.task","calc_orig_model.task","orig_model_voxet.task")
#egen_create_batch("egen_MC_cokrig_params.task")
egen_create_batch("orig_model_mesh.task")



egen_create_batch("calc_orig_model.task","orig_model_voxet.task")



# experiment file
# required variables
# path to: geomodeller\bin; model
# model xml name
# voxet output: type and voxel parameters (nx, ny, nz)

# disturbance parameters


