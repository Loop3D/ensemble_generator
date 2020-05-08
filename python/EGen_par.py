#%% Parameters for ensemble generation

#############################
#           Paths           #
#############################

path_to_geomodeller =

path_to_model =

#############################
#           Files           #
#############################

DTM_name =  #, just the filename, not the path, includes file extension

#############################
#       Ensemble par        #
#############################

egen_runs =
save_faults =  # True/False: do we want faults included?

#############################
#       Voxet parameters    #
#############################

litho =  # True or comment out
scalar = # True or comment out
scalar_grads = # True or comment out

# Voxet parameters
nx =
ny =
nz =

#############################
#      Perturbing params    #
#############################

# interface
error_gps =
distribution =
DEM =
# orientations
kappa =
error_gps =
loc_distribution =

#############################
#       Compute params      #
#############################

series_c =
fault_list =
krig_range =  # kriging range
interface =  # nugget effect on interface; larger values = smoother model (less adherence to the data) default = 0.000001
orientation =  # nugget effect on orientation data; larger values = smoother model (less adherence to the data) default = 0.01