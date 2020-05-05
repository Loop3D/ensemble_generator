import numpy as np

def egen_paths(geomodeller, model, data=None):
    """define paths for different parts of the process"""
    # arg path inputs need to be raw string to avoid escape issue eg. "\U" in C:\Users etc
    global path_geomodeller1
    global path_geomodeller2
    global path_model
    global path_output
    global path_data
    path_geomodeller1 = f'{geomodeller}/bin'
    path_geomodeller1 = path_geomodeller1.replace("\\", "/")
    path_geomodeller2 = f'{geomodeller}/bin/server'
    path_geomodeller2 = path_geomodeller2.replace("\\", "/")
    path_model = model
    # path_model = "%r" % model
    path_model = path_model.replace("\\", "/")
    path_output = f'{model}/output'  # task files will be stored in output directory. ?Separate one - unnecessary at this point
    path_output = path_output.replace("\\", "/")
    if data is not None:
        path_data = data.replace("\\", "/")
    else:
        data = None
    return #path_geomodeller1, path_geomodeller2, path_model


def egen_xml_to_task(model_name):
    """generate task file from xml"""
    # emulates exporter.task
    # path_model; path_outputs should be prior set with egen paths
    # paths areas input, so can be explicit or relative.
    import os
    global g_model_name  # name of model without .xml for naming use in exports etc.
    if model_name.find(".xml") == -1:
        model_name + str(".xml")
    if model_name.find(".xml") != -1:
        g_model_name = model_name
    else:
        g_model_name = model_name.replace(".xml", "")
    if not os.path.exists(path_output):
        os.makedirs(path_output)
    orig_task = open(f'{path_output}/xml_to_task.task', "w")
    task = '''GeomodellerTask {
        WriteBatchFile {
            filename: "%s/%s"
                Task_Name: "%s/project_export.task"
                convertSection_InterfacesTo3D: true
                convertSection_FoliationTo3D: true
                exportBoreholesToCSV: false
                csv_path: "%s/"
                exportToGeomodellerTempDirectory: false
            }
        }''' % (path_model, model_name, path_output, path_output)
    orig_task.write(task)
    orig_task.close()
    return


def egen_calc_original(model_name):
    '''calculate original model'''
    orig_task = open(f'{path_output}/{model_name}', "w")
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
    egen_batch = open(f'{path_output}/egen_batch.bat', "w")
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

# def egen_MC_cokrig_params(range = None, interface = None, orientation = None, drift = None):
#     '''set model interpolation parameters using cokriging'''
#     '''Range default = 10000.0]; Contacts_Nugget_Effect [default = 0.000001];
#      Gradients_Nugget_Effect [default = 0.01]; FaultDriftEquationDegree = 4 [default = 1]'''
#     if range is None:
#         range = 10000.0
#     if interface is None:
#         interface = 0.000001
#     if orientation is None:
#         orientation = 0.01
#     if drift is None:
#         drift = 1
#     task = '''GeomodellerTask {
#     OpenProjectNoGUI {
#         filename: "%s/%s"
#     }
#     }\n
#     GeomodellerTask {
#         ComputeModel {
#             SeriesList
#                 {
#         node: "all"
#                 }
#         SectionList {
#         node: "all"
#                 }
#         ModelInterpolationParameters {
#             Range: %f
#             Contacts_Nugget_Effect: %f
#             Gradients_Nugget_Effect: %f
#             FaultDriftEquationDegree: %i
#             }
#     }\n
#     GeomodellerTask {
#     CloseProjectNoGUI {
#     }
#     }''' % (path_model, g_model_name, range, interface, orientation, drift)
#
#     egen_interpolate = open(f'{path_output}/egen_MC_cokrig_params.task', "w")
#     egen_interpolate.write(task)
#     egen_interpolate.close()
#     return

# need to create function that parses the project_export.task so info can be extracted ie. fault and series names etc
# then these can be used to automate the different kriging parameters in a MC type of fashion and the other things.

def sample_vMF(mu, kappa, num_samples):
    """Generate num_samples N-dimensional samples from von Mises Fisher
    distribution around center mu \in R^N with concentration kappa.
    Source: https://github.com/jasonlaska/spherecluster/
    """
    dim = len(mu)
    result = np.zeros((num_samples, dim))
    for nn in range(num_samples):
        # sample offset from center (on sphere) with spread kappa
        w = _sample_weight(kappa, dim)

        # sample a point v on the unit sphere that's orthogonal to mu
        v = _sample_orthonormal_to(mu)

        # compute new point
        result[nn, :] = v * np.sqrt(1. - w ** 2) + w * mu

    return result