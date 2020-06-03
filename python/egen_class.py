class egen_project:
    #############################
    #      Names and labels     #
    #############################

    model_label = 'Geomodel_demo'
    source_geomodeller = True  # True or False
    #############################
    #           Paths           #
    #############################

    path_to_geomodeller = 'C:/GeoModeller/GeoModeller4.0.7_x64_27eee3dc31ba'
    # path_to_geomodeller = pathlib.Path('C:\GeoModeller\GeoModeller4.0.8_x64_88b64e610d9')

    path_to_model = 'C:/Users/Mark/Cloudstor/EGen/Geomodel_demo'
    # path_to_model_pl = pathlib.Path('C:/Users/Mark/Cloudstor/EGen/test_data3')

    #############################
    #           Files           #
    #############################

    DTM_name = 'dtm_rp.tif'  # , just the filename, not the path, includes file extension

    #############################
    #       Ensemble par        #
    #############################

    egen_runs = 100
    save_faults = True  # True/False: do we want faults included?

    #############################
    #       Voxet parameters    #
    #############################

    litho = True  # True or comment out
    scalar = False  # True or comment out
    scalar_grads = False  # True or comment out

    # Voxet parameters
    nx = 50
    ny = 50
    nz = 50

    #############################
    #      Perturbing params    #
    #############################

    # interface
    error_gps = 10
    distribution = 'uniform'
    DEM = False  # True or none
    # orientations
    kappa = 50
    error_gps = 10
    loc_distribution = 'uniform'

    #############################
    #       Compute params      #
    #############################

    series_list = 'all'  # list of series to calculate
    fault_list = 'all'  # (['Fault_12644', 'Fault_2235', 'Fault_11442', 'Fault_3496', 'Fault_5298', 'Fault_12647']) # list of faults to calculate or 'all'
    krig_range = None  # kriging range - set to None for default values
    interface = None  # nugget effect on interface; larger values = smoother model (less adherence to the data) default = 0.000001. Set to None for default value
    orientation = None  # nugget effect on orientation data; larger values = smoother model (less adherence to the data) default = 0.01. Set to None for default value
    drift = None  #

    #############################
    #       Summary stats       #
    #############################

    card = True  # True or False
    ent = True  # True or False
    propor = True  # True or False
    export = True
    air = False
