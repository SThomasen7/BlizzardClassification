#!/bin/python3

import make_sample as ms
import numpy as np
from sklearn import svm
from scipy.stats import rv_histogram
from sklearn.preprocessing import StandardScaler
import copy
import json
from multiprocessing import Pool

from sklearnex import patch_sklearn
patch_sklearn()

blizzard_raw, snow_raw = ms.load_data()
blizzard_raw = ms.group_blizzard_data(blizzard_raw)

def individual_classify(decision_function, blizzard, snow, print_stats=True):
    ## classify based on the NWS definition
    ## Requirements are:
    ## 35+ mph winds (15.6 m/s)
    ## visibility reduced to .25 miles for at least 3 hours  (402 meters)
    true_positive = 0
    false_positive = 0

    for key, value in blizzard.items():
        if decision_function(value):
            true_positive += 1

    for key, value in snow.items():
        if decision_function(value):
            false_positive += 1

    true_negative = len(snow) - false_positive
    false_negative = len(blizzard) - true_positive
    if true_positive + false_positive == 0:
        precision = 0
    else:
        precision = true_positive / (true_positive+false_positive)
    if true_positive + false_negative == 0:
        recall = 0
    else:
        recall = true_positive / (true_positive+false_negative)

    if print_stats:
        print(f"""
NWS Criteria results:
    Confusion Matrix
     [TP FN] [{true_positive} {false_negative}]
     [FP TN] [{false_positive} {true_negative}]

    Precision: {precision:.2f}
    Recall:    {recall:.2f}
        """)

    return {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "true_negative": true_negative,
            "false_negative": false_negative,
            "precision": precision,
            "recall": recall
    }

def definition_classify(blizzard, snow):
    """ Classify based on NWS definition """
    def is_blizzard_nws(data):
        ## return true if wind is greater than 15.6 m/s at any point
        ## AND
        ## the time delta for rows that have a visibility leq to 402 for at least 3 hours

        wind_condition = False
        visb_condition = 0

        prev = None
        if len(data) == 1:
            return False
        for _, row in data.iterrows():
            if row.wind_speed >= 15.60:
                wind_condition = True

            if prev is None:
                prev = ms.make_datetime(row.time)

                try:
                    if row.visibility_distance <= 403:
                        visb_condition += \
                            (ms.make_datetime(list(data.iterrows())[1][1].time) -
                            prev).total_seconds()
                    continue
                except Exception as e:
                    print("Exception here")
                    print(data)
                    print(list(data.iterrows())[1])
                    raise Exception()


            if row.visibility_distance <= 403:
                current = ms.make_datetime(row.time)
                visb_condition += (current-prev).total_seconds()
                prev = current

        return wind_condition and (visb_condition/3600) >= 3
    return individual_classify(is_blizzard_nws, blizzard, snow)

def threshold_classify_browne(blizzard, snow):
    """Classify the data as compound events as browne had"""
    max_val = 0
    max_result = None
    for x in np.linspace(0, 10, 100):
        threshold = x
        def is_blizzard_browne(data):
            ## Is blizzard if the daily average wind speed is greater than 7 m/s
            ## AND
            ## daily accumulation is greater than 10 mm
            
            if np.max(data.snow_accumulation)*22.4 > threshold and \
                        np.mean(data.wind_speed) > 7:
                return True
            return False

        stats = individual_classify(is_blizzard_browne, blizzard, snow, print_stats=False)
        stat = stats["precision"]+stats["recall"]

        if stat > max_val:
            max_val = stat
            max_result = (threshold, stats)

    out = max_result[1]
    out["threshold"] = max_result[0]
    return out
    #print(max_result[0])
    #print(max_result[1])

def zeroR_classify(blizzard, snow):
    def is_blizzard_zeror(data):
        return True

    stats = individual_classify(is_blizzard_zeror, blizzard, snow, print_stats=False)
    return stats


def svm_classify_generic(blizzard, snow, entry_fctor):
    ## classify the data using an SVM, but only the variables: 
    ##      wind_speed, temp, snow_accumulation

    train_x, train_y, test_x, test_y = ms.make_train_test_split(snow, blizzard)

    ## let's make each x value the mean of the variables
    train_x2 = list()
    test_x2 = list()
    for entry in train_x:
        train_x2.append(entry_fctor(entry))

    for entry in test_x:
        test_x2.append(entry_fctor(entry))

    train_x2 = StandardScaler().fit_transform(train_x2)
    test_x2 = StandardScaler().fit_transform(test_x2)
    clf = svm.LinearSVC(dual=True, max_iter=10000)
    clf.fit(train_x2, train_y)
    pred_y = clf.predict(test_x2)
    print(clf.coef_)

    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0
    for i in range(len(test_x)):
        if test_y[i] == 0:
            if pred_y[i] == 0:
                true_negative += 1
            else:
                false_positive += 1
        else:
            if pred_y[i] == 0:
                false_negative += 1
            else:
                true_positive += 1
    precision, recall = make_prec_recall(true_positive, false_positive,
            true_negative, false_negative)
    stats = {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "true_negative": true_negative,
            "false_negative": false_negative,
            "precision": precision,
            "recall": recall,
    }

    for i, c in enumerate(clf.coef_.tolist()[0]):
        stats[f"coef{i}"] = c

    return stats

def svm_classify_2(blizzard, snow):
    def fctor(data):
        return [np.mean(data.wind_speed), 
                np.mean(data.snow_accumulation)]
    return svm_classify_generic(blizzard, snow, fctor)

def svm_classify_3(blizzard, snow):
    def fctor(data):
        return [np.mean(data.wind_speed), 
                np.mean(data.snow_accumulation), 
                np.mean(data.temp)]
    return svm_classify_generic(blizzard, snow, fctor)

def svm_classify_4(blizzard, snow):
    def fctor(data):
        return [np.mean(data.wind_speed), 
                np.mean(data.snow_accumulation), 
                np.mean(data.temp),
                np.mean(data.visibility_distance)]
    return svm_classify_generic(blizzard, snow, fctor)

def svm_classify_2alt(blizzard, snow):
    def fctor(data):
        return [np.mean(data.wind_speed), 
                np.mean(data.visibility_distance)]
    return svm_classify_generic(blizzard, snow, fctor)


def naive_bayes_generic(blizzard, snow, data_fctor):
    train_x, train_y, test_x, test_y = ms.make_train_test_split(snow, blizzard)

    parameters_blizzard = list()
    parameters_snow = list()
    for i, storm in enumerate(train_x):
        for _, row in storm.iterrows():
            variables = data_fctor(row)

            if parameters_blizzard == list():
                for v in variables:
                    parameters_blizzard.append(list())
                    parameters_snow.append(list())

            for j, v in enumerate(variables):
                if train_y[i] == 1:
                    parameters_blizzard[j].append(v)
                else:
                    parameters_snow[j].append(v)

    ## get the probabilities of the classes
    p_blizzard = np.sum(test_y) / len(test_y)
    p_snow = 1-p_blizzard

    ## create the PDFs of each variable
    pdfs_blizzard = list()
    pdfs_snow = list()
    histograms = {"blizzard": list(), "snow": list()}
    ## create pdfs for blizzards
    for row in parameters_blizzard:
        #print(row)
        histograms["blizzard"].append(np.histogram(row, bins=500))
        pdfs_blizzard.append(
            rv_histogram(histograms["blizzard"][-1])
        )
    ## create pdfs for snow
    for row in parameters_snow:
        histograms["snow"].append(np.histogram(row, bins=500))
        pdfs_snow.append(
            rv_histogram(histograms["blizzard"][-1])
        )

    ## this concludes the training phase

    ## next we will calculate the likelihood of each point, and average across all points
    ## in the blizzard, and assign according to the maximum

    pred_y = list()
    for storm in test_x:
        ps_blizzard = list()
        ps_snow = list()
        for _, row in storm.iterrows():
            p_row_blizzard = 1.0
            p_row_snow = 1.0
            for i, var in enumerate(data_fctor(row)):
                p_row_blizzard *= pdfs_blizzard[i].pdf(var)
                p_row_snow *= pdfs_snow[i].pdf(var)

            ps_blizzard.append(p_row_blizzard)
            ps_snow.append(p_row_snow)
        if np.mean(ps_blizzard)*p_blizzard > np.mean(ps_snow)*p_snow:
            pred_y.append(1)
        else:
            pred_y.append(0)
            
    ## given the predicted y calculate our metrics
    true_negative = 0
    false_negative = 0
    true_positive = 0
    false_positive = 0
    for i in range(len(test_x)):
        if test_y[i] == 0:
            if pred_y[i] == 0:
                true_negative += 1
            else:
                false_positive += 1
        else:
            if pred_y[i] == 0:
                false_negative += 1
            else:
                true_positive += 1
    precision, recall = make_prec_recall(true_positive, false_positive,
            true_negative, false_negative)
    return {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "true_negative": true_negative,
            "false_negative": false_negative,
            "precision": precision,
            "recall": recall,
    }

def naive_bayes_2(blizzard, snow):
    def fctor(data):
        return [data.wind_speed, data.snow_accumulation]
    return naive_bayes_generic(blizzard, snow, fctor)

def naive_bayes_3(blizzard, snow):
    def fctor(data):
        return [data.wind_speed, data.snow_accumulation, data.temp]
    return naive_bayes_generic(blizzard, snow, fctor)

def naive_bayes_4(blizzard, snow):
    def fctor(data):
        return [data.wind_speed, data.snow_accumulation, data.temp,
                    data.visibility_distance]
    return naive_bayes_generic(blizzard, snow, fctor)

def naive_bayes_2alt(blizzard, snow):
    def fctor(data):
        return [data.wind_speed, data.visibility_distance]
    return naive_bayes_generic(blizzard, snow, fctor)

def make_prec_recall(true_positive, false_positive,
        true_negative, false_negative):
    if true_positive + false_positive == 0:
        precision = 0
    else:
        precision = true_positive / (true_positive+false_positive)
    if true_positive + false_negative == 0:
        recall = 0
    else:
        recall = true_positive / (true_positive+false_negative)
    return precision, recall

def repeat_experiments(N=3):
    metrics_template =  {
            "true_positive": list(),
            "false_positive": list(),
            "true_negative": list(),
            "false_negative": list(),
            "precision": list(),
            "recall": list()
    }

    results = dict()

    ## run the experiments
    for i in range(N):
        blizzard, snow = ms.sample_non_blizzard(blizzard_raw, snow_raw)
        print(i)

        classifiers = [definition_classify, threshold_classify_browne, zeroR_classify,
                svm_classify_2, svm_classify_3, svm_classify_4, svm_classify_2alt,
                naive_bayes_2, naive_bayes_3, naive_bayes_4, naive_bayes_2alt]
        
        for classifier in classifiers:
            if classifier.__name__ not in results:
                results[classifier.__name__] = copy.deepcopy(metrics_template)

            ## run the experiment
            result = classifier(blizzard, snow)

            ## record the results
            for key in result.keys():
                if key not in results[classifier.__name__]:
                    results[classifier.__name__][key] = list()
                results[classifier.__name__][key].append(result[key])

    return results

if __name__ == "__main__":
    #results = repeat_experiments(2)
    #with open("results.json", 'w') as fptr:
        #json.dump(results, fptr, indent=2)

    p_count = 32
    rep_count = 8
    with Pool(processes=p_count) as pool:
        results = pool.map(repeat_experiments, [rep_count]*p_count)

    print(f"{p_count} Threads executing {rep_count} experiments for a total of: "
          f"{p_count*rep_count}")
    ## converge the results
    resultsc = dict()
    for entry in results:
        for classifier in entry.keys():
            
            if classifier not in resultsc:
                resultsc[classifier] = dict()

            for metric in entry[classifier].keys():
                if metric not in resultsc[classifier]:
                    resultsc[classifier][metric] = list()

                ## append the results
                resultsc[classifier][metric] += entry[classifier][metric]


    ## print the results
    for classifier in resultsc.keys():
        print(classifier)
        for metric in resultsc[classifier]:
            print(f"  {metric}: {np.mean(resultsc[classifier][metric]):.3f}")

    with open("results.json", 'w') as fptr:
        json.dump(resultsc, fptr, indent=2)
