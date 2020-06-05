# ensemble_generator

## Functions for generating and analysing ensembles of geological models

## Workflow

### Source of model and data: **map2loop**

**1. Import modules**
sys
os
egen_func
perturber_func
m2l_export_egen
egen_summary_stats
egen_parse_geomodeller

**2. Set paths**
egen_paths

**3. Build a task file from the data extracted from GIS by map2loop**
l2gm_ensemble - *this will be the 'original' model*

**4. Compute original model and export lithology/scalar voxet/s**
1. egen_create_batch_auto
2. execute batch files

**5. perturb the input data**
1. perturb_interface
2. perturb_orient_vMF

**6. build the ensemble: create the task files**
task_builder

**7. compute the ensemble: compute models and export litho/scalar voxets**
1. egen_create_batch_auto . *multiprocessing*
2. execute the batch files

**8. run summary stats**
stats_gocad_voxet

### Source of model and data: **GeoModeller**

**1. Import modules**
sys
os
egen_func
perturber_func
*m2l_export_egen - not needed if source is geomodeller model*
egen_summary_stats
egen_parse_geomodeller

**2. Set paths**
egen_paths

**3. convert xml to task file and parse task file to extract model data, metadata and topology**
1. egen_xml_to_task
2. execute the task file
3. parse_gm_task

**4. Compute original model and export lithology/scalar voxets**
1. egen_create_batch_auto
2. execute batch files

**5. perturb the input data**
1. perturb_interface
2. perturb_orient_vMF

**6. build the ensemble: create the task files**
task_builder

**7. compute the ensemble: compute models and export litho/scalar voxets**
1. egen_create_batch_auto . *multiprocessing*
2. execute the batch files

**8. run summary stats**
stats_gocad_voxet
