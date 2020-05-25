import egen.egen_func as ef
import egen.perturber_func as pf
import egen.m2l_export_egen as ex
import egen.egen_summary_stats as es
import multiprocessing as mp
import egen.stats_utils
import time
import numpy as np
import os

# debug
# par_file = 'C:/Users/Mark/Cloudstor/EGen/test_data3/EGen_par.py'
par_file = 'C:/Users/Mark/Cloudstor/EGen/ObjFunc_model/realInit_par.py'


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
    modelpath = f'''sys.path.append(os.path.abspath('{path_to_model}'))\n'''
    f.write(modelpath)
    egen_path = f'''ef.egen_paths('{path_to_geomodeller}', '{path_to_model}')\n'''
    f.write(egen_path)

    # Step 2 - perturb interfaces
    change_dir = f'''os.chdir('./output')\n'''
    egen_int_forms_pert = f'''pf.perturb_interface({egen_runs}, {error_gps}, file_type='contacts', distribution='{distribution}', DEM={DEM}, source_geomodeller={source_geomodeller})\n'''
    f.write(egen_int_forms_pert)
    if source_geomodeller is False:
        egen_int_fault_pert = f'''pf.perturb_interface({egen_runs}, {error_gps}, file_type='faults', distribution='{distribution}', DEM={DEM}, source_geomodeller={source_geomodeller})\n'''
        f.write(egen_int_fault_pert)
    f.write(change_dir)



    # Step 3 - perturb orientations
    egen_ori_forms_pert = f'''pf.perturb_orient_vMF({egen_runs}, {kappa}, {error_gps}, file_type='contacts', loc_distribution='{loc_distribution}', DEM={DEM})\n'''
    f.write(egen_ori_forms_pert)
    if source_geomodeller is False:
        egen_ori_fault_pert = f'''pf.perturb_orient_vMF({egen_runs}, {kappa}, {error_gps}, file_type='faults', loc_distribution='{loc_distribution}', DEM={DEM})\n'''
        f.write(egen_ori_fault_pert)


    # Step 4 - create new model task file with l2gm_ensemble

    # calculate original model and export voxet




    # uses parallel processing for speed
    num_cores = mp.cpu_count()
    use_cores = int(num_cores*.8)

    # single processing at the moment (boring)
    egen_l2gm = f'''ex.l2gm_ensemble('{path_to_model}', './tmp/', './output/', './dtm/{DTM_name}', save_faults = {save_faults}, model_from=0, model_to={egen_runs}, series_calc="{series_list}", fault_calc = {fault_list})\n'''
    f.write(egen_l2gm)

    # Step 5 - compute models and export voxets

    pool_split = stats_utils.split(egen_runs, use_cores)
    pool = np.arange(0, egen_runs)
    #pool_list = []
    for g in range(use_cores):
        pool_list = pool[:int(pool_split[g])]
        calc_model_names = []
        for h in pool_list:
            calc_model_names.append("model_" + str(h) + ".task")

        egen_create_batch = f'''ef.egen_create_batch_auto({calc_model_names}, {g})\n'''
        pool = pool[int(pool_split[g]):]
        f.write(egen_create_batch)

    for e in range(use_cores):
        egen_exec_batch = f'''os.system('cmd /c egen_batch_{e}.bat')\n'''
        f.write(egen_exec_batch)

    change_dir_1 = f'''os.chdir('./ensemble')\n'''
    f.write(change_dir_1)

    pool = np.arange(0, egen_runs)
    for i in range(use_cores):
        pool_list = pool[:int(pool_split[i])]
        model_names = []
        for j in pool_list:
            model_names.append("model_" + str(j) + "_voxet.task")
        egen_calc_vox_ens = f'''ef.calc_voxet_ensemble('{path_to_model}', {nx}, {ny}, {nz}, model_from={pool_list[0]}, model_to={pool_list[-1]}, litho={litho}, scalar={scalar}, scalar_grads={scalar_grads})\n'''
        #egen_exec_vox_batch = f'''os.system('cmd /c egen_batch_{f}.bat')'''
        pool = pool[int(pool_split[i]):]
        f.write(egen_calc_vox_ens)
        #print(egen_calc_vox_ens)

    pool = np.arange(0, egen_runs)
    for k in range(use_cores):
        pool_list = pool[:int(pool_split[k])]
        calc_vox_name = f'''model_{pool_list[0]}_{pool_list[-1]}_voxet.task'''
        egen_create_vox_batch = f'''ef.egen_create_batch_auto('{calc_vox_name}', run = 'voxrun{k}')\n'''
        pool = pool[int(pool_split[g]):]
        #print(egen_create_vox_batch)
        f.write(egen_create_vox_batch)

    # TODO this bit below and weird batch file creation
    # for f in range(use_cores):
    #     egen_exec_vox_batch = f'''os.system('cmd /c egen_batch_{f}.bat')'''
    #     f.write(egen_exec_vox_batch)


    # Step 6 - import voxets and compute summary statistics
    change_dir2 = f'''os.chdir("{path_to_model}")\n'''
    f.write(change_dir2)

    if litho is True:
        egen_summary_litho_stats = f'''es.stats_gocad_voxet(directory = './voxets', type = "GOCAD_LITHO", model_label='{model_label}', card = {card}, ent = {ent})\n'''
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
