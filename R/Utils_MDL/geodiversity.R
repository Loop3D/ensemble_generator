# testing - delete above line when working
#setwd("C:/Users/Mark/Documents/Projects/Geomodeller/MapToModel/MPM_Test_1/CURE_19-10-14-17-04-46")
# ____________________

geodiversity <- function (r_grid) {
  require(psych)
  #volumes of various lithologies - simple count
  cell_vol_km = abs(r_grid[["header"]][8,2]*r_grid[["header"]][8,3]*r_grid[["header"]][8,4])
  if (r_grid$header_units$V2[1] == "m") {
    cell_vol_km <- cell_vol_km/1000**3 # convert from m**3 to km**3
  }
  else
  models <- names(r_grid$data)
  delete_these <- c("x", "y", "z")
  models <- models [! models %in% delete_these]
  n_models <- length(models)
  n_lithos <- max(unique(r_grid$data[,n_models+3]))
  temp <- data.frame(matrix(NA, nrow = n_models, ncol = n_lithos))
  #count_temp <- matrix(NA, n_models, n_lithos)
  for (i in 1:n_models) {
    mod <- i+3
    counts <- sapply(1:n_lithos, function(x) length(which(r_grid$data[,mod]==x)))
    temp[i,] <- counts
    #temp_region <- r_grid$data$MPM_Test_1_0_GOCAD_LITHO.vop1==1
    #temp_region <- r_grid$data$MPM_Test_1_0_GOCAD_LITHO.vop1[temp_region]
  }
  stats <- describe(temp)
  #GD_stats <- matrix(NA, n_models, 3) # three columns for three extra stats
  t1 <- sapply(1:n_lithos, function(x) which.min(temp[,x]))
  t2 <- sapply(1:n_lithos, function(x) which.max(temp[,x]))
  t3 <- sapply(1:n_lithos, function(x) which(temp[,x]==stats[x, "median"]))
  length_check <- sapply(t3, function(x) length(t3[x]))
  ind <- which(length_check == n_models)
  t3[ind] <- "NA"
  GD_stats <- list(stats=stats, min_models = t1, max_models = t2, median_models = t3, counts = temp)
  return(GD_stats)
}

