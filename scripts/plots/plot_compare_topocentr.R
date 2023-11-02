library(rgl)
library(htmlwidgets)

path_to_kepler_module_substr = "\\\\wsl.localhost\\Ubuntu-22.04\\home\\max\\git2\\ma-max-wendler\\examples\\space_veins\\csv\\vectors\\Debug-iridium-NEXT-kepler_SatelliteExampleScenario.leoIRIDIUM[100].vehicleStatistics_"
path_to_sgp4_module_substr = "\\\\wsl.localhost\\Ubuntu-22.04\\home\\max\\git2\\ma-max-wendler\\examples\\space_veins\\csv\\vectors\\Debug-iridium-NEXT-sgp4_SatelliteExampleScenario.leoIRIDIUM[100].vehicleStatistics_"

x_kepler <- data.frame(read.csv(paste0(path_to_kepler_module_substr, "omnetCoordX:vector.csv"), sep="\t"))
y_kepler <- data.frame(read.csv(paste0(path_to_kepler_module_substr, "omnetCoordY:vector.csv"), sep="\t"))
z_kepler <- data.frame(read.csv(paste0(path_to_kepler_module_substr, "omnetCoordZ:vector.csv"), sep="\t"))

x_sgp4 <- data.frame(read.csv(paste0(path_to_sgp4_module_substr, "omnetCoordX:vector.csv"), sep="\t"))
y_sgp4 <- data.frame(read.csv(paste0(path_to_sgp4_module_substr, "omnetCoordY:vector.csv"), sep="\t"))
z_sgp4 <- data.frame(read.csv(paste0(path_to_sgp4_module_substr, "omnetCoordZ:vector.csv"), sep="\t"))

print(x_kepler)
print(x_sgp4)

print(y_kepler)
print(y_sgp4)

print(z_kepler)
print(z_sgp4)

# Calculate the difference in x, y, and z coordinates
diff_x <- x_kepler$omnetCoordX_vector - x_sgp4$omnetCoordX_vector
diff_y <- y_kepler$omnetCoordY_vector - y_sgp4$omnetCoordY_vector
diff_z <- z_kepler$omnetCoordZ_vector - z_sgp4$omnetCoordZ_vector

# Calculate the Euclidean distance at each point in time
distance <- sqrt(diff_x^2 + diff_y^2 + diff_z^2)

print(distance)