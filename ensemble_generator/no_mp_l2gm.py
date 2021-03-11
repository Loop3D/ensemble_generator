# testing and timing multiprocessing - this one is the control

#import multiprocessing as mp
import ensemble_generator.m2l_export_egen as ex
import time

start_time = time.time()
series_c = (['Turee_Creek_Group', 'Hamersley_Group', 'Fortescue_Group'])
ex.l2gm_ensemble('C:/Users/Mark/Cloudstor/EGen/test_data3', './tmp/', './output/', './dtm/dtm_rp.tif', save_faults = True, model_from=0, model_to=10, series_calc=series_c)
print(time.time() - start_time)