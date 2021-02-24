testfile_loc = 'C:/Users/Mark/Cloudstor/EGen/tasks/save_model.task'
testfile_loc1 = 'C:/Users/Mark/Cloudstor/EGen/tasks/win_compute_model_and_save_litho_voxet.task'
project_task_loc = 'C:/Users/Mark/Cloudstor/EGen/models/Geomodel_Demo/output/project_export.task'
testfile = open(testfile_loc, 'r')
testfile.read()
print(_)
testfile.close()

import pandas as pd

testfile = pd.read_csv(testfile_loc, sep = '\n')
testfile1 = pd.read_csv(testfile_loc1, sep = '\n')
testfile = pd.read_csv(testfile_loc, sep='{', delimiter='}')

testfile2 = pd.read_csv(testfile_loc1)

testfile2 = pd.read_csv(testfile_loc1, sep='{', delimiter='}')

project_task = pd.read_csv(project_task_loc, sep = '\n', header = None)

#Yerrida Basin prospectivity test
testfile_loc = 'E:/Projects/Capricorn/3Dmodels/Yerrida/YerridaBasin_masked_10Oct2017'
testfile_loc1 = 'E:/Projects/Capricorn/3Dmodels/Yerrida/YerridaBasin_masked_10Oct2017/win_compute_model_and_save_litho_voxet.task'
project_task_loc = 'E:/Projects/Capricorn/3Dmodels/Yerrida/YerridaBasin_masked_10Oct2017/project_export.task'
