class egen_project:
    #############################
    #      Names and labels     #
    #############################

    model_label = 'YerridaBasin'
    source_geomodeller = True  # True or False
    model_task = 'YerridaBasin_masked_10Oct2017.task'
    model_xml = 'YerridaBasin_masked_10Oct2017.xml'
    #############################
    #           Paths           #
    #############################

    path_to_geomodeller = 'C:/GeoModeller/GeoModeller4.0.8_x64_d9d8f5c58a1'  # version July2020
    # path_to_geomodeller = pathlib.Path('C:\GeoModeller\GeoModeller4.0.8_x64_88b64e610d9')

    path_to_model = 'C:/Users/Mark/Cloudstor/EGen/YerridaBasin_masked_10Oct2017'
    # path_to_model_pl = pathlib.Path('C:/Users/Mark/Cloudstor/EGen/test_data3')

    #############################
    #           Files           #
    #############################

    DTM_name = 'Yerrida_SRTM_90m.ers'  # , just the filename, not the path, includes file extension

    #############################
    #       Ensemble par        #
    #############################

    egen_runs = 10
    save_faults = True  # True/False: do we want faults included?

    #############################
    #       Voxet parameters    #
    #############################

    litho = True  # True or comment out
    scalar = False  # True or comment out
    scalar_grads = False  # True or comment out

    # Voxet parameters
    nx = 113
    ny = 100
    nz = 40

    #############################
    #      Perturbing params    #
    #############################

    # interface
    error_gps = 10
    distribution = 'uniform'
    DEM = False  # True or none
    # orientations
    kappa = 150
    error_gps = 10
    loc_distribution = 'uniform'

    #############################
    #       Compute params      #
    #############################

    series_list = (['ArcheanGranite', "ArcheanGreenstone_Series", "PostArcheanUncon_Series", "Juderina", "Mafic_Intrusions_inWindplain_Series", "Windplain_Uncon", "JohnsonCairn", "MaficIntrusions_inJohnsonCairn_Series", "PostWindplainUncon_Series", "LowerMooloogoolSubGroup", "MaficIntrusive_MooloogoolIntrusive_Series", "Mooloogool_Uncon_Series", "UpperMooloogool_SubSeries", "ToolooSubGroup", "Masking_intrusion"]) # list of series to calculate
    fault_list = 'all'  # (['Fault_12644', 'Fault_2235', 'Fault_11442', 'Fault_3496', 'Fault_5298', 'Fault_12647']) # list of faults to calculate or 'all'
    krig_range = None  # kriging range - set to None for default values
    interface = None  # nugget effect on interface; larger values = smoother model (less adherence to the data) default = 0.000001. Set to None for default value
    orientation = None  # nugget effect on orientation data; larger values = smoother model (less adherence to the data) default = 0.01. Set to None for default value
    drift = None  #

    #############################
    #       Summary stats       #
    #############################

    card = True  # True or False - export a voxet representing model cardinality
    ent = True  # True or False - export a voxet representing model entropy
    propor = True  # True or False - export a voxet representing the proportions of modelled lithologies
    export = True  # Export voxet - Can be 'False' if the arrays produced by the summary stats function are being passed directly to a downstream process
    air = True  # is there an 'air' layer in the model? Will be yes if there is a DTM and/or the surface topo is not at the top of the model volume. Important for geodiversity and proportion calculations.
