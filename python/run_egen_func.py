import egen_func as ef
import perturber_func as pf
import m2l_export_egen as ex
import multiprocessing as mp
import stats_utils
import time
import numpy as np

# debug


def run_egen(par_file=None):
    #load Egen_par.py
    exec(open("EGen_par.py").read())

    # Step 1 - set paths
    egen_path = f'''ef.egen_path('{path_to_geomodeller}', '{path_to_model}')'''
    f.write(egen_path)

    # Step 2 - perturb interfaces
    egen_int_forms_pert = f'''pf.perturb_interface({egen_runs}, {error_gps}, file_type='contacts', distribution='{distribution}', DEM={DEM})'''
    egen_int_fault_pert = f'''pf.perturb_interface({egen_runs}, {error_gps}, file_type='faults', distribution='{distribution}', DEM={DEM})'''
    f.write(egen_int_forms_pert)
    f.write(egen_int_fault_pert)

    # Step 3 - perturb orientations
    egen_ori_forms_pert = f'''pf.perturb.orient.vMF({egen_runs}, {kappa}, {error_gps}, file_type='contacts', loc_distribution='{loc_distribution}', DEM={DEM})'''
    egen_ori_fault_pert = f'''pf.perturb.orient.vMF({egen_runs}, {kappa}, {error_gps}, file_type='faults', loc_distribution='{loc_distribution}', DEM={DEM})'''
    f.write(egen_ori_forms_pert)
    f.write(egen_ori_fault_pert)


    # Step 4 - create new model task file with l2gm_ensemble
    # uses parallel processing for speed
    num_cores = mp.cpu_count()
    use_cores = int(num_cores*.8)
    egen_runs = 100
    # TODO create model_to and model_from starting numbers
    # single processing at the moment (boring)
    egen_l2gm = f'''ex.l2gm_ensemble('{path_to_model}', './tmp/', './output/', './dtm/{DTM_name}', save_faults = {save_faults}, model_from=0, model_to={egen_runs}, series_calc={series_c})'''

    # Step 5 - compute models and export voxets

    pool_split = stats_utils.split(egen_runs, use_cores)
    pool = np.arange(0, egen_runs)
    pool_list = []
    for i in range(use_cores):
        pool_list = pool[:int(pool_split[i])]
        pool = pool[int(pool_split[i]):]
        model_names = []
        for j in pool_list:
            model_names.append("model_" + str(j) + "_voxet.task")
        egen_calc_vox_ens = f'ef.calc_voxet.ensemble({path_to_model}, {nx}, {ny}, {nz}, model_from={pool_list[0]}, model_to={pool_split[-1]}, litho={litho}, scalar={scalar}, scalar_grids={scalar_grids})'
        model_names = ','.join(map(str, model_names))
        egen_create_batch = f'ef.egen_create_batch_auto({model_names})'


        f.write(egen_calc_vox_ens)



    block1 = {0,16}
    for i in range()
    calc_models_voxets = f'''ef.calc_voxet_ensemble('{path_to_model}, {nx}, {ny}, {nz}, model_from'''
