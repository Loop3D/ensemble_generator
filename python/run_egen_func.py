# import egen_func as ef
# import perturber_func as pf
# import m2l_export_egen as ex
# import egen_summary_stats as es
import multiprocessing as mp
import stats_utils
# import time
import numpy as np
import pathlib
# import os
import importlib

#class_file = 'Geomodel_parameters'

def run_egen(class_file):
    params = importlib.import_module(class_file)

    # open egen execute .py file
    #os.chdir(path_to_model)
    path = pathlib.PurePosixPath(params.egen_project.path_to_model) / params.egen_project.model_task
    path_geomodeller = pathlib.PurePosixPath(params.egen_project.path_to_geomodeller)
    f = open(path.parent / 'egen_execute.py', 'w')

    # Step 0 - import modules

    modules = '''
import sys, os
sys.path.append(os.path.abspath('C:/Users/Mark/Cloudstor/EGen/ensemble_generator/python'))
import egen_func as ef
import perturber_func as pf
import m2l_export_egen as ex
import egen_summary_stats as es
import egen_parse_geomodeller as ep
'''



    f.write(modules)
    # Step 1 - set paths
    modelpath = f'''sys.path.append(os.path.abspath('{path.parent}'))\n'''
    f.write(modelpath)
    egen_path = f'''ef.egen_paths('{path_geomodeller}', '{path.parent}')\n'''
    f.write(egen_path)

    # Step 2 - perturb interfaces

    #f.write(f'''os.chdir('./output')\n''')
    egen_int_forms_pert = f'''pf.perturb_interface({params.egen_project.egen_runs}, {params.egen_project.error_gps}, file_type='contacts', distribution='{params.egen_project.distribution}', DEM={params.egen_project.DEM}, source_geomodeller={params.egen_project.source_geomodeller})\n'''
    f.write(egen_int_forms_pert)
    if params.egen_project.source_geomodeller is False:
        egen_int_fault_pert = f'''pf.perturb_interface({params.egen_project.egen_runs}, {params.egen_project.error_gps}, file_type='faults', distribution='{params.egen_project.distribution}', DEM={params.egen_project.DEM}, source_geomodeller={params.egen_project.source_geomodeller})\n'''
        f.write(egen_int_fault_pert)




    # Step 3 - perturb orientations
    egen_ori_forms_pert = f'''pf.perturb_orient_vMF({params.egen_project.egen_runs}, {params.egen_project.kappa}, {params.egen_project.error_gps}, file_type='contacts', loc_distribution='{params.egen_project.loc_distribution}', DEM={params.egen_project.DEM}, source_geomodeller={params.egen_project.source_geomodeller})\n'''
    f.write(egen_ori_forms_pert)
    if params.egen_project.source_geomodeller is False:
        egen_ori_fault_pert = f'''pf.perturb_orient_vMF({params.egen_project.egen_runs}, {params.egen_project.kappa}, {params.egen_project.error_gps}, file_type='faults', loc_distribution='{params.egen_project.loc_distribution}', DEM={params.egen_project.DEM}, source_geomodeller={params.egen_project.source_geomodeller})\n'''
        f.write(egen_ori_fault_pert)


    # Step 4 - create new model task file with l2gm_ensemble

    # calculate original model and export voxet




    # uses parallel processing for speed
    num_cores = mp.cpu_count()
    use_cores = int(num_cores*.8)

    # single processing at the moment (boring)
    if params.egen_project.source_geomodeller is False:
        egen_l2gm = f'''ex.l2gm_ensemble('{path.parent}', './tmp/', './output/', './dtm/{params.egen_project.DTM_name}', save_faults = {params.egen_project.save_faults}, model_from=0, model_to={params.egen_project.egen_runs}, series_calc="{params.egen_project.series_list}", fault_calc = {params.egen_project.fault_list})\n'''
        f.write(egen_l2gm)

    if params.egen_project.source_geomodeller is True:
        egen_xml_to_task = f'''ef.egen_xml_to_task('{params.egen_project.model_xml}')\n'''
        exec_xml_to_task = f'''os.system('cmd /c '''
        egen_parse_task = f'''ep.parse_gm_task('{params.egen_project.path_to_model}/{params.egen_project.model_task}')\n'''
        egen_taskbuilder = f'''ef.task_builder('{params.egen_project.path_to_model}', '{params.egen_project.model_task}')\n'''
        f.write(egen_xml_to_task)
        f.write(exec_xml_to_task)
        f.write(egen_parse_task)
        f.write(egen_taskbuilder)

    # Step 5 - compute models and export voxets

    pool_split = stats_utils.split(params.egen_project.egen_runs, use_cores)
    pool = np.arange(0, params.egen_project.egen_runs)
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

    pool = np.arange(0, params.egen_project.egen_runs)
    for i in range(use_cores):
        pool_list = pool[:int(pool_split[i])]
        model_names = []
        for j in pool_list:
            model_names.append("model_" + str(j) + "_voxet.task")
        egen_calc_vox_ens = f'''ef.calc_voxet_ensemble('{path}', {params.egen_project.nx}, {params.egen_project.ny}, {params.egen_project.nz}, model_from={pool_list[0]}, model_to={pool_list[-1]}, litho={params.egen_project.litho}, scalar={params.egen_project.scalar}, scalar_grads={params.egen_project.scalar_grads})\n'''
        #egen_exec_vox_batch = f'''os.system('cmd /c egen_batch_{f}.bat')'''
        pool = pool[int(pool_split[i]):]
        f.write(egen_calc_vox_ens)
        #print(egen_calc_vox_ens)

    pool = np.arange(0, params.egen_project.egen_runs)
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
    change_dir2 = f'''os.chdir("{path}")\n'''
    f.write(change_dir2)

    if params.egen_project.litho is True:
        egen_summary_litho_stats = f'''es.stats_gocad_voxet(directory = './voxets', type = "GOCAD_LITHO", model_label='{params.egen_project.model_label}', card = {params.egen_project.card}, ent = {params.egen_project.ent}, propor= {params.egen_project.propor}, export = {params.egen_project.export}, air = {params.egen_project.air})\n'''
        f.write(egen_summary_litho_stats)
    if params.egen_project.scalar is True:
        # TODO enter scalar voxet output
        egen_summary_scalar_stats = f'''es.read_gocad_voxet('./voxets', type = "TODO", card = {card}, ent = {ent}'''
        f.write(egen_summary_scalar_stats)
    if params.egen_project.scalar_grads is True:
        # TODO enter scalar voxet grad output
        egen_summary_scalar_stats = f'''es.read_gocad_voxet('./voxets', type = "TODO", card = {card}, ent = {ent}'''
        f.write(egen_summary_scalar_stats)
    f.close()
