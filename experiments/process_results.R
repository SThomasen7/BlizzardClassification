library("rjson")
json_file <- "results/aggregated_classify_results.json"
json_data <- fromJSON(paste(readLines(json_file), collapse=""))

plot_stat_intervals <- function(data, model_name){
  print("******************************")
  hist(data$precision, main=c("Precision estimates for ", model_name),
       xlab = "Precision", breaks=20, xlim=c(0, 1))
  qs=quantile(data$precision,probs=c(0.05,.95))
  abline(v=qs, col="red", lwd=2)
  best_estimate=quantile(data$precision,probs=c(0.5))
  abline(v=best_estimate, col="blue", lwd=2)
  
  print(c("Precision quantile and best estimate -- ", model_name))
  print(qs)
  print(best_estimate)
  
  hist(data$recall, main=c("Recall estimates for ", model_name),
       xlab = "Recall", breaks=20, xlim=c(0, 1))
  qs=quantile(data$recall,probs=c(0.05,.95))
  abline(v=qs, col="red", lwd=2)
  best_estimate=quantile(data$recall,probs=c(0.5))
  abline(v=best_estimate, col="blue", lwd=2)
  
  print(c("Recall quantile and best estimate -- ", model_name))
  print(qs)
  print(best_estimate)
  
}

## Get the histograms of precision and recall for each classification method.
pdf("figs/classify_results/svm_precision_recall.pdf")
par(mfrow = c(4, 2), cex = 0.66)
plot_stat_intervals(json_data[["svm_classify_2"]], "svm_classify_2")
plot_stat_intervals(json_data[["svm_classify_3"]], "svm_classify_3")
plot_stat_intervals(json_data[["svm_classify_4"]], "svm_classify_4")
plot_stat_intervals(json_data[["svm_classify_2alt"]], "svm_classify_2 alternative")
dev.off()

pdf("figs/classify_results/bayes_precision_recall.pdf")
par(mfrow = c(4, 2), cex = 0.66)
plot_stat_intervals(json_data[["naive_bayes_2"]], "snaive_bayes_2")
plot_stat_intervals(json_data[["naive_bayes_3"]], "naive_bayes_3")
plot_stat_intervals(json_data[["naive_bayes_4"]], "naive_bayes_4")
plot_stat_intervals(json_data[["naive_bayes_2alt"]], "naive_bayes_2 alternative")
dev.off()

pdf("figs/classify_results/basic_precision_recall.pdf")
par(mfrow = c(2, 2), cex = 0.66)
plot_stat_intervals(json_data[["definition_classify"]], "NWS Definition")
plot_stat_intervals(json_data[["threshold_classify_browne"]], "Browne Definition")
plot_stat_intervals(json_data[["zeroR_classify"]], "Zero R")
dev.off()


pdf("figs/classify_results/browne_thresholds.pdf")
par(mfrow = c(1, 1), cex = 0.66)
## plot the threshold for browne's classification method
hist(json_data$threshold_classify_browne$threshold, 
    main="Snow accumulation thresholds for Browne",
    xlab = "Threshold", breaks=20, xlim=c(0, 1))
qs=quantile(json_data$threshold_classify_browne$threshold,
            probs=c(0.05,.95))
abline(v=qs, col="red", lwd=2)
best_estimate=quantile(json_data$threshold_classify_browne$threshold,
                       probs=c(0.5))
abline(v=best_estimate, col="blue", lwd=2)
dev.off()

################################################################
## take a look at the distribution of coefficients for SVM4, this gives us
## an idea of the importance of each variable in classifying blizzards.
## First we'll plot the histograms for the four variables, and then run
## pairwise t-tests to see how their magnitude compares to the others
pdf("figs/classify_results/svm4_coefs.pdf")
par(mfrow = c(2, 2), cex = 0.66)
svm4 = json_data[["svm_classify_4"]]

## coef0 -- wind speed
hist(svm4$coef0, 
     main="SVM4 Coefficients for Wind speed (m/s)",
     xlab = "Coefficients", breaks=20, xlim=c(-1, 1))
qs=quantile(svm4$coef0,
            probs=c(0.05,.95))
abline(v=qs, col="red", lwd=2)
best_estimate=quantile(svm4$coef0,
                       probs=c(0.5))
abline(v=best_estimate, col="blue", lwd=2)

## coef1 -- 24hr snow accumulation
hist(svm4$coef1, 
     main="SVM4 Coefficients for 24Hr snow accumulation (m)",
     xlab = "Coefficients", breaks=20, xlim=c(-1, 1))
qs=quantile(svm4$coef1,
            probs=c(0.05,.95))
abline(v=qs, col="red", lwd=2)
best_estimate=quantile(svm4$coef1,
                       probs=c(0.5))
abline(v=best_estimate, col="blue", lwd=2)
## coef2 -- temp
hist(svm4$coef2, 
     main="SVM4 Coefficients for Temperature (°C)",
     xlab = "Coefficients", breaks=20, xlim=c(-1, 1))
qs=quantile(svm4$coef2,
            probs=c(0.05,.95))
abline(v=qs, col="red", lwd=2)
best_estimate=quantile(svm4$coef2,
                       probs=c(0.5))
abline(v=best_estimate, col="blue", lwd=2)
## coef3 -- visibility
hist(svm4$coef3, 
     main="SVM4 Coefficients for Visibility Distance (m)",
     xlab = "Coefficients", breaks=20, xlim=c(-1, 1))
qs=quantile(svm4$coef3,
            probs=c(0.05,.95))
abline(v=qs, col="red", lwd=2)
best_estimate=quantile(svm4$coef3,
                       probs=c(0.5))
abline(v=best_estimate, col="blue", lwd=2)
dev.off()

################################################################

## bootstrap t-test to confirm that the
alpha = 0.01

print("wind-speed - snow accumulation")
test=t.test(abs(svm4$coef0),abs(svm4$coef1),mu=0,
            conf.level=1-alpha,
            var.equal=TRUE,  
            alternative="two.sided")
print(test)
print("Difference in means")
print(mean(abs(svm4$coef0))-mean(abs(svm4$coef1)))
print("************************")
print("wind-speed - temp")
test=t.test(abs(svm4$coef0),abs(svm4$coef2),mu=0,
            conf.level=1-alpha,
            var.equal=TRUE,  
            alternative="two.sided")
print(test)
print("Difference in means")
print(mean(abs(svm4$coef0))-mean(abs(svm4$coef2)))
print("************************")
print("wind-speed - visibility")
test=t.test(abs(svm4$coef0),abs(svm4$coef3),mu=0,
            conf.level=1-alpha,
            var.equal=TRUE,  
            alternative="two.sided")
print(test)
print("Difference in means")
print(mean(abs(svm4$coef0))-mean(abs(svm4$coef3)))
print("************************")
###########################################################
print("************************")
print("snow-accumulation - temp")
test=t.test(abs(svm4$coef1),abs(svm4$coef2),mu=0,
            conf.level=1-alpha,
            var.equal=TRUE,  
            alternative="two.sided")
print(test)
print("Difference in means")
print(mean(abs(svm4$coef1))-mean(abs(svm4$coef2)))
print("************************")
print("snow-accumulation - visibility")
test=t.test(abs(svm4$coef1),abs(svm4$coef3),mu=0,
            conf.level=1-alpha,
            var.equal=TRUE,  
            alternative="two.sided")
print(test)
print("Difference in means")
print(mean(abs(svm4$coef1))-mean(abs(svm4$coef3)))

###########################################################
print("************************")
print("temp - visibility")
test=t.test(abs(svm4$coef2),abs(svm4$coef3),mu=0,
            conf.level=1-alpha,
            var.equal=TRUE,  
            alternative="two.sided")
print(test)
print("Difference in means")
print(mean(abs(svm4$coef2))-mean(abs(svm4$coef3)))
print("************************")
