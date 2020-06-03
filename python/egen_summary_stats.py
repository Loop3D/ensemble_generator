#%% import modules
import numpy as np
import pandas as pd
#from math import log, e
import sys, os, glob
from stats_utils import entropy_custom
from stats_utils import litho_probabilites


#%%

def stats_gocad_voxet(directory, type, model_label='Anon', card=False, ent=False, propor=False, export=True, air=False):
    # i want to specify the voxet name too, but first let's test just using the directory name
    #type = c("Card_VOXET", "Entropy_VOXET", "Frequency_VOXET", "OLS_VOXET", "P1_VOXET", "GOCAD_LITHO")
    # this function imports voxets that are output by Geomodeller and related CURE (Common Uncertainty Research Explorer).
    # while these voxets are technically "Gocad" format, true Gocad format has @@ prefixes to properties
    # So this reader won't work with true gocad formats (yet).
    #print(str(os.getcwd()))
    os.chdir(directory)

    pattern = type
    if type == "GOCAD_LITHO":
        pattern_a = "*"
    elif type == "gocad_litho":
        pattern_a = "*"
    else:
        pattern_a = type
    # generate list of voxet header files to import
    h_pattern = pattern_a + pattern + "*.vo"
    header_file = glob.glob(h_pattern)

    if len(header_file) != 0:
        # this reads the first file listed from the dir() operation, but I don't like it much. I'd prefer to specify
        # the header explicitly, but I can't seem to get the regex within the pattern arg working properly
        # "Frequency_VOXET.vo\W" works in the regex util, but not in R... who knows.

        # gocad header voxets have varying number of columns down the file. This process
        # dynamically generates the number of columns so the head can be imported as a csv

        # The max column count a line in the file could have
        largest_column_count = 0

        with open(header_file[0], 'r') as temp_h:
            # read lines
            lines = temp_h.readlines()

            for l in lines:
                # Count the column count for the current line
                column_count = len(l.split(' ')) + 1

                # Set the new most column count
                largest_column_count = column_count if largest_column_count < column_count else largest_column_count

        #Close the file
        temp_h.close()

        # Generate column names (will be 0, 1, 2, ..., largest_column_count - 1)
        column_names = [i for i in range(0, largest_column_count)]

        # Read csv
        full_header = pd.read_csv(header_file[0], header=None, delimiter=" ", names=column_names)

        #full_header = pd.read_csv(header_file[0], header=None, sep=" ")
        header = pd.read_csv(header_file[0], header=None, sep=" ", skiprows=4, nrows=8)
        header_units = pd.read_csv(header_file[0], header=None, sep=" ", skiprows=13, nrows=1)
    else:
        print("Unknown voxet type: please enter voxet filename without the file extension")
        sys.exit()

    # create file names for export
    card_file_name = model_label + '_card'
    ent_file_name = model_label + '_entropy'
    # proportion file names set in the export loop below


    #create headers for different exports
    card_header = full_header.copy(deep=True) # interesting - need to do a deep copy. Normal copy will produce a new dataframe linked to the orginal. Changes to the original will be reflected in the copies.
    ent_header = full_header.copy(deep=True) # interesting - need to do a deep copy. Normal copy will produce a new dataframe linked to the orginal. Changes to the original will be reflected in the copies.
    propor_header = full_header.copy(deep=True)

    # format header info - cardinality
    card_header.loc[2, 1] = card_file_name
    card_header.loc[15, 2] = "'Cardinality'"
    card_header.loc[16, 2] = "'Cardinality'"
    card_header.loc[17, 2] = "'Cardinality'"
    card_header.loc[18, 2] = "'Cardinality'"
    card_header.loc[24, 2] = card_file_name + '.vop1'

    # format header info - entropy
    ent_header.loc[2, 1] = ent_file_name
    ent_header.loc[15, 2] = "'Entropy'"
    ent_header.loc[16, 2] = "'Entropy'"
    ent_header.loc[17, 2] = "'Entropy'"
    ent_header.loc[18, 2] = "'Entropy'"
    ent_header.loc[24, 2] = ent_file_name + '.vop1'


    #list the voxet property binary files to import
    # generate list of voxet header files to import
    p_pattern = pattern_a + pattern + "*.vop1"
    prop_files = glob.glob(p_pattern)
    litho_df = pd.DataFrame(np.zeros([int(header.loc[6,1]*header.loc[6,2]*header.loc[6,3]), 1]))

    for f in range(len(prop_files)):
        data = np.fromfile(prop_files[f], '>f4') # import binary with format '>f4': '>' = big endian, 'f' float, '4' size
        litho_df[f] = pd.DataFrame(data) # assign data to df column

    litho_df.columns = [prop_files] # label columns with model name
    # issue - the original voxet export includes 'air' - lithoID = 0, the recalculated model voxets do not.
    # we want air to be included, esp for geophys. So we create an 'air' mask using df indices where 0.0
    if air is True:
        air_idx = litho_df[[f'orig_{type}.vop1']] == 0.0
        idx = air_idx
        for i in range(litho_df.shape[1]-1): # subtract 1 from iterator because we start with one row
            air_idx = np.concatenate([air_idx, idx], axis=1)
        litho_df[air_idx] = 0.0


    # calculate cardinality
    # simple operation - how many unique values in each row.
    if card is True:
        card_data = litho_df.nunique(1)
        if export is True:
            card_export = np.array(card_data, '>f4')
            card_export.tofile(card_file_name + '.vop1')
            card_header.to_csv(card_file_name + ".vo", sep=" ", na_rep="", header=False, index=False)

    #calculate entropy
    if ent is True:
        ent_data = litho_df.apply(entropy_custom, axis=1)
        if export is True:
            ent_export = np.array(ent_data, '>f4')
            ent_export.tofile(ent_file_name + '.vop1')
            ent_header.to_csv(ent_file_name + ".vo", sep=" ", na_rep="", header=False, index=False)

    #calculate frequency
    if propor is True:
        propor_data = litho_probabilites(litho_df)
        if export is True:
            propor_block_template = propor_header.copy(deep=True)[15:26]
            propor_header = propor_header.drop(propor_header.index[15:27])
            propor_header.loc[2, 1] = f'''{model_label}_proportions'''
            propor_header_file_name = f'''{model_label}_propor.vo'''
            #propor_file_name = propor_header.drop(propor_header.index[15:26])
            for v in range(1, propor_data.shape[0]):
                property_file_name = f'''{model_label}_propor_{v}.vop1'''
                propor_block_tmp = propor_block_template.copy(deep=True)
                propor_block_tmp.loc[15:18,1]=v
                propor_block_tmp.loc[20:25, 1] = v
                propor_block_tmp.loc[15, 2] = f'''Proportion_lith_{v}'''
                propor_block_tmp.loc[16, 2] = f'''Proportion_lith_{v}'''
                propor_block_tmp.loc[17, 2] = f'''Proportion_lith_{v}'''
                propor_block_tmp.loc[18, 2] = f'''Proportion_lith_{v}'''
                propor_block_tmp.loc[24, 2] = property_file_name
                propor_header = propor_header.append(propor_block_tmp)
                propor_export = np.array(propor_data.loc[v], '>f4')
                propor_export.tofile(property_file_name)
            propor_header.to_csv(propor_header_file_name, sep=" ", na_rep="", header=False, index=False)

    return litho_df, card_data, ent_data, propor_data



#%% export summary stats to voxet

# def export_gocad_voxet(dataframe, path, type):
#      '''exports a dataframe to gocad voxet binary
#      'dataframe' is the pandas dataframe to be exported as voxet
#      'path' is the export path
#      'type' is the type of voxet - this defines the export name: "cardinality", "entropy", "probability"'''
#      #write header
#
#      #write binary
#
#
#      coords = np.zeros([int(header.loc[6,1]*header.loc[6,2]*header.loc[6,3]), 3])
#      coords_ref =
#
# def writeCFloat(f, ndarray):
#     np.asarray(ndarray, dtype=np.float32).tofile(f)
# def writeCInt(f, ndarray):
#     np.asarray(ndarray, dtype=np.int32).tofile(f)
# def writeC80(f, string):
#     np.asarray(string, dtype='a80').tofile(f)
#
# if __name__ == "__main__":
#     f = open('test.out', mode='wb')
#     ndarray = np.zeros((10000,10000))
#
#     writeCInt(f, ndarray)
#     writeCFloat(f, ndarray)
#     writeC80(f, 'coordinates')

#%% visualisation (put in different py file)



#


#
#
#
#
#
#   #build voxet in x, y, z order
#   coords <- matrix(NA, nrow = header[7,2]*header[7,3]*header[7,4], ncol = 3)
#   coords_ref <- list(z = seq(header[5,4], header[6,4], header[8,4]), y = seq(header[5,3], header[6,3], header[8,3]), x = seq(header[5,2], header[6,2], header[8,2]))
#   l=0
#   for (i in 1:header[7,4]){ #then build z-axis
#     for (j in 1:header[7,3]){ #then build y-axis
#       for (k in 1:header[7,2]){ #build x-axis first
#         l <- l+1
#         coords[l,] <- c(coords_ref$x[k], coords_ref$y[j], coords_ref$z[i])
#       }
#     }
#   }
#   # combine all property vectors into a dataframe
#   r_grid <- data.frame(coords, data.frame(sapply(prop_files, function(x) get(x))))
#   # rename coords columns in spatstat expectation i.e. lower case "x", "y", "z"
#   names(r_grid)[names(r_grid)=="X1"] <- "x"
#   names(r_grid)[names(r_grid)=="X2"] <- "y"
#   names(r_grid)[names(r_grid)=="X3"] <- "z"
#
#   temp_list <- list(header = header, header_units = header_units, data = r_grid)
#   #eval(parse(paste("r_grid_", type, sep="")) <- r_grid) # return grid with type in name
#   return(temp_list)
# }
#
#
