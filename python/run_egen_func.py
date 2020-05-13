import egen_func as ef
import perturber_func as pf
import m2l_export_egen as ex
import egen_summary_stats as es
import multiprocessing as mp
import stats_utils
import time
import numpy as np
import os

# debug
par_file = 'C:/Users/Mark/Cloudstor/EGen/test_data3/EGen_par.py'

def run_egen(par_file=None):
    #load Egen_par.py
    exec(open(par_file).read())

    # open egen execute .py file
    os.chdir(path_to_model)
    f = open('egen_execute.py', 'w')

    # Step 0 - import modules

    modules = '''
import sys, os
sys.path.append(os.path.abspath('C:/Users/Mark/Cloudstor/EGen/ensemble_generator/python'))
import egen_func as ef
import perturber_func as pf
import m2l_export_egen as ex
import egen_summary_stats as es
'''

    f.write(modules)
    # Step 1 - set paths

    egen_path = f'''ef.egen_paths('{path_to_geomodeller}', '{path_to_model}')\n'''
    f.write(egen_path)

    # Step 2 - perturb interfaces
    change_dir = f'''os.chdir('./output')\n'''
    egen_int_forms_pert = f'''pf.perturb_interface({egen_runs}, {error_gps}, file_type='contacts', distribution='{distribution}', DEM={DEM})\n'''
    egen_int_fault_pert = f'''pf.perturb_interface({egen_runs}, {error_gps}, file_type='faults', distribution='{distribution}', DEM={DEM})\n'''
    f.write(change_dir)
    f.write(egen_int_forms_pert)
    f.write(egen_int_fault_pert)

    # Step 3 - perturb orientations
    egen_ori_forms_pert = f'''pf.perturb_orient_vMF({egen_runs}, {kappa}, {error_gps}, file_type='contacts', loc_distribution='{loc_distribution}', DEM={DEM})\n'''
    egen_ori_fault_pert = f'''pf.perturb_orient_vMF({egen_runs}, {kappa}, {error_gps}, file_type='faults', loc_distribution='{loc_distribution}', DEM={DEM})\n'''
    f.write(egen_ori_forms_pert)
    f.write(egen_ori_fault_pert)


    # Step 4 - create new model task file with l2gm_ensemble

    # calculate original model and export voxet




    # uses parallel processing for speed
    num_cores = mp.cpu_count()
    use_cores = int(num_cores*.8)

    # single processing at the moment (boring)
    egen_l2gm = f'''ex.l2gm_ensemble('{path_to_model}', './tmp/', './output/', './dtm/{DTM_name}', save_faults = {save_faults}, model_from=0, model_to={egen_runs}, series_calc="{series_c}")\n'''
    f.write(egen_l2gm)

    # Step 5 - compute models and export voxets

    pool_split = stats_utils.split(egen_runs, use_cores)
    pool = np.arange(0, egen_runs)
    #pool_list = []
    for i in range(use_cores):
        pool_list = pool[:int(pool_split[i])]
        model_names = []
        for j in pool_list:
            model_names.append("model_" + str(j) + "_voxet.task")
        egen_calc_vox_ens = f'''ef.calc_voxet.ensemble('{path_to_model}', {nx}, {ny}, {nz}, model_from={pool_list[0]}, model_to={pool_list[-1]}, litho={litho}, scalar={scalar}, scalar_grads={scalar_grads})\n'''
        #ef.egen_create_batch_auto(model_names, i)
        egen_create_batch = f'''ef.egen_create_batch_auto({model_names}, {i})\n'''
        pool = pool[int(pool_split[i]):]
        f.write(egen_calc_vox_ens)

    # Step 6 - import voxets and compute summary statistics
    if litho is True:
        egen_summary_litho_stats = f'''es.stats_gocad_voxet('./voxets', type = "GOCAD_LITHO", model_label='{model_label}', card = {card}, ent = {ent})\n'''
        f.write(egen_summary_litho_stats)
    # if scalar is True:
    #     # TODO enter scalar voxet output
    #     egen_summary_scalar_stats = f'''es.read_gocad_voxet('./voxets', type = "TODO", card = {card}, ent = {ent}'''
    #     f.write(egen_summary_scalar_stats)
    # if scalar_grads is True:
    #     # TODO enter scalar voxet grad output
    #     egen_summary_scalar_stats = f'''es.read_gocad_voxet('./voxets', type = "TODO", card = {card}, ent = {ent}'''
    #     f.write(egen_summary_scalar_stats)
    f.close()