#%% Parameters for ensemble generation
#############################
#  Names, labels, source    #
#############################

model_label = ''
source_M2L = #  True or False
source_geomodeller = #  True or False
#############################
#           Paths           #
#############################

path_to_geomodeller = ''

path_to_model = ''

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

# perturbation off/on

perturb_model = # True/False no perturbation of

# interface
error_gps =
distribution =
DEM =  # True or defaults to none
# orientations
kappa =
error_gps =
loc_distribution =

#############################
#       Compute params      #
#############################

series_list = 'all' # list of series to calculate
fault_list = None
krig_range =  None # kriging range
interface =  None # nugget effect on interface; larger values = smoother model (less adherence to the data) default = 0.000001.  Set to None for default value
orientation =  None # nugget effect on orientation data; larger values = smoother model (less adherence to the data) default = 0.01.  Set to None for default value
drift = None # Drift degree - 0 (no drift or trend), 1 (linear, tends towards planar), 2 (quadratic, tends to parabolic). Default = 1.  Set to None for default value
#############################
#       Summary stats       #
#############################

card = # True or False
ent = # True or False
propor = # True or False
export =# True or False
air = # True or False