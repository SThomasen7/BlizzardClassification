## final project R
## Scott Andersen
#install.packages("scatterplot3d") # Install
#library("scatterplot3d") # load
#library(plotly)
data = read.csv("data/aggregated_fix.csv", header=TRUE, sep=",", row.names=NULL,
                check.names = FALSE, stringsAsFactors = FALSE)

wind_speed = data$wind_speed
temp = data$temp
vis = data$visibility_distance
has_blizzard = data$has_blizzard
snow_accumulation = data$snow_accumulation

# blizzard data
blizzard.wind = wind_speed[has_blizzard == 1 & temp < 100]
blizzard.accm = snow_accumulation[has_blizzard == 1 & temp < 100]
blizzard.visb = vis[has_blizzard == 1 & temp < 100]
blizzard.temp = temp[has_blizzard == 1 & temp < 100]

# snow data
snow.wind = wind_speed[has_blizzard == 0 & temp < 100]
snow.accm = snow_accumulation[has_blizzard == 0 & temp < 100]
snow.visb = vis[has_blizzard == 0 & temp < 100]
snow.temp = temp[has_blizzard == 0 & temp < 100]

pdf("figs/distributions.pdf")
par(mfrow=c(4,2))
hist(blizzard.wind, main="Blizzard Winds", xlab="Wind speed (m/s)")
hist(snow.wind, main="Snow Winds", xlab="Wind speed (m/s)")
hist(blizzard.accm, main="Blizzard Accumulation", xlab="Snow accumulation (in)")
hist(snow.accm, main="Snow Accumulation", xlab="Snow accumulation (in)")
hist(blizzard.visb, main="Blizzard Visibility", xlab="Visibility distance (m)")
hist(snow.visb, main="Snow Visibility", xlab="Visibility distance (m)")
hist(blizzard.temp, main="Blizzard Temps", xlab="Temperature (°C)")
hist(snow.temp, main="Snow Temps", xlab="Temperature (°C)")
dev.off()

## bootstrap samples to determine the 

## Function for bootstrap comparison
## bootstrap calculate difference in means
#test_bootstrap = function(dataA, dataB, Alabel, Blabel, title, N=100000, S=1000000){
#  # Define arrays for store results
#  mean_array_1=rep(NA, length.out=N)
#  mean_array_2=rep(NA, length.out=N)
#  mean_array_diff=rep(NA, length.out=N)
  
  # Use a for loop to calculate bootstrap statistics
#  for(i in 1:N) {
#    sample_1_boot=sample(dataA,size=length(S),replace=TRUE)
#    sample_2_boot=sample(dataB,size=length(S),replace=TRUE)
    
#    mean_array_1[i]=mean(sample_1_boot)
#    mean_array_2[i]=mean(sample_2_boot)
#    mean_array_diff[i]=mean(sample_1_boot)-mean(sample_2_boot)
#  }
  
#  plot(density(mean_array_1),
#       col="blue",lwd=2,
#       main=title,      
#       ylab="density",
#       xlab="sample mean")
#  abline(v=mean(mean_array_1),col="blue",lwd=2)
  
#  lines(density(mean_array_2),col="red",lwd=2)
#  abline(v=mean(mean_array_2),col="red",lwd=2)
  
  #Create Legend
#  legend(x="topright",
#         legend=c(Alabel, Blabel),
#         col=c("blue","red"),
#         lty=c("solid","solid"),
#         lwd=c(5,5)
#  )
  
#  plot(density(mean_array_diff),
#       col="black",lwd=2,
#       main="Distribution of Difference in Means",
#       ylab="density",
#       xlab="sample mean difference")
#  abline(v=mean(mean_array_diff),col="black",lwd=3)
  
#  quantiles = quantile(mean_array_diff, probs=c(0.025, 0.975))
#  abline(v=quantiles[1],col="black",lty="dashed",lwd=2)
#  abline(v=quantiles[2],col="black",lty="dashed",lwd=2)
#  print(quantiles[1]-quantiles[2])

#}

#pdf("figs/means.pdf")
#par(mfrow=c(4,2))
#test_bootstrap(blizzard.wind, snow.wind, "Blizzard Winds", "Snow Winds",
#               "Wind means")

#test_bootstrap(blizzard.temp, snow.temp, "Blizzard Temps", "Snow Temps",
#               "Temp means")

#test_bootstrap(blizzard.accm, snow.accm, "Blizzard accum", "Snow accum",
#               "24 Hour Snow accumulation means")

#test_bootstrap(blizzard.visb, snow.visb, "Blizzard visb", "Snow visib",
#               "Visibility means")
#dev.off()

## let's take a look at the data as points in 2D and 3D to determine
## if it is appropriate to threshold blizzards

## first let's just look at wind and daily snow accumulation
#plot(snow.wind, snow.temp, col="black", pch=16, cex=0.5)
#points(blizzard.wind, blizzard.temp, col="lightblue", pch=16, cex=0.5)

#plot(snow.wind, snow.accm, col="black", pch=16, cex=0.5)
#points(blizzard.wind, blizzard.accm, col="lightblue", pch=16, cex=0.5)

#wind_speed = data$wind_speed[data$temp < 100]
#temp = data$temp[data$temp < 100]
#vis = data$visibility_distance[data$temp < 100]
#has_blizzard = data$has_blizzard[data$temp < 100]
#snow_accumulation = data$snow_accumulation[data$temp < 100]
#colors <- c("gray", "lightblue")
#colors <- colors[has_blizzard]
#colors <- ifelse(has_blizzard == 1, "lightblue", "gray")
#scatterplot3d(wind_speed, temp, vis, pch=16, color=colors)

#fig <- plot_ly(x = wind_speed,
#        y = temp,
#        z = vis,
#        type = "scatter3d",
#        mode = "markers",
#        marker = list(color=colors))