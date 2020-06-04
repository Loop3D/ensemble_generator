# ensemble_generator

## Functions for generating and analysing ensembles of geological models

## Workflow

### Source of model and data: **map2loop**


### Source of model and data: **GeoModeller**

**Import modules**
sys
os
egen_func
perturber_func
m2l_export_egen
egen_summary_stats
egen_parse_geomodeller

**Set paths**
egen_paths

**convert xml to task file**
1. egen_xml_to_task
2. execute the task file

**parse the task file to extract model data, metadata and topology**
parse_gm_task

**perturb the input data**
1. perturb_interface
2. perturb_orient_vMF

**build the ensemble: create the task files**
task_builder

**compute the ensemble: compute models and export litho/scalar voxets**
1. egen_create_batch_auto . *multiprocessing*
2. execute the batch files

**run summary stats**
