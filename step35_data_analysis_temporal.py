#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Step 3X Preprocessing: Data analysis for temporal data
License_info: ISC
ISC License

Copyright (c) 2020, Alexander Wendt

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

# Futures
#from __future__ import print_function

# Built-in/Generic Imports
import os

# Libs

import argparse
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import matplotlib as m
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

# Own modules
import data_visualization_functions as vis
import data_handling_support_functions as sup

__author__ = 'Alexander Wendt'
__copyright__ = 'Copyright 2020, Christian Doppler Laboratory for ' \
                'Embedded Machine Learning'
__credits__ = ['']
__license__ = 'ISC'
__version__ = '0.2.0'
__maintainer__ = 'Alexander Wendt'
__email__ = 'alexander.wendt@tuwien.ac.at'
__status__ = 'Experiental'

register_matplotlib_converters()

#Global settings
np.set_printoptions(precision=3)
#Suppress print out in scientific notiation
np.set_printoptions(suppress=True)

parser = argparse.ArgumentParser(description='Step 3.5 - Analyze Data Temporal Analysis')
parser.add_argument("-conf", '--config_path', default="config/debug_timedata_omxS30.ini",
                    help='Configuration file path', required=False)

args = parser.parse_args()


def rescale(conf, features, y):
    '''


    '''

    scaler = StandardScaler()  # Because normal distribution. Don't use minmax scaler for PCA or unsupervised learning
    # as the axis shall be centered and not shifted.
    scaler.fit(features)
    # Use this scaler also for the test data at the end
    X_scaled = pd.DataFrame(data=scaler.transform(features), index=features.index, columns=features.columns)
    print("Unscaled values")
    print(features.iloc[0:2, :])
    print("Scaled values")
    print(X_scaled.iloc[0:2, :])
    scaler.fit(y.reshape(-1, 1))
    y_scaled = pd.DataFrame(data=scaler.transform(y.reshape(-1, 1)), index=features.index, columns=[conf['Common'].get('class_name')])
    print("Unscaled values")
    print(y[0:10])
    print("Scaled values")
    print(y_scaled.iloc[0:10, :])

    return X_scaled, y_scaled

def analyze_timegraph(source, features, y, conf, image_save_directory):
    '''


    '''

    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    from statsmodels.stats.diagnostic import acorr_ljungbox

    # Autocorrelation

    # Source: https://machinelearningmastery.com/gentle-introduction-autocorrelation-partial-autocorrelation/

    #### Autoregression Intuition

    # Consider a time series that was generated by an autoregression(AR) process with a lag of k.We know that the
    # ACF describes the autocorrelation between an observation and another observation at a prior time step
    # that includes direct and indirect dependence information.This means we would expect the ACF for
    # the AR(k) time series to be strong to a lag of k and the inertia of that relationship would
    # carry on to subsequent lag values, trailing off at some point as the effect was weakened.
    # We know that the PACF only describes the direct relationship between an observation and its lag.
    # This would suggest that there would be no correlation for lag values beyond k.
    # This is exactly the expectation of the ACF and PACF plots for an AR(k) process.

    #### Moving Average Intuition

    # Consider a time series that was generated by a moving average(MA) process with a lag of k.Remember that the
    # moving average process is an autoregression model of the time series of residual errors from prior
    # predictions.Another way to think about the moving average model is that it corrects future forecasts
    # based on errors made on recent forecasts.We would expect the ACF for the MA(k) process to show a strong
    # correlation with recent values up to the lag of k, then a sharp decline to low or no correlation.
    # By definition, this is how the process was generated.For the PACF, we would expect the plot to show a
    # strong relationship to the lag and a trailing off of correlation from the lag onwards.Again, this is
    # exactly the expectation of the ACF and PACF plots for an MA(k) process.

    # if the autocorrelation function has a very long tail, then it is no stationary process

    m.rc_file_defaults()  # Reset sns

    # Here, the time graph is selected
    print("Plot the total autocorrelation of the price.The dark blue values are the correlation of the price with "
          "the lag. The light blue cone is the confidence interval. If the correlation is > cone, the value is "
          "significant.")

    vis.plot_autocorrelation(np.log(source['Close']), "OMXS30", mode="acf", lags=None, xlim=None, ylim=None, image_save_directory=image_save_directory)

    vis.plot_autocorrelation(np.log(source['Close']), "OMXS30_700_first", mode="acf", lags=None, xlim=[0, 700], ylim=None,
                         image_save_directory=image_save_directory)

    vis.plot_autocorrelation(np.log(source['Close']), "OMXS30", mode="pacf", lags=200, xlim=None, ylim=None,
                         image_save_directory=image_save_directory)

    vis.plot_autocorrelation(np.log(source['Close']), "OMXS30_first_10", mode="pacf", lags=50, xlim=[0, 10], ylim=None,
                         image_save_directory=image_save_directory)


    vis.plot_autocorrelation(features.MA200Norm, "OMXS30_MA200", mode="acf", lags=None, xlim=None, ylim=None,
                         image_save_directory=image_save_directory)

    vis.plot_autocorrelation(features.MA200Norm, "OMXS30_MA200_first_200", mode="acf", lags=None, xlim=[0, 200], ylim=None,
                         image_save_directory=image_save_directory)

    vis.plot_autocorrelation(features.MA200Norm, "OMXS30_MA200", mode="pacf", lags=200, xlim=None, ylim=None,
                         image_save_directory=image_save_directory)

    # Plot difference between time values to see if the differences are stationary
    diff = pd.DataFrame(data=np.divide(source['Close'] - source['Close'].shift(1), source['Close'])).set_index(source['Date'])
    diff = diff.iloc[1:, :]
    fig = plt.figure(figsize=(15, 4))
    plt.plot(source['Date'].iloc[1:], diff)
    plt.grid()

    # Here, the time graph is selected
    print(
        "Plot the total autocorrelation of the price. The dark blue values are the correlation of the price with the lag. " +
        "The light blue cone is the confidence interval. If the correlation is > cone, the value is significant.")

    vis.plot_autocorrelation(diff, "OMXS30_difference", mode="acf", lags=None, xlim=[0, 50], ylim=[-0.2, 0.2],
                         image_save_directory=image_save_directory)

    vis.plot_autocorrelation(diff, "OMXS30_difference", mode="pacf", lags=100, xlim=[0, 50], ylim=[-0.2, 0.2],
                         image_save_directory=image_save_directory)


    #Plot temporal correlation
    X_scaled, y_scaled = rescale(conf, features, y)
    # Correlation graphs for temporal correlation
    vis.plot_temporal_correlation_feature(X_scaled, conf['Common'].get('dataset_name'), image_save_directory, source, y_scaled)


def main():
    conf = sup.load_config(args.config_path)
    features, y, df_y, class_labels = sup.load_features(conf)

    source_filename = conf['Paths'].get("training_data_directory") + "/" + conf['Common'].get('dataset_name') + "_source" + ".csv"
    source = sup.load_data_source(source_filename)

    image_save_directory = conf['Paths'].get('result_directory') + "/analysis_data_analysis"

    analyze_timegraph(source, features, y, conf, image_save_directory)
    #analyse_features(features, y, class_labels, source, conf, image_save_directory)


if __name__ == "__main__":

    main()

    print("=== Program end ===")