#%% Parameters for ensemble generation

#############################
#           Paths           #
#############################

path_to_geomodeller =

path_to_model =

#############################
#       Ensemble par        #
#############################

egen_runs = 1

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

# orientations
kappa =
error_gps =
loc_distribution =

#############################
#       Compute params      #
#############################

series_list =
fault_list =
krig_range =  # kriging range
interface =  # nugget effect on interface; larger values = smoother model (less adherence to the data) default = 0.000001
orientation =  # nugget effect on orientation data; larger values = smoother model (less adherence to the data) default = 0.01