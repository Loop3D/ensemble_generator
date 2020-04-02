#make sure the working directory is where the files are

library(readr)
library(dplyr)
setwd("C:/Users/Mark/Dropbox/Vuonos/Conversion/interfaces") # make sure we're looking in the right spot
#filenames <- data.frame(dir(".", pattern = "'\'.ts[^'\'.csv]", no.. = TRUE))
filenames <- data.frame(dir(".", pattern = ".*\\.ts$", no.. = TRUE))
colnames(filenames) <- ("files")

# set a minimum threshold for points number
minthresh = 20
buffer = 5 # to avoid any unnecessary downscaling, this means if the file has less than 25 (20 + 5) points prior to downsampling, don't downsample

# downscaling function
Nth.delete<-function(dataframe, n)dataframe[-(seq(n,to=nrow(dataframe),by=n)),]
# n = downscaling coeffient, removes every nth line. 1.25 = 20% of lines retained; 1.5 = 33% retained, 2 = 50%, 3 = 66%, 4 = 25% and so on.
downsampling_report <- matrix(NA, nrow = nrow(filenames), ncol = 4) #file name; orig; downsample; percent reduced

for (i in 1:nrow(filenames)) {
  filename <- as.character(filenames[i,])
  downsampling_report[i,1] <- filename
  outputfilename <- paste(filename, '.csv', sep='')
  tempfile <- read_table2(filename, col_names = FALSE, skip = 56)
  indx <- min(which(tempfile == "TRGL")) # find where TRGL rows start (we don't want these)
  tempfile <- tempfile[-c(indx:nrow(tempfile)), ] # delete everything from where TRGL starts to the end of file
  tempfile <- select(tempfile, -c(X1, X2, X6)) # remove unnecessary columns
  colnames(tempfile) <- c("x", "y", "z") # rename columns to x, y, z
  downsampling_report[i,2] <- nrow(tempfile)
  # downscaling via proportion ('n') only if the number of points is > than the minthres, plus a buffer
  if(nrow(tempfile)>minthresh+buffer) { # check for number of points (line 27)
    n <- ((minthresh/nrow(tempfile))+1) # calc necessary coefficient
    tempfile <- Nth.delete(tempfile, n) # downsample
  }  
  downsampling_report[i,3] <- nrow(tempfile)
  downsampling_report[i,4] <- (1-(as.numeric(downsampling_report[i,3])/as.numeric(downsampling_report[i,2])))*100
  colnames(downsampling_report) <- c("filename", "orig_no.", "downsampled_no.", "percent_reduced")
  write.csv(tempfile, file = outputfilename, row.names = F) # export as csv
  
}
write.csv(downsampling_report, file = "downsampling_report.csv", row.names = F)


## this one is for orientation points (not interface)
## AT THIS POINT IN TIME, I DON'T KNOW AN EASY WAY TO EXPORT SURFACES WITH THEIR NORMALS. We need the normals to get the orientations. You can export normals with the 'Export to Excel' option, but dealing with the formatting is a pain. On the To do list.
## we need to downsample these points intelligently - that is, no just a decimation, but keep some more of the points that are closer to the surface.
## format is Geological formation or fault, X, Y, Z, Direction, Dip, Polarity

#setwd("C:/Users/Mark/Dropbox/Vuonos/Conversion/orientations") # make sure we're looking in the right spot
for (j in 1:nrow(filenames)) {
  filenames <- data.frame(dir(".", no.. = TRUE))
  colnames(filenames) <- ("files")
  filename <- as.character(filenames[j,])
  outputfilename <- paste(filename, '.csv', sep='')
  tempfile <- read_table2(filename, col_names = FALSE, skip = 56)
  indx <- min(which(tempfile == "TRGL")) # find where TRGL rows start (we don't want these)
  tempfile <- tempfile[-c(indx:nrow(tempfile)), ] # delete everything from where TRGL starts to the end of file
  tempfile <- select(tempfile, -c(X1, X2, X6)) # remove unnecessary columns
  colnames(tempfile) <- c("x", "y", "z") # rename columns to x, y, z
  write.csv(tempfile, file = outputfilename, row.names = F)
}
