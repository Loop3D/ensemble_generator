#%% import modules
import numpy as np
import pandas as pd
#from math import log, e
import sys, os, glob
from stats_utils import entropy_custom
import


#%%

def read_gocad_voxet(directory, type):
    # i want to specify the voxet name too, but first let's test just using the directory name
    #type = c("Card_VOXET", "Entropy_VOXET", "Frequency_VOXET", "OLS_VOXET", "P1_VOXET", "GOCAD_LITHO")
    # this function imports voxets that are output by Geomodeller and related CURE (Common Uncertainty Research Explorer).
    # while these voxets are technically "Gocad" format, true Gocad format has @@ prefixes to properties
    # So this reader won't work with true gocad formats (yet).
    #current_dir = os.getcwd()
    #on.exit(setwd(current_dir))
    os.chdir(directory)

    pattern = type
    if type == "GOCAD_LITHO":
        pattern_a = "*"
    else:
        pattern_a = None
    # generate list of voxet header files to import
    h_pattern = pattern_a + pattern + "*.vo"
    header_file = glob.glob(h_pattern)
    if len(header_file) != 0:
        # this reads the first file listed from the dir() operation, but I don't like it much. I'd prefer to specify
        # the header explicitly, but I can't seem to get the regex within the pattern arg working properly
        # "Frequency_VOXET.vo\W" works in the regex util, but not in R... who knows.
        header = pd.read_csv(header_file[0], header = None, sep=" ", skiprows=4, nrows=8)
        header_units = pd.read_csv(header_file[0], header=None, sep=" ", skiprows=13, nrows=1)
    else:
        print("Unknown voxet type: please enter voxet filename without the file extention")
        sys.exit()


    #list the voxet property binary files to import
    # generate list of voxet header files to import
    p_pattern = pattern_a + pattern + "*.vop1"
    prop_files = glob.glob(p_pattern)
    litho_df = pd.DataFrame(np.zeros([int(header.loc[6,1]*header.loc[6,2]*header.loc[6,3]), 1]))

    for f in range(len(prop_files)):
        data = np.fromfile(prop_files[f], '>f4') # import binary with format '>f4': '>' = big endian, 'f' float, '4' size
        litho_df[f] = pd.DataFrame(data) # assign data to df column

    litho_df.columns = [prop_files] # label columns with model name

    # calculate cardinality
    # simple operation - how many unique values in each row.
    card =  litho_df.nunique(1)

    # calculate entropy
    #  scipy.stats.entropy(pk, qk=None, base=None, axis=0)
    test = litho_df[:1]

    ent = litho_df.apply(entropy_custom, axis = 1)
    # TODO this isn't working - check results. min entropy should be 0 if min card = 1

    # frequency / probability

    frequency_df = pd.DataFrame(np.zeros([int(header.loc[6,1]*header.loc[6,2]*header.loc[6,3]), int(litho_df.iloc[:, [0]].max())]))
    for p in range(int(litho_df.iloc[:, [0]].max())):
        # calculate the proportion of lithoID = p for each row
        frequency_df[p] = litho_df.apply(some function in here proportion of lithoID = p for each row, axis=1) # TODO fix this bit - use apply to determine

#%%

def export_gocad_voxet(dataframe, path, type):
    '''exports a dataframe to gocad voxet binary
    'dataframe' is the pandas dataframe to be exported as voxet
    'path' is the export path
    'type' is the type of voxet - this defines the export name: "cardinality", "entropy", "probability"'''
    coords = np.zeros([int(header.loc[6,1]*header.loc[6,2]*header.loc[6,3]), 3])
    coords_ref =







  #build voxet in x, y, z order 
  coords <- matrix(NA, nrow = header[7,2]*header[7,3]*header[7,4], ncol = 3)
  coords_ref <- list(z = seq(header[5,4], header[6,4], header[8,4]), y = seq(header[5,3], header[6,3], header[8,3]), x = seq(header[5,2], header[6,2], header[8,2]))
  l=0
  for (i in 1:header[7,4]){ #then build z-axis
    for (j in 1:header[7,3]){ #then build y-axis
      for (k in 1:header[7,2]){ #build x-axis first
        l <- l+1
        coords[l,] <- c(coords_ref$x[k], coords_ref$y[j], coords_ref$z[i])
      }
    }
  }
  # combine all property vectors into a dataframe
  r_grid <- data.frame(coords, data.frame(sapply(prop_files, function(x) get(x))))
  # rename coords columns in spatstat expectation i.e. lower case "x", "y", "z"
  names(r_grid)[names(r_grid)=="X1"] <- "x"
  names(r_grid)[names(r_grid)=="X2"] <- "y"
  names(r_grid)[names(r_grid)=="X3"] <- "z"
  
  temp_list <- list(header = header, header_units = header_units, data = r_grid)
  #eval(parse(paste("r_grid_", type, sep="")) <- r_grid) # return grid with type in name
  return(temp_list)
}


