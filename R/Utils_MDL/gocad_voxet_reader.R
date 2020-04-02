read_voxet <- function(directory, type = c("Card_VOXET", "Entropy_VOXET", "Frequency_VOXET", "OLS_VOXET", "P1_VOXET", "GOCAD_LITHO")) { # i want to specify the voxet name too, but first let's test just using the directory name
  # this function imports voxets that are output by Geomodeller and related CURE (Common Uncertainty Research Explorer).
  # while these voxets are technically "Gocad" format, true Gocad format has @@ prefixes to properties
  # So this reader won't work with true gocad formats (yet).
  current_dir <- getwd()
  on.exit(setwd(current_dir))
  setwd(directory)
  
  pattern = type
  # 
  # if (type == "Cardinality") {
  #   pattern = "Card_VOXET"
  # } else if (type == "Entropy") {
  #   pattern = "Entropy_VOXET"
  # } else if (type == "Frequency") {
  #   pattern = "Frequency_VOXET"
  # } else if (type == "OLS") {
  #   pattern = "OLS_VOXET"
  # } else if (type == "P1") {
  #   pattern = "P1_VOXET"
  # } else {
  #   stop("Unknown type")
  # }
  #   
  if (type == "GOCAD_LITHO") {
    pattern_a = "\\w+"
  } else {
    pattern_a = NULL
  }
  
  # search regex for Entropy (Entropy_)\\w+ (Frequency_)\w+ (Card_)\\w+ (OLS_)\\w+ (P1_)\\w+
  # need to add the above as defined options for an arg 'type' of voxet
  #header_file <- dir(".", pattern = "\\w+\\.vo")
  h_pattern <- paste(pattern_a, pattern, "\\.vo", sep="")
  header_file <- dir(".", pattern = h_pattern)
  if (length(header_file) != 0) {
    # this reads the first file listed from the dir() operation, but I don't like it much. I'd prefer to specify
    # the header explicitly, but I can't seem to get the regex within the pattern arg working properly
    # "Frequency_VOXET.vo\W" works in the regex util, but not in R... who knows.
    header <- read.table(header_file[1], header = FALSE, sep = " ", skip = 4, nrows = 8)
    header_units <- read.table(header_file[1], header = FALSE, sep = " ", skip = 13, nrows = 1)
  } else {
    stop("Unknown voxet type: please enter voxet filename without the file extention")
  }
  
  #list the files to import
  #prop_files <- dir(".", pattern = "\\w+\\.vop\\w+") # the regex expression here says search for '.vop' (the \.vop part) and any alphanumeric before (\w+) or after (\w+). Note \\ for break characters
  p_pattern <- paste(pattern_a, pattern, ".vop\\w+", sep = "")
  prop_files <- dir(".", pattern = p_pattern) # the regex expression here says search for '.vop' (the \.vop part) and any alphanumeric before (\w+) or after (\w+). Note \\ for break characters
  for (f in 1:length(prop_files)){
    # need to ensure that voxet 2 is voxet 2, and not prop voxet 10, as it is second in the list
    assign(prop_files[f], readBin(prop_files[f], numeric(), n=header[7,2]*header[7,3]*header[7,4], size = 4, endian="big"))
  }
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



