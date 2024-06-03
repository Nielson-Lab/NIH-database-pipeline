#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 11:33:35 2019

@author: kirsh012

# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

Description: This module calculates the statistics for the given file in the Inputs folder. These descriptive stats are

    - Percent missing
    - # unique values
    - Mean
    - Median
    - Min
    - Max
    - Mode
    - Variance
    - Standard Deviation
    - 5th percentile
    - 95th percentile
    - Skewness
    - Kurtosis
    - Value Range (for up to 10 unique values)

"""

import numpy as np
import pandas as pd
import csv
from collections import defaultdict

def read_csv(file):
    ''' Reads the merged file that you want to get statistics for '''

    with open(file, 'r') as fin:

        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(fin.readline())
        fin.seek(0)
        delim = str(dialect.delimiter)
        reader = csv.DictReader(fin, delimiter = delim)

        data = defaultdict(list)
        for row in reader:

            for key, value in row.items():

                data[key].append(value)


    return data

def make_stats_dict_from_file(dd):

    stats_dict = {}

    for key, values in dd.items():
        stats_dict[key] = {}
        try_stats(stats_dict, key, values)

    return stats_dict




def make_stats_dict_in_pipeline(dd):

    stats_dict = {}

    columns = [k for k in dd[list(dd.keys())[0]]]
    #print(columns)
    for column in columns:
        stats_dict[column] = {}
        col_values = []
        for subject, values in dd.items():
            #print(values)
            col_values.extend(values[column])

        try_stats(stats_dict, column, col_values)


    return stats_dict

# Consider using pandas Series instead of numpy arrays
def get_mean(array): # TypeError
    mean = pd.to_numeric(pd.Series(array), errors = 'coerce').mean()
    return mean #np.nanmean(array, axis = None)

def get_median(array): # TypeError
    median = pd.to_numeric(pd.Series(array), errors='coerce').median()
    return median #np.nanmedian(array, axis = None)

def get_min(array): # TypeError
    m = pd.to_numeric(pd.Series(array), errors='coerce').min()
    return m #np.nanmin(array, axis = None)

def get_max(array): # TypeError
    m = pd.to_numeric(pd.Series(array), errors = 'coerce').max()
    return m #np.nanmax(array, axis = None)

def get_mode(array):
    #mode, count = stats.mode(array, axis = None, nan_policy = 'omit')
    mode = pd.to_numeric(pd.Series(array), errors='ignore').mode()#[0]
    if len(mode) != 0:
        mode = mode[0]
    else:
        mode = np.nan
    return mode

def get_5th_percentile(array):
    q = pd.to_numeric(pd.Series(array), errors='coerce').quantile(0.05)
    return q #np.nanquantile(array, 0.05, axis = None)

def get_95th_percentile(array):
    q = pd.to_numeric(pd.Series(array), errors='coerce').quantile(0.95)
    return q #np.nanquantile(array, 0.95, axis = None)

def get_variance(array):
    var = pd.to_numeric(pd.Series(array),errors='coerce').var()
    return var #np.nanvar(array, axis = None)

def get_std(array):
    std = pd.to_numeric(pd.Series(array),errors='coerce').std()
    return std #np.nanstd(array, axis = None)

def get_skew(array):
    skew = pd.to_numeric(pd.Series(array),errors='coerce').skew()
    return skew #stats.skew(array, axis = None, nan_policy = 'omit')

def get_kurtosis(array):
    kurt = pd.to_numeric(pd.Series(array),errors='coerce').kurt()
    return kurt #stats.kurtosis(array, axis = None, nan_policy = 'omit')

def get_unique(array):

    uni = pd.Series(array).nunique() #/ len(array) * 100
    return uni #len(np.unique(array[~np.isnan(array)])) / len(array) * 100

def get_missing(array):

    miss = array.isnull().sum() / len(array) * 100
    return miss #um(np.isnan(array)) / len(array) * 100

def get_value_range(array):
    value_range = pd.Series(array.unique()).sort_values().tolist()
    if len(value_range) <= 10:
        return str(value_range)
    else:
        return "Element has more than 10 unique values"

def try_stats(d, col, array):
    array = pd.Series(array).replace("", np.nan)
    try:
        d[col]['% Missing'] = get_missing(array)
    except TypeError:
        d[col]['% Missing'] = np.nan

    try:
        d[col]['# Unique Values'] = get_unique(array)
    except TypeError:
        d[col]['# Unique Values'] = np.nan

    try:
        d[col]['Mean'] = get_mean(array)

    except TypeError:
        d[col]['Mean'] = np.nan

    try:
        d[col]['Median'] = get_median(array)
    except TypeError:
        d[col]['Median'] = np.nan

    try:
        d[col]['Min'] = get_min(array)
    except TypeError:
        d[col]['Min'] = np.nan

    try:
        d[col]['Max'] = get_max(array)
    except TypeError:
        d[col]['Max'] = np.nan

    try:
        d[col]['Mode'] = get_mode(array)
    except TypeError:
        d[col]['Mode'] = np.nan

    try:
        d[col]['Variance'] = get_variance(array)
    except TypeError:
        d[col]['Variance'] = np.nan

    try:
        d[col]['Standard Deviation'] = get_std(array)
    except TypeError:
        d[col]['Standard Deviation'] = np.nan

    try:
        d[col]['5th Percentile'] = get_5th_percentile(array)
    except TypeError:
        d[col]['5th Percentile'] = np.nan

    try:
        d[col]['95th Percentile'] = get_95th_percentile(array)
    except TypeError:
        d[col]['95th Percentile'] = np.nan

    try:
        d[col]['Skewness'] = get_skew(array)
    except TypeError:
        d[col]['Skewness'] = np.nan

    try:
        d[col]['Kurtosis'] = get_kurtosis(array)
    except TypeError:
        d[col]['Kurtosis'] = np.nan

    try:
        d[col]['Value Range'] = get_value_range(array)
    except TypeError:
        d[col]['Value Range'] = np.nan

    return d

def dict_to_csv(dd, savename):
    usecols = ['Name', '% Missing', '# Unique Values', 'Mean', 'Median', 'Min', 'Max', 'Mode', \
               'Variance', 'Standard Deviation', '5th Percentile', '95th Percentile', \
               'Skewness', 'Kurtosis', 'Value Range']

    with open(savename, 'w') as fout:
        writer = csv.DictWriter(fout, fieldnames = usecols, lineterminator = '\n')

        writer.writeheader()

        for var in dd:
            temp_dd = {c: v for c, v in dd[var].items()}
            temp_dd["Name"] = var
            writer.writerow(temp_dd)

    return
