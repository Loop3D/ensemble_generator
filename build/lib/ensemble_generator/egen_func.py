import numpy as np
import sys, os, glob, pathlib, csv, importlib
import pandas as pd
#from Geomodel_parameters import egen_project

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


def egen_xml_to_task(path_to_model, model_xml, model_task):
    """generate task file from xml"""
    # emulates exporter.task
    # path_model; path_outputs should be prior set with egen paths
    # paths areas input, so can be explicit or relative.
    import os
    global g_model_xml  # name of model without .xml for naming use in exports etc.
    if model_xml.find(".xml") == -1:
        model_xml = model_xml + str(".xml")
    if model_xml.find(".xml") != -1:
        g_model_xml = model_xml
    else:
        g_model_xml = model_xml.replace(".xml", "")
    # if not os.path.exists(path_output):
    #     os.makedirs(path_output)
    orig_task = open(f'{path_to_model}/xml_to_task.task', "w")
    task = f'''GeomodellerTask {{
        WriteBatchFile {{
            filename: "{path_to_model}/{model_xml}"
                Task_Name: "{path_to_model}/{model_task}"
                convertSection_InterfacesTo3D: true
                convertSection_FoliationTo3D: true
                exportBoreholesToCSV: false
                csv_path: "{path_to_model}/output/"
                exportToGeomodellerTempDirectory: false
            }}
        }}'''
    orig_task.write(task)
    orig_task.close()
    return


def egen_calc_original(model_xml):
    '''calculate original model'''
    global g_model_xml
    g_model_xml = model_xml

    orig_task = open(f'{path_output}/calc_{model_xml}', "w")
    task = f'''GeomodellerTask {{
    OpenProjectNoGUI {{
        filename: "{path_model}/{g_model_xml}"
        }}
    }}
GeomodellerTask {{
    ComputeModel {{
        SeriesList {{
            node: "all"
        }}
        FaultList {{
            node: "all"
        }}
        SectionList {{
            node: "all"
        }}
    }}
}}


GeomodellerTask {{
    SaveProjectAs {{
        filename: "{path_model}/{g_model_xml}"
        log: "projectsave.rpt"
        }}
    }}
GeomodellerTask {{
    CloseProjectNoGUI {{
    }}
}}
    '''
    orig_task.write(task)
    orig_task.close()
    return


def egen_orig_model_voxet(path_to_model, model_xml, nx, ny, nz, litho=True, scalar=False, scalar_grads=False):
    """task for exporting voxets from the original model - litho, scalar, gradients etc"""
    """assumes you want the same voxel parameters for all voxets"""
    """if different cell sizes are needed, repeat this function with the appropriate params and voxet"""
    if not os.path.exists(f'''{path_to_model}/voxets'''):
        os.makedirs(f'''{path_to_model}/voxets''')
    open_task = f'''GeomodellerTask {{
    OpenProjectNoGUI {{
        filename: "{path_to_model}/{model_xml}"
    }}
}}\n'''
    if litho is True:
        # save out lithology voxet
        task1 = f'''GeomodellerTask {{
                SaveLithologyVoxet {{
                    nx:{nx}
                    ny:{ny}
                    nz:{nz}
                    LithologyVoxetFileStub: "{path_to_model}/voxets/orig_gocad_litho"
                    }}
                }}\n'''
    else:
        task1 = ""
    if scalar is True:
        task2 = f'''GeomodellerTask {{
                SavePotentialGradientVoxet {{
                    nx:{nx}
                    ny:{ny}
                    nz:{nz}
                    Just_Gradients: false
                    VoxetFileStub: "{path_to_model}/voxets/orig_gocad_scalar"
                    }}
                }}\n'''
    else:
        task2 = ""
    if scalar_grads is True:
        task3 = f'''GeomodellerTask {{
                SavePotentialGradientVoxet {{
                    nx:{nx}
                    ny:{ny}
                    nz:{nz}
                    Just_Gradients: true
                    VoxetFileStub: "{path_to_model}/voxets/orig_gocad_scalar_grads"
                    }}
                }}\n'''
    else:
        task3 = ""
    close_task = '''GeomodellerTask {
    CloseProjectNoGUI {
    }
}'''
    orig_model_voxet = open(f'{path_to_model}/orig_model_voxet.task', "w")
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
    egen_batch = open(f'{path_model}/egen_batch.bat', "w")
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
    egen_batch = open(f'{path_model}/egen_voxet_ensemble_batch.bat', "w")
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
        filename: "{path_model}/{g_model_xml}"
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

def calc_voxet_ensemble(path_model, nx, ny, nz, model_from = None, model_to = None, litho = None, scalar=None, scalar_grads=None):
    """task for calculating and an ensemble of models, then
    exporting voxets from the original model - litho, scalar, gradients etc"""
    """assumes you want the same voxel parameters for all voxets"""
    """if different cell sizes are needed, repeat this function with the appropriate params and voxet"""
    '''path = path to model tasks
    nx, ny, nz = number of cells on the respective axes 
    model_from, model_to = options here for splitting the ensemble into group for calc on multiple cores
    litho, scalar, scalar_grads = None. Set to 'True' to boolean to export litho, scalar
     scalar gradient voxets (gocad binary format).'''
    #task_path = path_model
    #ensemble_path = path_model + "/ensemble"
    ensemble_path = path_model
    os.chdir(path_model)
    if not os.path.exists("./voxets"):
        os.makedirs("./voxets")

    pattern = "*.xml"
    xml_names = glob.glob(pattern)
    voxet_path = "../voxets"
    #os.chdir(ensemble_path)

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
        model_xml = xml_names[m]
        open_task = '''GeomodellerTask {
            OpenProjectNoGUI {
                filename: "%s"
            }
        }\n''' % (model_xml)
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

def task_builder(path, filename, class_file):
#def task_builder(path, egen_runs, series_calc=None, krig_range=None, interface=None, orientation=None, drift=None, fault_calc=None, litho=True, scalar=False, scalar_grads=False):
    '''speed increase with numpy... maybe? instead of pandas'''
    func_params = importlib.import_module(class_file)
    path = pathlib.PurePosixPath(path) / filename
    #if not os.path.exists("./ensemble"):
    #    os.makedirs("./ensemble")
    #par_file = path.parent / par_file
    #exec(open(path.parent / par_file).read())
    #print(egen_runs)
    contents = pd.read_csv(path, sep='\t', header=None, quotechar='\0')  # + '/' + filename, sep='\t', header=None)
    fault_info = pd.read_csv(path.parent / "output/fault_info.csv")  # contents = task_file.readlines()
    strat_info = pd.read_csv(path.parent / "output/strat.csv")
    #contents = (contents)
    # get first file part - everything up to where the data points are added
    end_line = contents[0]=='  Add3DInterfacesToFormation {'
    idx = [a for a, x in enumerate(end_line) if x] # make list of row indices where the string above is found
    task_pt1 = contents[0:(idx[0]-1)]
    voxet_path = path.parent / "voxets/"
    if not os.path.exists("./voxets"):
        os.makedirs("./voxets")

    for i in range(func_params.egen_project.egen_runs):
        new_contacts = pd.read_csv(f'{path.parent}/output/contacts_{i}.csv')
        new_contacts = new_contacts.round(6)
        new_contacts['formation'] = new_contacts['formation'].str.strip()
        new_orientations = pd.read_csv(f'{path.parent}/output/contacts_orient_{i}.csv')
        new_orientations = new_orientations.round(6)
        new_orientations['formation'] = new_orientations['formation'].str.strip()
        #p_idx = new_orientations['polarity'] == 0 #  replace polarity 1 = 'Normal_Polarity'; 0 = 'Reverse_Polarity'
        #new_orientations['polarity'][p_idx] = 'Reverse_Polarity' # this may cause trouble (chained indexing), I have changed the parser to not convert polarity flags
        #new_orientations['polarity'][p_idx==False] = 'Normal_Polarity'

        tmp_contact_formations = new_contacts.formation.unique()
        tmp_orient_formations = new_orientations.formation.unique()
         #  build the 'chunk' of the task file with contact info
         #  build the 'chunk' of the task file with orientation info
        tmp_cont_chunk = pd.DataFrame([])
        tmp_orient_chunk = pd.DataFrame([])
        for k in range(len(tmp_contact_formations)):
            idx = new_contacts['formation']==tmp_contact_formations[k]
            tmp_contacts = new_contacts[idx]
            tmp_cont_chunk = tmp_cont_chunk.append(['\nGeomodellerTask {'])
            tmp_cont_chunk = tmp_cont_chunk.append(['Add3DInterfacesToFormation {'])
            tmp_cont_chunk = tmp_cont_chunk.append([f'\tformation: "{tmp_contact_formations[k]}"'])
            for l in range(len(tmp_contacts)):
                tmp_cont_chunk = tmp_cont_chunk.append(['point {'])
                tmp_cont_chunk = tmp_cont_chunk.append([f'x: {tmp_contacts.iloc[l, 0]}'])
                tmp_cont_chunk = tmp_cont_chunk.append([f'y: {tmp_contacts.iloc[l, 1]}'])
                tmp_cont_chunk = tmp_cont_chunk.append([f'z: {tmp_contacts.iloc[l, 2]} }}'])
            tmp_cont_chunk = tmp_cont_chunk.append([f'}}'])
            tmp_cont_chunk = tmp_cont_chunk.append([f'}}'])

        for j in range(len(tmp_orient_formations)):
            idx = new_orientations['formation'] == tmp_orient_formations[j]
            tmp_orient = new_orientations[idx]
            tmp_orient_chunk = tmp_orient_chunk.append(['\nGeomodellerTask {'])
            tmp_orient_chunk = tmp_orient_chunk.append(['Add3DFoliationToFormation {'])
            tmp_orient_chunk = tmp_orient_chunk.append([f'\tformation: "{tmp_orient_formations[j]}"'])
            for h in range(len(tmp_orient)):
                tmp_orient_chunk = tmp_orient_chunk.append(['foliation {'])
                tmp_orient_chunk = tmp_orient_chunk.append(['Point3D {'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'x: {tmp_orient.iloc[h, 0]}'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'y: {tmp_orient.iloc[h, 1]}'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'z: {tmp_orient.iloc[h, 2]} }}'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'\tdip: {tmp_orient.iloc[h, 4]}'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'\tdirection: {tmp_orient.iloc[h, 3]}'])
                #tmp_orient_chunk = tmp_orient_chunk.append([f'\tazimuth: {tmp_orient.iloc[h, 3]}'])
                tmp_orient_chunk = tmp_orient_chunk.append([f'\tpolarity: {tmp_orient.iloc[h, 5]} }}'])
            tmp_orient_chunk = tmp_orient_chunk.append([f'}}\n}}'])
        #tmp_orient_chunk = tmp_orient_chunk.append([f'}}'])

        full_task = task_pt1.append(tmp_cont_chunk)
        full_task = full_task.append(tmp_orient_chunk)

            ####
            # Calculate model lines

            #

            # assign default parameters
        if func_params.egen_project.series_list is None:
            #series_c = 'all'
            series_list = strat_info['series'].unique()
        else:
            series_list = func_params.egen_project.series_list

        if func_params.egen_project.series_list == 'all':
            series_list = strat_info['series'].unique()



        if func_params.egen_project.krig_range is None:
            krig_range = 10000.0
        if func_params.egen_project.interface is None:
            interface = 0.000001
        if func_params.egen_project.orientation is None:
            orientation = 0.01
        if func_params.egen_project.drift is None:
            drift = 1

        calc_model_str1 = [f'''GeomodellerTask {{\nComputeModel {{\nSeriesList {{''']
        #f.write(calc_model_str1)
        full_task = full_task.append(calc_model_str1)

        for sc in range(len(series_list)):
            calc_model_str_series_calc = [f'''node: "{series_list[sc]}"''']

        #    f.write(calc_model_str_series_calc)
            full_task = full_task.append(calc_model_str_series_calc)

        ## I don't think we need the 'section' to calculate as all data is 3D
        calc_model_str_section_list = [f'''}}\nSectionList {{\nnode: "all" }}''']
        #f.write(calc_model_str_section_list)
        full_task = full_task.append(calc_model_str_section_list)

        if func_params.egen_project.fault_list is not None:
            calc_model_str_fault_calc1 = [f'''\nFaultList {{''']
        #    f.write(calc_model_str_fault_calc1)
            full_task = full_task.append(calc_model_str_fault_calc1)

            # print(calc_model_str_fault_calc1)
            for fc in range(len(fault_info)):
                calc_model_str_fault_calc2 = [f'''node: "{fault_info.iat[fc,0]}"''']
                full_task = full_task.append(calc_model_str_fault_calc2)

            calc_model_str_fault_calc3 = ["}"]
        #   f.write(calc_model_str_fault_calc3)
            full_task = full_task.append(calc_model_str_fault_calc3)

        # set calc_uncertainty flag to false. When = true the calculation is much slower. We can't get the error estimate out at this point anyway.
        # can make this an if statement and add a parameter to the class
        calc_uncert = [f'''\ncalc_uncertainty: false''']
        full_task = full_task.append(calc_uncert)

        for ss in range(len(series_list)):
            calc_model_str2 = [f'''\nSeriesInterpolationParameters {{\nseries: "{series_list[ss]}"\nRange: {krig_range}\nContacts_Nugget_Effect: {interface}\nGradients_Nugget_Effect: {orientation}\nFaultDriftEquationDegree: {drift} }}''']
        #   f.write(calc_model_str2)
            full_task = full_task.append(calc_model_str2)

        calc_model_str3 = [f'''\n}}\n}}\n''']
        #f.write(calc_model_str3)
        full_task = full_task.append(calc_model_str3)

        ####
        calc_model_str4 = [f'GeomodellerTask {{\n    SaveProjectAs {{\n        filename: "{path.parent}/model_{i}.xml"\n    }}\n}}\n']
        full_task = full_task.append(calc_model_str4)

        if func_params.egen_project.litho is True:
            # save out lithology voxet
            vox_task1 = [f'''GeomodellerTask {{\nSaveLithologyVoxet {{\nnx: {func_params.egen_project.nx}\nny: {func_params.egen_project.ny}\nnz: {func_params.egen_project.nz}\nLithologyVoxetFileStub: "{voxet_path}/model_{i}_gocad_litho"\n}}\n}}\n''']
        else:
            vox_task1 = [""]
        if func_params.egen_project.scalar is True:
            vox_task2 = [f'''GeomodellerTask {{\nSavePotentialGradientVoxet {{\nnx: {func_params.egen_project.nx}\nny: {func_params.egen_project.ny}\nnz: {func_params.egen_project.nz}\nJust_Gradients: false\nVoxetFileStub: "{voxet_path}/model_{i}_gocad_scalar"\n}}\n}}\n''']
            # vox_task2 = ['''GeomodellerTask {
            # SavePotentialGradientVoxet {
            #     nx: %d
            #     ny: %d
            #     nz: %d
            #
            #     VoxetFileStub: "%s/model_%i_gocad_scalar"
            #     }
            # }\n'''] % (nx, ny, nz, voxet_path, i)
        else:
            vox_task2 = [""]
        if func_params.egen_project.scalar_grads is True:
            vox_task3 = [f'''GeomodellerTask {{\nSavePotentialGradientVoxet {{\nnx: {func_params.egen_project.nx}\nny: {func_params.egen_project.ny}\nnz: {func_params.egen_project.nz}\nJust_Gradients: true\nVoxetFileStub: "{voxet_path}/model_{i}_gocad_scalar_grads"\n}}\n}}\n''']
            # vox_task3 = ['''GeomodellerTask {
            # SavePotentialGradientVoxet {
            #     nx: %d
            #     ny: %d
            #     nz: %d
            #     Just_Gradients: true
            #     VoxetFileStub: "%s/model_%i_gocad_scalar_grads"
            #     }
            # }\n'''] % (nx, ny, nz, voxet_path, i)
        else:
            vox_task3 = [""]

        full_task = full_task.append(vox_task1)
        full_task = full_task.append(vox_task2)
        full_task = full_task.append(vox_task3)

        close_task = ['''GeomodellerTask {\nCloseProjectNoGUI {\n}\n}''']

        full_task = full_task.append(close_task)

        np.savetxt(f'''{path.parent}/{path.stem}_{i}{path.suffix}''', np.array(full_task), fmt='%s')
        #full_task.to_csv(f'{path.parent / path.stem}_{i}{path.suffix}', index=None, header=None, quoting=csv.QUOTE_NONE, quotechar="",  escapechar="\\")
        print(f'Run {i}')
    #debug
    # task_pt1.to_csv(path.parent / 'task_pt1.task', index=None, header=None, quoting=csv.QUOTE_NONE, quotechar="",  escapechar="\\")  #, quotechar="",  escapechar="\\")
    # temp_1 = full_task[0:1050]
    # temp_1.to_csv(path.parent / 'temp_pt1.task', index=None, header=None, quoting=csv.QUOTE_NONE, quotechar="",  escapechar="\\")  #, quotechar="",  escapechar="\\")
    #
    # full_task.to_csv(f'{path.parent / path.stem}_{i}{path.suffix}', index=None, header=None)
    # # new_contents =

def task_builder_windows(path, filename, class_file):
    '''This version of task builder uses the 'ReadAndImport3dData' call from the Geomodeller Protobuf API. At this point,
    this function only works on Windows using version: GeoModeller-4.0.8-2020-06-04-eb3e596cac2_WIN_x64.msi
    This function creates a task file imports new 3D data to the project, computes a scalar field, and exports
    a 3D voxet of given properties - lithology, scalar field, or scalar field gradients'''

    func_params = importlib.import_module(class_file)
    path = pathlib.PurePosixPath(path) / filename
    #if not os.path.exists("./ensemble"):
    #    os.makedirs("./ensemble")
    # par_file = path.parent / par_file
    # exec(open(path.parent / par_file).read())
    # print(egen_runs)
    contents = pd.read_csv(path, sep='\t', header=None, quotechar='\0')  # + '/' + filename, sep='\t', header=None)
    fault_info = pd.read_csv(path.parent / "output/fault_info.csv")  # contents = task_file.readlines()
    strat_info = pd.read_csv(path.parent / "output/strat.csv")
    # contents = (contents)
    # get first file part - everything up to where the data points are added
    end_line = contents[0] == '  Add3DInterfacesToFormation {'
    idx = [a for a, x in enumerate(end_line) if x]  # make list of row indices where the string above is found
    task_pt1 = contents[0:(idx[0] - 1)]
    voxet_path = path.parent / "voxets/"
    if not os.path.exists("./voxets"):
        os.makedirs("./voxets")

    for i in range(func_params.egen_project.egen_runs):
        add_new_data = [f'''GeomodellerTask {{\n\tReadAndImport3dData {{\n\t\tcontact_csv_file: "output/contacts_{i}.csv"\n\t\tfoliation_csv_file: "output/contacts_orient_{i}.csv"\n\t\toperation: Import_default\n\t}}\n}}''']

        full_task = task_pt1.append(add_new_data)
        ####
        # Calculate model lines

        #

        # assign default parameters
        if func_params.egen_project.series_list is None:
            # series_c = 'all'
            series_list = strat_info['series'].unique()
        else:
            series_list = func_params.egen_project.series_list

        if func_params.egen_project.series_list == 'all':
            series_list = strat_info['series'].unique()

        if func_params.egen_project.krig_range is None:
            krig_range = 10000.0
        if func_params.egen_project.interface is None:
            interface = 0.000001
        if func_params.egen_project.orientation is None:
            orientation = 0.01
        if func_params.egen_project.drift is None:
            drift = 1

        calc_model_str1 = [f'''GeomodellerTask {{\nComputeModel {{\nSeriesList {{''']
        # f.write(calc_model_str1)
        full_task = full_task.append(calc_model_str1)

        for sc in range(len(series_list)):
            calc_model_str_series_calc = [f'''node: "{series_list[sc]}"''']

            #    f.write(calc_model_str_series_calc)
            full_task = full_task.append(calc_model_str_series_calc)

        ''' Don't need to include the SectionList in the compute call. It's possible this also creates issues as there
        is no data on the Section to calculate. Previous testing produced a 'Failed Cholesky inversion' error, plus a 
        homogenous null model.'''
        calc_model_str_section_list = [f'''}}\nSectionList {{\nnode: "all" }}''']
        # f.write(calc_model_str_section_list)
        full_task = full_task.append(calc_model_str_section_list)

        if func_params.egen_project.fault_list is not None:
            calc_model_str_fault_calc1 = [f'''\nFaultList {{''']
            #    f.write(calc_model_str_fault_calc1)
            full_task = full_task.append(calc_model_str_fault_calc1)

            # print(calc_model_str_fault_calc1)
            for fc in range(len(fault_info)):
                calc_model_str_fault_calc2 = [f'''node: "{fault_info.iat[fc, 0]}"''']
                full_task = full_task.append(calc_model_str_fault_calc2)

            calc_model_str_fault_calc3 = ["}"]
            #   f.write(calc_model_str_fault_calc3)
            full_task = full_task.append(calc_model_str_fault_calc3)

        # set calc_uncertainty flag to false. When = true the calculation is much slower. We can't get the error estimate out at this point anyway.
        # can make this an if statement and add a parameter to the class
        calc_uncert = [f'''\ncalc_uncertainty: false''']
        full_task = full_task.append(calc_uncert)

        for ss in range(len(series_list)):
            calc_model_str2 = [
                f'''\nSeriesInterpolationParameters {{\nseries: "{series_list[ss]}"\nRange: {krig_range}\nContacts_Nugget_Effect: {interface}\nGradients_Nugget_Effect: {orientation}\nFaultDriftEquationDegree: {drift} }}''']
            #   f.write(calc_model_str2)
            full_task = full_task.append(calc_model_str2)

        calc_model_str3 = [f'''\n}}\n}}\n''']
        # f.write(calc_model_str3)
        full_task = full_task.append(calc_model_str3)

        calc_model_str_uncert = [f'''calc_uncertainty: false''']

        ####
        calc_model_str4 = [
            f'GeomodellerTask {{\n    SaveProjectAs {{\n        filename: "{path.parent}/model_{i}.xml"\n    }}\n}}\n']
        full_task = full_task.append(calc_model_str4)

        if func_params.egen_project.litho is True:
            # save out lithology voxet
            vox_task1 = [
                f'''GeomodellerTask {{\nSaveLithologyVoxet {{\nnx: {func_params.egen_project.nx}\nny: {func_params.egen_project.ny}\nnz: {func_params.egen_project.nz}\nLithologyVoxetFileStub: "{voxet_path}/model_{i}_gocad_litho"\n}}\n}}\n''']
        else:
            vox_task1 = [""]
        if func_params.egen_project.scalar is True:
            vox_task2 = [
                f'''GeomodellerTask {{\nSavePotentialGradientVoxet {{\nnx: {func_params.egen_project.nx}\nny: {func_params.egen_project.ny}\nnz: {func_params.egen_project.nz}\nJust_Gradients: false\nVoxetFileStub: "{voxet_path}/model_{i}_gocad_scalar"\n}}\n}}\n''']
            # vox_task2 = ['''GeomodellerTask {
            # SavePotentialGradientVoxet {
            #     nx: %d
            #     ny: %d
            #     nz: %d
            #
            #     VoxetFileStub: "%s/model_%i_gocad_scalar"
            #     }
            # }\n'''] % (nx, ny, nz, voxet_path, i)
        else:
            vox_task2 = [""]
        if func_params.egen_project.scalar_grads is True:
            vox_task3 = [
                f'''GeomodellerTask {{\nSavePotentialGradientVoxet {{\nnx: {func_params.egen_project.nx}\nny: {func_params.egen_project.ny}\nnz: {func_params.egen_project.nz}\nJust_Gradients: true\nVoxetFileStub: "{voxet_path}/model_{i}_gocad_scalar_grads"\n}}\n}}\n''']
            # vox_task3 = ['''GeomodellerTask {
            # SavePotentialGradientVoxet {
            #     nx: %d
            #     ny: %d
            #     nz: %d
            #     Just_Gradients: true
            #     VoxetFileStub: "%s/model_%i_gocad_scalar_grads"
            #     }
            # }\n'''] % (nx, ny, nz, voxet_path, i)
        else:
            vox_task3 = [""]

        full_task = full_task.append(vox_task1)
        full_task = full_task.append(vox_task2)
        full_task = full_task.append(vox_task3)

        close_task = ['''GeomodellerTask {\nCloseProjectNoGUI {\n}\n}''']

        full_task = full_task.append(close_task)

        np.savetxt(f'''{path.parent}/{path.stem}_{i}{path.suffix}''', np.array(full_task), fmt='%s')
        # full_task.to_csv(f'{path.parent / path.stem}_{i}{path.suffix}', index=None, header=None, quoting=csv.QUOTE_NONE, quotechar="",  escapechar="\\")
        print(f'Run {i}')
