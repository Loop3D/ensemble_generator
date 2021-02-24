# import egen_func as ef
# import perturber_func as pf
# import m2l_export_egen as ex
# import egen_summary_stats as es
import multiprocessing as mp
import ensemble_generator.stats_utils
#import time
import numpy as np
import pathlib
import os, sys
import importlib

#class_file = 'Geomodel_parameters'

def run_egen(class_file):
    params = importlib.import_module(class_file)

    # open egen execute .py file
    os.chdir(params.egen_project.path_to_model)
    path = pathlib.PurePosixPath(params.egen_project.path_to_model) / params.egen_project.model_task
    path_geomodeller = pathlib.PurePosixPath(params.egen_project.path_to_geomodeller)
    f = open(path.parent / 'egen_execute.py', 'w')
#%%
    # Step 1 - import modules

    modules = '''
import sys, os, subprocess, time
sys.path.append(os.path.abspath('C:/Users/Mark/Cloudstor/EGen/ensemble_generator/python'))
import egen_func as ef
import perturber_func as pf
import m2l_export_egen as ex
import egen_summary_stats as es
import egen_parse_geomodeller as ep
'''

    f.write(modules)
#%% Step 2 - set paths
    modelpath = f'''sys.path.append(os.path.abspath('{path.parent}'))\n'''
    f.write(modelpath)
    egen_path = f'''ef.egen_paths('{path_geomodeller}', '{path.parent}')\n'''
    f.write(egen_path)

#%% Step 3 Create task from m2l OR parse task from exported from Geomodeller project

    # if data from m2l, build task file from data, compute task file, export litho voxet
    if params.egen_project.source_geomodeller is False:
        egen_l2gm = f'''ex.l2gm_ensemble('{path.parent}', './tmp/', './output/', './dtm/{params.egen_project.DTM_name}', save_faults = {params.egen_project.save_faults}, model_from=0, model_to=0, series_calc="{params.egen_project.series_list}", fault_calc = {params.egen_project.fault_list})\n'''
        f.write(egen_l2gm)
        egen_l2gm_compute = f'''ef.egen_create_batch('orig_model.task')\nos.system(cmd /c egen_batch.bat'''
    # if data from geomodeller model, create task from xml, parse task
    if params.egen_project.source_geomodeller is True:
        egen_xml_to_task = f'''ef.egen_xml_to_task('{params.egen_project.path_to_model}','{params.egen_project.model_xml}', '{params.egen_project.model_task}')\n'''
        egen_x2task_batch = f'''ef.egen_create_batch('xml_to_task.task')\n'''
        exec_xml_to_task = f'''os.system('cmd /c egen_batch.bat')\n'''
        egen_parse_task = f'''ep.parse_gm_task('{params.egen_project.path_to_model}/{params.egen_project.model_task}')\n'''

        f.write(egen_xml_to_task)
        f.write(egen_x2task_batch)
        f.write(exec_xml_to_task)
        f.write(egen_parse_task)


#%% Step 4 - calculate models and export voxet/s

        # calculate original model and export voxet
        egen_calc_orig = f'''ef.egen_calc_original('{params.egen_project.model_xml}')\n'''
        egen_calc_orig_batch = f'''ef.egen_create_batch('{params.egen_project.model_task}')\n'''
        exec_calc_orig = f'''os.system('cmd /c egen_batch.bat')\n'''
        egen_voxet_orig = f'''ef.egen_orig_model_voxet('{params.egen_project.path_to_model}','{params.egen_project.model_xml}',{params.egen_project.nx}, {params.egen_project.ny}, {params.egen_project.nz}, litho={params.egen_project.litho}, scalar={params.egen_project.scalar}, scalar_grads={params.egen_project.scalar_grads})\n'''
        egen_voxet_orig_batch = f'''ef.egen_create_batch('orig_model_voxet.task')\n'''
        exec_voxet_orig = f'''os.system('cmd /c egen_batch.bat')\n'''
        f.write(egen_calc_orig)
        f.write(egen_calc_orig_batch)
        f.write(exec_calc_orig)
        f.write(egen_voxet_orig)
        f.write(egen_voxet_orig_batch)
        f.write(exec_voxet_orig)

#%% Step 5 - perturb interfaces

    # f.write(f'''os.chdir('./output')\n''')
    egen_int_forms_pert = f'''pf.perturb_interface({params.egen_project.egen_runs}, {params.egen_project.error_gps}, file_type='contacts', distribution='{params.egen_project.distribution}', DEM={params.egen_project.DEM}, source_geomodeller={params.egen_project.source_geomodeller})\n'''
    f.write(egen_int_forms_pert)

    egen_ori_forms_pert = f'''pf.perturb_orient_vMF({params.egen_project.egen_runs}, {params.egen_project.kappa}, {params.egen_project.error_gps}, file_type='contacts', loc_distribution='{params.egen_project.loc_distribution}', DEM={params.egen_project.DEM}, source_geomodeller={params.egen_project.source_geomodeller})\n'''
    f.write(egen_ori_forms_pert)

    if params.egen_project.source_geomodeller is False:
        '''we do this because the task file parser puts faults and orientations into the same file'''
        '''if the data comes from directly from m2l, the interfaces and faults are delivered in separate files'''
        if params.egen_project.save_faults is True:
            egen_int_fault_pert = f'''pf.perturb_interface({params.egen_project.egen_runs}, {params.egen_project.error_gps}, file_type='faults', distribution='{params.egen_project.distribution}', DEM={params.egen_project.DEM}, source_geomodeller={params.egen_project.source_geomodeller})\n'''
            f.write(egen_int_fault_pert)
            egen_ori_faults_pert = f'''pf.perturb_orient_vMF({params.egen_project.egen_runs}, {params.egen_project.kappa}, {params.egen_project.error_gps}, file_type='faults', loc_distribution='{params.egen_project.loc_distribution}', DEM={params.egen_project.DEM}, source_geomodeller={params.egen_project.source_geomodeller})\n'''
            f.write(egen_ori_faults_pert)

#%% Step 6 - build the ensemble

    #egen_task_timestart = f'''t_start = time.time()\n'''
    if sys.platform == "win32":
        egen_taskbuilder = f'''ef.task_builder_windows('{params.egen_project.path_to_model}', '{params.egen_project.model_task}', '{class_file}')\n'''
    else:
        egen_taskbuilder = f'''ef.task_builder('{params.egen_project.path_to_model}', '{params.egen_project.model_task}', '{class_file}')\n'''
    #egen_task_timeend = f'''t_end = time.time()\nprint(str(t_end-t_start))\n'''
    #egen_task_time_taskbuild = f'''taskb_time = t_end-t_start\ntext_file = open("taskbuilder_time.txt", "w")\ntext_file.write(str(taskb_time))\ntext_file.close()\n'''
    #f.write(egen_task_timestart)
    f.write(egen_taskbuilder)
    #f.write(egen_task_timeend)
    #f.write(egen_task_time_taskbuild)
#%% Step 7 - compute the ensemble and export lithos

    #change_dir_1 = f'''os.chdir('./ensemble')\n'''
    #f.write(change_dir_1)

    # uses parallel processing for speed
    num_cores = mp.cpu_count()
    use_cores = int(num_cores*.5)

    pool_split = stats_utils.split(params.egen_project.egen_runs, use_cores)
    pool = np.arange(0, params.egen_project.egen_runs)
    #pool_list = []
    for g in range(use_cores):
        pool_list = pool[:int(pool_split[g])]
        calc_model_names = []
        for h in pool_list:
            calc_model_names.append(f'''{path.stem}_{h}.task''')

        egen_create_batch = f'''ef.egen_create_batch_auto({calc_model_names}, {g})\n'''
        pool = pool[int(pool_split[g]):]
        f.write(egen_create_batch)

    for e in range(use_cores):
        #egen_exec_batch = f'''os.system('cmd /c egen_batch_{e}.bat')\n'''
        egen_exec_batch = f'''subprocess.call('egen_batch_{e}.bat')\n'''
        f.write(egen_exec_batch)

    pool = np.arange(0, params.egen_project.egen_runs)
    # for i in range(use_cores):
    #     pool_list = pool[:int(pool_split[i])]
    #     model_names = []
    #     for j in pool_list:
    #         model_names.append("model_" + str(j) + "_voxet.task")
    #     egen_calc_vox_ens = f'''ef.calc_voxet_ensemble('{path}', {params.egen_project.nx}, {params.egen_project.ny}, {params.egen_project.nz}, model_from={pool_list[0]}, model_to={pool_list[-1]}, litho={params.egen_project.litho}, scalar={params.egen_project.scalar}, scalar_grads={params.egen_project.scalar_grads})\n'''
    #     #egen_exec_vox_batch = f'''os.system('cmd /c egen_batch_{f}.bat')'''
    #     pool = pool[int(pool_split[i]):]
    #     f.write(egen_calc_vox_ens)
    #     #print(egen_calc_vox_ens)

    pool = np.arange(0, params.egen_project.egen_runs)
    # for k in range(use_cores):
    #     pool_list = pool[:int(pool_split[k])]
    #     calc_vox_name = f'''model_{pool_list[0]}_{pool_list[-1]}_voxet.task'''
    #     egen_create_vox_batch = f'''ef.egen_create_batch_auto('{calc_vox_name}', run = 'voxrun{k}')\n'''
    #     pool = pool[int(pool_split[g]):]
    #     #print(egen_create_vox_batch)
    #     f.write(egen_create_vox_batch)

    # TODO this bit below and weird batch file creation
    # for f in range(use_cores):
    #     egen_exec_vox_batch = f'''os.system('cmd /c egen_batch_{f}.bat')'''
    #     f.write(egen_exec_vox_batch)


#%% Step 8 - import voxets and compute summary statistics
    # change_dir2 = f'''os.chdir("{path.parent}")\n'''
    # f.write(change_dir2)

    if params.egen_project.litho is True:
        egen_summary_litho_stats = f'''es.stats_gocad_voxet(directory = '{path.parent}/voxets', type = "gocad_litho", model_label='{params.egen_project.model_label}', card = {params.egen_project.card}, ent = {params.egen_project.ent}, propor= {params.egen_project.propor}, export = {params.egen_project.export}, air = {params.egen_project.air})\n'''
        f.write(egen_summary_litho_stats)
    if params.egen_project.scalar is True:
        # TODO enter scalar voxet output
        egen_summary_scalar_stats = f'''es.stats_gocad_voxet('{path.parent}/voxets', type = "TODO", card = {card}, ent = {ent}'''
        f.write(egen_summary_scalar_stats)
    if params.egen_project.scalar_grads is True:
        # TODO enter scalar voxet grad output
        egen_summary_scalar_stats = f'''es.stats_gocad_voxet('{path.parent}/voxets', type = "TODO", card = {card}, ent = {ent}'''
        f.write(egen_summary_scalar_stats)
    f.close()
