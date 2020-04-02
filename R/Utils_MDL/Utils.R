## various functions for r written for uncertainty analysis of 3D models
# Mark Lindsay and the Loop/MinEx CRC research group based at the CET, with contributions from Monash Uni. 

# Jensen-Shannon divergence
# Ref: https://en.wikipedia.org/wiki/Jensen%E2%80%93Shannon_divergence
#  Endres, D. M.; J. E. Schindelin (2003). "A new metric for probability distributions" (PDF). IEEE Trans. Inf. Theory. 49 (7): 1858–1860. doi:10.1109/TIT.2003.813506.

# "Rcpp Gallery" https://www.r-bloggers.com/parallel-distance-matrix-calculation-with-rcppparallel/

js_distance <- function(mat) {
  kld = function(p,q) sum(ifelse(p == 0 | q == 0, 0, log(p/q)*p))
  res = matrix(0, nrow(mat), nrow(mat))
  for (i in 1:(nrow(mat) - 1)) {
    for (j in (i+1):nrow(mat)) {
      m = (mat[i,] + mat[j,])/2
      d1 = kld(mat[i,], m)
      d2 = kld(mat[j,], m)
      res[j,i] = sqrt(.5*(d1 + d2))
    }
  }
  res
}

# convert [x,y,z,property] format to pp3 (3D point pattern) in spatstat
# requires spatstat to be loaded
vox_to_pp3 <- function(voxet, property) {
  # assumes you want a property as a mark, which you do if using a property voxet (the point locations are predetermined, and not the subject of analysis)
  # also assumes the roi is the extents of the voxet, though additional args can be added to allow this to be changed.
  vox_box <- box3(xrange = c(min(voxet$x), max(voxet$x)), yrange = c(min(voxet$y), max(voxet$y)), zrange = c(min(voxet$z), max(voxet$z)), unitname = c("metre", "metres"))
  #prop <- paste(voxet, "$", property, sep ="")
  temp <- pp3(voxet$x, voxet$y, voxet$z, vox_box, marks = property)
  return(temp)
  # example: card_test <- vox_to_pp3(voxet_card_orig, voxet_card_orig$Card_VOXET.vop1)
}

## Gocad voxet reader
read_voxet <- function(directory, type) { # i want to specify the voxet name too, but first let's test just using the directory name
  #type = c("Card_VOXET", "Entropy_VOXET", "Frequency_VOXET", "OLS_VOXET", "P1_VOXET", "GOCAD_LITHO")
  # this function imports voxets that are output by Geomodeller and related CURE (Common Uncertainty Research Explorer).
  # while these voxets are technically "Gocad" format, true Gocad format has @@ prefixes to properties
  # So this reader won't work with true gocad formats (yet).
  current_dir <- getwd()
  on.exit(setwd(current_dir))
  setwd(directory)
  
  pattern = type
  # 
  
  #   
  if (type == "GOCAD_LITHO") {
    pattern_a = "\\w+"
  } else {
    pattern_a = NULL
  }
  
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

## summary stats for frequency ensemble voxets
# plans for the future - add 'type' arg to summarise litho/uncertainty voxets, 
summary_stats <- function(voxet, type) {
  require(psych)
  #if (type==Frequency){ add type specific operations here. 
  formations <- seq(1:(length(voxet$data)-3))
  formations <- sapply(formations, function(y) paste("Formation_", y, sep = ""))
  summ_stats <- sapply(4:length(voxet$data), function(x) describe(voxet$data[,x]))
  summ_stats <- data.frame(t(summ_stats)) # note the data type of the data is 'unknown' so...
  summ_stats[, 1:ncol(summ_stats)] <- sapply(summ_stats[, 1:ncol(summ_stats)], as.numeric) # convert all cols to numeric so we can have fun with numbers
  summ_stats$formation <- formations
  #add custom stats here 
  summ_stats$NumOnes <- sapply(4:length(voxet$data), function(x) sum((voxet$data[,x]==1), na.rm = TRUE)) # number of 1's (i.e. certain it's that formation)
  summ_stats$NumZeros <- sapply(4:length(voxet$data), function(x) sum((voxet$data[,x]==0), na.rm = TRUE)) # number of 0's (i.e. certain it's NOT that formation)
  summ_stats$NotOneOrZero <- summ_stats$n-(summ_stats$NumOnes+summ_stats$NumZeros) # number of cells not 1 or zero (uncertain cells)
  # custom stats bit ends here
  return(summ_stats)
}

