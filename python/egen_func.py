import numpy as np
import sys, os, glob
import pandas as pd

def egen_paths(geomodeller, model, data=None):
    """define paths for different parts of the process"""
    # arg path inputs need to be raw string to avoid escape issue eg. "\U" in C:\Users etc
    global path_geomodeller1
    global path_geomodeller2
    global path_model
    global path_to_model
    global path_output
    global path_data
    path_geomodeller1 = f'{geomodeller}/bin'
    path_geomodeller1 = path_geomodeller1.replace("\\", "/")
    path_geomodeller2 = f'{geomodeller}/bin/server'
    path_geomodeller2 = path_geomodeller2.replace("\\", "/")
    path_model = model
    path_to_model = model
    # path_model = "%r" % model
    path_model = path_model.replace("\\", "/")
    path_to_model = path_to_model.replace("\\", "/")
    path_output = f'{model}/output'  # task files will be stored in output directory. ?Separate one - unnecessary at this point
    path_output = path_output.replace("\\", "/")

    if data is not None:
        path_data = data.replace("\\", "/")
    else:
        data = None
    return #path_geomodeller1, path_geomodeller2, path_model, path_to_model, path_output


def egen_xml_to_task(model_name):
    """generate task file from xml"""
    # emulates exporter.task
    # path_model; path_outputs should be prior set with egen paths
    # paths areas input, so can be explicit or relative.
    import os
    global g_model_name  # name of model without .xml for naming use in exports etc.
    if model_name.find(".xml") == -1:
        model_name = model_name + str(".xml")
    if model_name.find(".xml") != -1:
        g_model_name = model_name
    else:
        g_model_name = model_name.replace(".xml", "")
    if not os.path.exists(path_output):
        os.makedirs(path_output)
    orig_task = open(f'{path_output}/xml_to_task.task', "w")
    task = f'''GeomodellerTask {{
        WriteBatchFile {{
            filename: "{path_model}/{model_name}"
                Task_Name: "{path_output}/project_export.task"
                convertSection_InterfacesTo3D: true
                convertSection_FoliationTo3D: true
                exportBoreholesToCSV: false
                csv_path: "{path_output}/"
                exportToGeomodellerTempDirectory: false
            }}
        }}'''
    orig_task.write(task)
    orig_task.close()
    return


def egen_calc_original(model_name):
    '''calculate original model'''
    global g_model_name
    g_model_name = model_name

    orig_task = open(f'{path_output}/calc_{model_name}', "w")
    task = '''GeomodellerTask {
    OpenProjectNoGUI {
        filename: "%s/%s"
        }
    }
GeomodellerTask {
    ComputeModel {
        SeriesList {
            node: "all"
        }
        FaultList {
            node: "all"
        }
        SectionList {
            node: "all"
        }
    }
}
GeomodellerTask {
    SaveProjectAs {
        filename: "%s/%s"
        log: "projectsave.rpt"
        }
    }
GeomodellerTask {
    CloseProjectNoGUI {
    }
}
    ''' % (path_model, g_model_name, path_model, g_model_name)
    orig_task.write(task)
    orig_task.close()
    return


def egen_orig_model_voxets(nx, ny, nz, litho=None, scalar=None, scalar_grads=None):
    """task for exporting voxets from the original model - litho, scalar, gradients etc"""
    """assumes you want the same voxel parameters for all voxets"""
    """if different cell sizes are needed, repeat this function with the appropriate params and voxet"""
    open_task = '''GeomodellerTask {
    OpenProjectNoGUI {
        filename: "%s/%s"
    }
}\n''' % (path_model, g_model_name)
    if litho is not None:
        # save out lithology voxet
        task1 = '''GeomodellerTask {
                SaveLithologyVoxet {
                    nx:%d
                    ny:%d
                    nz:%d
                    LithologyVoxetFileStub: "%s/orig_gocad_litho"
                    }
                }\n''' % (nx, ny, nz, path_output)
    else:
        task1 = ""
    if scalar is not None:
        task2 = '''GeomodellerTask {
                SavePotentialGradientVoxet {
                    nx: %d
                    ny: %d
                    nz: %d
                    Just_Gradients: false
                    VoxetFileStub: "%s/orig_gocad_scalar"
                    }
                }\n''' % (nx, ny, nz, path_output)
    else:
        task2 = ""
    if scalar_grads is not None:
        task3 = '''GeomodellerTask {
                SavePotentialGradientVoxet {
                    nx: %d
                    ny: %d
                    nz: %d
                    Just_Gradients: true
                    VoxetFileStub: "%s/orig_gocad_scalar_grads"
                    }
                }\n''' % (nx, ny, nz, path_output)
    else:
        task3 = ""
    close_task = '''GeomodellerTask {
    CloseProjectNoGUI {
    }
}'''
    orig_model_voxet = open(f'{path_output}/orig_model_voxet.task', "w")
    orig_model_voxet.write(open_task + task1 + task2 + task3 + close_task)
    orig_model_voxet.close()
    return


def egen_create_batch(*tasks): # need to fix how the tasks args can be added to the batch without explicit indexing
    '''create batch file .bat for windows for correct sequence of task file execution'''
    # create a switch for linux - .sh and path setting will be different
    task_list = [None] * len(tasks)
    batch = f"SET PATH=%PATH%;{path_geomodeller1}\n"
    for i in range(0, len(tasks)):
        batch = batch + "geomodellerbatch " + tasks[i] + "\n"
    egen_batch = open(f'{path_model}/output/egen_batch.bat', "w")
    egen_batch.write(batch)
    egen_batch.close()
    return

def egen_create_batch_auto(tasks, run): # need to fix how the tasks args can be added to the batch without explicit indexing
    '''create batch file .bat for windows for correct sequence of task file execution
    this version of the function accepts a list of task names of input'''

    # create a switch for linux - .sh and path setting will be different
    batch1 = f"SET PATH=%PATH%;{path_geomodeller1}\n"
    egen_batch = open(f'{path_model}/egen_batch_{run}.bat', "w")
    egen_batch.write(batch1)
    for m in range(0, len(tasks)):
        batch2 = "geomodellerbatch " + str(tasks[m]) + "\n"
        egen_batch.write(batch2)
    egen_batch.close()
    return

def egen_create_voxet_ensemble_batch(samples): # need to fix how the tasks args can be added to the batch without explicit indexing
    '''create batch file .bat for windows for correct sequence of task file execution'''
    # create a switch for linux - .sh and path setting will be different
    task_list = [None] * samples * 2 # '2' because we are creating task entries for 1) model_n.task and 2) model_n_voxet.task

    batch = f"SET PATH=%PATH%;{path_geomodeller1}\n"
    for i in range(samples):
        batch = batch + "geomodellerbatch model_" + str(i) + "_voxet.task\n"
    egen_batch = open(f'{path_model}/ensemble/egen_voxet_ensemble_batch.bat', "w")
    egen_batch.write(batch)
    egen_batch.close()
    return

def egen_MC_cokrig_params(range = None, interface = None, orientation = None, drift = None):
    '''set model interpolation parameters using cokriging'''
    '''Range default = 10000.0]; Contacts_Nugget_Effect [default = 0.000001];
     Gradients_Nugget_Effect [default = 0.01]; FaultDriftEquationDegree = 4 [default = 1]'''
    if range is None:
        range = 10000.0
    if interface is None:
        interface = 0.000001
    if orientation is None:
        orientation = 0.01
    if drift is None:
        drift = 1
    task = f'''GeomodellerTask {{
    OpenProjectNoGUI {{
        filename: "{path_model}/{g_model_name}"
    }}
    }}\n
    GeomodellerTask {{
        ComputeModel {{
            SeriesList
                {{
        node: "all"
                }}
        SectionList {{
        node: "all"
                }}
        ModelInterpolationParameters {{
            Range: {range}
            Contacts_Nugget_Effect: {interface}
            Gradients_Nugget_Effect: {orientation}
            FaultDriftEquationDegree: {drift}
            }}
    }}\n
    GeomodellerTask {{
    CloseProjectNoGUI {{
    }}
    }}'''

    egen_interpolate = open(f'{path_output}/egen_MC_cokrig_params.task', "w")
    egen_interpolate.write(task)
    egen_interpolate.close()
    return

def calc_voxet_ensemble(model_path, nx, ny, nz, model_from = None, model_to = None, litho = None, scalar=None, scalar_grads=None):
    """task for calculating and an ensemble of models, then
    exporting voxets from the original model - litho, scalar, gradients etc"""
    """assumes you want the same voxel parameters for all voxets"""
    """if different cell sizes are needed, repeat this function with the appropriate params and voxet"""
    '''path = path to model tasks
    nx, ny, nz = number of cells on the respective axes 
    model_from, model_to = options here for splitting the ensemble into group for calc on multiple cores
    litho, scalar, scalar_grads = None. Set to 'True' to boolean to export litho, scalar
     scalar gradient voxets (gocad binary format).'''
    #task_path = model_path
    ensemble_path = model_path + "/ensemble"
    os.chdir(model_path)
    if not os.path.exists("./voxets"):
        os.makedirs("./voxets")

    pattern = "*.xml"
    xml_names = glob.glob(pattern)
    voxet_path = "../voxets"
    os.chdir(ensemble_path)

    # if 'model_from' != locals():
    #     model_from = 0
    # if 'model_to' != locals():
    #     model_to = len(xml_names)
    if model_from is None:
        model_from = 0
    if model_to is None:
        model_to = len(xml_names)

    model_voxet = open(f'{ensemble_path}/model_{model_from}_{model_to}_voxet.task', "w")
    for m in range(model_from, model_to):
        model_name = xml_names[m]
        open_task = '''GeomodellerTask {
            OpenProjectNoGUI {
                filename: "%s"
            }
        }\n''' % (model_name)
        if litho is not None:
            # save out lithology voxet
            task1 = '''GeomodellerTask {
            SaveLithologyVoxet {
                nx:%d
                ny:%d
                nz:%d
                LithologyVoxetFileStub: "%s/model_%i_gocad_litho"
                }
            }\n''' % (nx, ny, nz, voxet_path, m)
        else:
            task1 = ""
        if scalar is not None:
            task2 = '''GeomodellerTask {
            SavePotentialGradientVoxet {
                nx: %d
                ny: %d
                nz: %d
                Just_Gradients: false
                VoxetFileStub: "%s/model_%i_gocad_scalar"
                }
            }\n''' % (nx, ny, nz, voxet_path, m)
        else:
            task2 = ""
        if scalar_grads is not None:
            task3 = '''GeomodellerTask {
            SavePotentialGradientVoxet {
                nx: %d
                ny: %d
                nz: %d
                Just_Gradients: true
                VoxetFileStub: "%s/model_%i_gocad_scalar_grads"
                }
            }\n''' % (nx, ny, nz, voxet_path, m)
        else:
            task3 = ""
        close_task = '''GeomodellerTask {
            CloseProjectNoGUI {
            }
        }'''

        model_voxet.write(open_task + task1 + task2 + task3 + close_task)
    model_voxet.close()

    return

#%% task builder

# debug
filename = 'realInit.task'
path = pathlib.Path('C:/Users/Mark/Cloudstor/EGen/ObjFunc_model') / filename



def task_builder(path, filename, egen_runs, input='./output', *kwargs):
    #task_file = open(path + '/' + filename, "r")
    contents = pd.read_csv(path + '/' + filename, sep='\t', header=None)
    #contents = task_file.readlines()
    #contents = (contents)
    # get first file part - everything up to where the data points are added
    end_line = contents[0]==('  Add3DInterfacesToFormation {')
    idx = [a for a, x in enumerate(end_line) if x] # make list of row indices where the string above is found
    task_pt1 = contents[0:(idx[0]-1)]

    #task_output = open('task_test.task', 'w')
    #task_output.write(str(task_pt1))
    #task_output.close()
    for i in range(egen_runs):
        new_contacts = pd.read_csv(f'{path}/output/contacts_{i}.csv')
        new_orientations = pd.read_csv(f'{path}/output/contacts_orient_{i}.csv')
        p_idx = new_orientations['polarity'] == 0 #  replace polarity 1 = 'Normal_Polarity'; 0 = 'Reverse_Polarity'
        new_orientations['polarity'][p_idx] = 'Reverse_Polarity' # this may cause trouble (chained indexing), I have changed the parser to not convert polarity flags
        new_orientations['polarity'][p_idx==False] = 'Normal_Polarity'

        tmp_contact_formations = new_contacts.formation.unique()
        tmp_orient_formations = new_orientations.formation.unique()
        tmp_cont_chunk = pd.DataFrame(['Geomodeller Task {']) #  build the 'chunk' of the task file with contact info
        tmp_orient_chunk = pd.DataFrame(['Geomodeller Task {']) #  build the 'chunk' of the task file with orientation info
        for k in range(len(tmp_contact_formations)):
            idx = new_contacts['formation']==tmp_contact_formations[k]
            tmp_contacts = new_contacts[idx]
            tmp_cont_chunk = tmp_cont_chunk.append(['Add3DInterfacesToFormation {'])
            for l in range(len(tmp_contacts)):
                tmp_cont_chunk = tmp_cont_chunk.append(['point {'])
                tmp_cont_chunk = tmp_cont_chunk.append([f'x: {tmp_contacts.iloc[l, 1]}'])
                tmp_cont_chunk = tmp_cont_chunk.append([f'y: {tmp_contacts.iloc[l, 2]}'])
                tmp_cont_chunk = tmp_cont_chunk.append([f'z: {tmp_contacts.iloc[l, 3]} }}'])
            tmp_cont_chunk = tmp_cont_chunk.append([f'formation: "{tmp_contact_formations[k]}" }}'])
            tmp_cont_chunk = tmp_cont_chunk.append([''])
        for j in range(len(tmp_orient_formations)):
            idx = new_orientations['formation'] == tmp_orient_formations[j]
            tmp_orient = new_orientations[idx]
            tmp_orient_chunk = tmp_orient_chunk.append(['Add3DFoliationToFormation {'])
            tmp_orient_chunk = tmp_orient_chunk.append([f'formation: "{tmp_orient_formations[j]}" {{'])
            for h in range(len(tmp_orient)):
                tmp_orient_chunk = tmp_orient_chunk.append(['foliation {'])
                tmp_orient_chunk = tmp_orient_chunk.append(['Point3D {'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'x: {tmp_orient.iloc[h, 1]}'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'y: {tmp_orient.iloc[h, 2]}'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'z: {tmp_orient.iloc[h, 3]} }}'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'dip: {tmp_orient.iloc[h, 5]} }}'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'direction: {tmp_orient.iloc[h, 4]} }}'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'azimuth: {tmp_orient.iloc[h, 4]} }}'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'polarity: {tmp_orient.iloc[h, 6]} }}'])
            tmp_orient_chunk = tmp_orient_chunk.append([f'}}'])

    full_task = task_pt1.append(tmp_cont_chunk)
    full_task = full_task.append(tmp_orient_chunk)

    full_task.to_csv(f'{path.parent}/{path.stem}_{i}{path.suffix}', index=None, header=None, sep = '\t')



    new_contents =


