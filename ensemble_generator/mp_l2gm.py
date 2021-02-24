# testing and timing multiprocessing

import multiprocessing as mp
import ensemble_generator.m2l_export_egen as ex
import time

start_time = time.time()
series_c = (['Turee_Creek_Group', 'Hamersley_Group', 'Fortescue_Group'])
p1 = mp.Process(target=ex.l2gm_ensemble('C:/Users/Mark/Cloudstor/EGen/test_data3', './tmp/', './output/', './dtm/dtm_rp.tif', save_faults = True, model_from=0, model_to=5, series_calc=series_c))
p1.start()
p2 = mp.Process(target=ex.l2gm_ensemble('C:/Users/Mark/Cloudstor/EGen/test_data3', './tmp/', './output/', './dtm/dtm_rp.tif', save_faults = True, model_from=6, model_to=10, series_calc=series_c))
p2.start()
print(time.time() - start_time)