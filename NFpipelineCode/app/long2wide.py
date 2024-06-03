#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

Description: This module converts a dataset in a longitudninal format to a wide format.
"""
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats
from functools import reduce
from itertools import combinations
from datetime import datetime
from dateutil.parser import parse
import operator
import re
import time
import glob
import csv
import pprint
import logging

def convert_to_time(s, intindc, indicator):

    if intindc:
        #date = s
        logging.info("Chose the intindc")
        date = re.sub('\s', '_', s.strip())
    else:
        try:
            date = float(s)
            logging.info("Float Try")
        except ValueError:
            date = parse(s)
            #try:
            #    date = datetime.strptime(s, "%m/%d/%Y")
            #    print("Expected date format: ", date)
            #except ValueError:
            #    try:
            #        date = datetime.strptime(s, "%m-%d-%Y")
            #        print("Second Exception")
            #    except ValueError:
            #        try:
            #            date = datetime.strptime(s, "%Y/%m/%d")
            #            print("Third Exception")
            #        except ValueError:
            #            try:
            #                date = datetime.strptime(s, "%Y-%m-%d")
            #                print("Fourth Exception")
            #            except ValueError:
            #                #s = s.strip()
            #                if indicator:
            #                    date = re.sub('\s', '_', s.strip())
            #                else:
            #                    raise ValueError("Unknown date format. Please revise")
            #            #print(f"Date {s} is an unknown datetime format. Please correct and try again.")

        except TypeError:
            #date = s
            logging.info("TypeERROR")
            date = re.sub('\s', '_', s.strip())

    return date

def read_csv(file, id_col, date_col):
    ''' Reads the merged file that you want to convert from long to wide format '''

    with open(file, 'r', encoding = 'utf-8-sig') as fin:

        csvreader = csv.reader(fin)
        columns = next(csvreader)

        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(fin.readline())
        fin.seek(0)
        delim = str(dialect.delimiter)
        reader = csv.DictReader(fin, delimiter = delim)

        data = {}
        for row in reader:
            key = (row[id_col], row[date_col])

            if key not in data:
                data[key] = defaultdict(list)

            for col in columns:
                if col not in [id_col, date_col]:
                    value = row.get(col, '')
                    data[key][col].append(value)
        #data = {}
        #for row in reader:
        #    #print(row)
        #    key = (row[id_col], row[date_col]) #convert_to_time(row[date_col], indicator))
        #
        #    #if key not in data:
        #    data[key] = {}#defaultdict(list)
        #    for col in columns:
        #        if col not in [id_col, date_col]:
        #            value = row.get(col, '')
        #            data[key][col] = value



    return data

def aggregate_data(dd, aggfunc, *args, **kwargs): # src,

    #if aggfunc == 'mean':
    #    aggfunc = np.nanmean
    #elif aggfunc == 'median':
    #    aggfunc = np.nanmedian
    #elif aggfunc == 'mode':
    #    aggfunc = lambda x: stats.mode(x)[0][0]
    #elif aggfunc == 'first':
    #    aggfunc = lambda x: x[0]
    #elif aggfunc == 'last':
    #    aggfunc = lambda x: x[-1]
    #else:
    #    aggfunc = lambda x: x

    for key in dd:

        for k, v in dd[key].items():

            if aggfunc == 'mean':
                try:
                    nv = np.array(list(map(lambda x: float(x) if x != '' else np.nan, v))) #pd.to_numeric(pd.Series(v), errors = 'coerce').mean()  #
                    dd[key][k] = np.nanmean(nv)
                except (TypeError, ValueError) as e:
                    # usually because these are categorical variables, get the mode
                    dd[key][k] = stats.mode(v)[0][0]#np.nan

            elif aggfunc == 'median':
                try:
                    nv = np.array(list(map(lambda x: float(x) if x != '' else np.nan, v)))
                    dd[key][k] = np.nanmedian(nv) # pd.to_numeric(pd.Series(nv), errors='coerce').median() #
                except (TypeError, ValueError) as e:
                    # Sort row then get the middle index
                    mdx = int(len(v) / 2)
                    dd[key][k] = sorted(v)[mdx]

            elif aggfunc == 'mode':
                #nv = pd.to_numeric(pd.Series(v), errors='ignore').mode()
                #if len(nv) != 0:
                #    dd[key][k] = nv[0]
                #else:
                #    dd[key][k] = np.nan
                # Original
                dd[key][k] = stats.mode(v)[0][0]

            elif aggfunc == 'first':
                dd[key][k] = v[0]
            elif aggfunc == 'last':
                dd[key][k] = v[-1]
            elif aggfunc == 'none':
                dd[key][k] = v

            '''
            try:
                if aggfunc.__name__ == 'nanmean' or aggfunc.__name__ == 'nanmedian':
                    nv = np.array(list(map(lambda x: float(x) if x != '' else np.nan, v)))
                else:
                    nv = v
                dd[key][k] = aggfunc(nv, *args, **kwargs)
            except TypeError:
                dd[key][k] = np.nan
            except ValueError:
                dd[key][k] = np.nan
            '''
    return dd

def split_keys(dict1, indicator):
    '''
    Splits the original (ID, Date) key into nested keys. Returns dict like
    {'ID': [{'Date1': values1}, {'Date2: values2'}]}
    '''

    newd = defaultdict(list)
    for key, val in dict1.items():
        ndd = {}
        id_key = key[0]
        time_key = key[1]#convert_to_time(key[1], indicator)

        ndd[time_key] = val
        newd[id_key].append(ndd)

    return newd

def make_time_keys(dd, time_int, suffix, intindc, indc): # remove source,
    '''
    Converts the time keys into time intervals based on the desired grouping (in days)
    then renames the keys to reflect the interval.
    '''
    #time_int = float(time_int)
    #time_points = []
    for key, val in dd.items():

        for i in range(len(dd[key])):
            #print(i)
            #if source == 'NDA' and i == 0:
            #    date = list(dd[key][i+1].keys())[0]
            #    print(date)
            #else:
            date = list(dd[key][i].keys())[0]
            if date == '':
                continue

            usedate = convert_to_time(date, intindc, indc)
            if i == 0:

                baseline = usedate
                if isinstance(usedate, float) or isinstance(usedate, int):
                    time_passed = usedate - baseline
                    #if date not in time_points:
                    #    time_points.append(date)
                elif isinstance(usedate, datetime):
                    time_passed = (usedate - baseline).days

                elif isinstance(usedate, str):
                    time_passed = usedate
                    # Check for the description row in NDA


            else:
                if isinstance(usedate, float) or isinstance(usedate, int):
                    time_passed = usedate - baseline
                    #if date not in time_points:
                    #    time_points.append(date)
                elif isinstance(usedate, datetime):
                    time_passed = (usedate - baseline).days

                elif isinstance(usedate, str):
                    time_passed = usedate

            try:
                time_int = float(time_int)
                #print(time_passed)
                #print(time_int)
                grouped_time = int(np.floor(time_passed/time_int))
                #print(grouped_time)


                if isinstance(usedate, float) or isinstance(usedate, int):
                    new_key = f"{suffix}{int(time_passed)}"
                else:
                    new_key = f"{suffix}{grouped_time}"

            except (TypeError, ValueError) as e:
                new_key = f"{suffix}{date}"
            #except TypeError:
            #    new_key = f"{suffix}{date}"
            #    #grouped_time = int(np.floor(time_passed/time_int))
            #    #new_key = f"{suffix}{grouped_time}
            ##print(key)
            dd[key][i][new_key] = dd[key][i].pop(date)

    return dd#, time_points

def convert_long_to_wide(dd, ti, suff, intindc, savecols, indicator=False, aggfunc=False):

    '''
    This function takes a dictionary and converts it from longitudinal format
    to wide format.
    '''

    start = time.time()
    logging.info(f"Loaded aggfunc in long2wide: {aggfunc}")
    if aggfunc:

        aggfunc = aggfunc[0]
        logging.info(f"AGGFUNC in long2wide True: {aggfunc}")
        dd = aggregate_data(dd, aggfunc) # source,
    # Split the original (ID, Date) key into nested keys
    new_dict = split_keys(dd, indicator)

    # Create new dictionary of the columns that are not going to be transformed
    save_cols = savecols.split(';')
    safe_dict = {}
    for key in new_dict.keys():

        safe_dict[key] = {}
        for scol in save_cols:
            #print(scol)

            for n in range(len(new_dict[key])):

                for k in new_dict[key][n].keys():

                    if scol != '':
                        safe_dict[key][scol] = new_dict[key][n][k][scol]
                        #safe_dict[key] = {scol: new_dict[key][n][k][scol]}
                        #print(safe_dict)
                        new_dict[key][n][k].pop(scol)

    #print(safe_dict)
    # Convert the time keys into times
    new_dd = make_time_keys(new_dict, ti, suff, intindc, indicator) # remove source

    new_DD = {}
    for sub_key in new_dd:
        temp_dd = {key: [d.get(key) for d in new_dd[sub_key]] \
                    for key in set().union(*new_dd[sub_key])}

        for k in temp_dd:
            temp_dd[k] = [Dd for Dd in temp_dd[k] if Dd is not None]

        new_DD[sub_key] = temp_dd

    for key in new_DD:
        for tkey in new_DD[key]:
            new_DD[key][tkey] = {k: [d.get(k) for d in new_DD[key][tkey]] \
                            for k in set().union(*new_DD[key][tkey])}

    # Combine month keys with column Keys
    columns = []
    final_dict = defaultdict(dict)
    for KEY, VAL in new_DD.items():
        IDKEY = KEY
        for k, v in VAL.items():
            TKEY = k
            for kk, vv in v.items():
                new_key = f"{kk}_{TKEY}"
                final_dict[IDKEY][new_key] = vv[0]
                if new_key not in columns:
                    columns.append(new_key)

    # Merge columns we didn't transform with the final dictionary
    for ID, sub_dd in safe_dict.items():
        #print(sub_dd)
        #print(final_dict[ID])
        for save_col, save_val in sub_dd.items():
            #print(save_col)
            final_dict[ID][save_col] = save_val

    columns = save_cols + columns
    return final_dict, columns


def write_to_csv(dd, columns, filename, id_col):
    assert isinstance(dd, dict), "dd must be a dictionary"
    assert isinstance(columns, list), "columns must be a list"
    assert isinstance(filename, str), "filename must be a string"
    assert isinstance(id_col, str), "id_col must be a string"
    assert id_col not in columns, "id_col should not be in columns yet"

    # Open file to write
    with open(filename, 'w') as fout:

        # Need fieldnames to be all the columns
        #columns = sorted(columns)
        columns = [id_col] + columns

        writer = csv.DictWriter(fout, fieldnames = columns, lineterminator = '\n')
        # Write column names
        writer.writeheader()
        # Write dictionary row by row, duplicating keys as necessary
        for k in dd:
            '''
            tcols = list(dd[k].keys())

            for tcol in tcols:
                t = dd[k][tcol]

                if isinstance(t, list):
                    n = len(t)
                else:
                    n = 1

                for i in range(n):
                    temp = {}
                    if n <= 1:
                        temp[tcol] = dd[k].get(tcol, ['']*(i+1))[i]
                    else:
                        temp[tcol] = dd[k].get(tcol, '')

            temp[id_col] = k
            writer.writerow(temp)

            '''
            # The number of rows in the merged data
            tcols = list(dd[k].keys())
            #print(sorted(tcols))
            #print(sorted(columns))
            t = dd[k][tcols[0]]
            #print(t) # Last column
            #disparate_cols = list(set(columns) - set(tcols))
            #print(f"Columns missing for {k} are: ", disparate_cols)
            if isinstance(t, list):

                n = max(list(map(lambda x: len(dd[k][x]), dd[k]))) #len(t)

            else:
                n = -1

            # Values in dictionary are strings and only one per column / key
            if n == -1:
                temp = {}

                for col in columns:
                    temp[col] = dd[k].get(col, '')

                temp[id_col] = k
                writer.writerow(temp)

            else:
                for i in range(n):
                    # Create a temporary dictionary that contains the column
                    # and corresponding row value. Col names are keys in temp
                    temp = {}

                    for col in tcols: #columns:
                        #if n != 1: # Changed from != to == on Sep 10 2021
                        if len(dd[k][col]) != n:
                            extended_vals = dd[k].get(col, [''])*n
                            temp[col] = extended_vals[i] #dd[k].get(col, ['']*(i+1))[i]

                        else:
                            temp[col] = dd[k].get(col, [''])[i]

                    # To write the key, we need to add it as a column.
                    temp[id_col] = k

                    # Write row to the csv file
                    writer.writerow(temp)
                #'''

    return


#nda_test = {('AAA', '08/21/2019'): {'Col1': ['This is a description of Col1', '1','2','','4'], 'Col2':['This is a description of Col2','a','b', 'a', '']},
#            ('BBB', '08/21/2019'): {'Col1': ['This is a description of Col1', '1','2','','4'],  'Col2':['This is a description of Col2', 'a','b', 'a', '']},
#            ('AAA', '08/22/2019'): {'Col1': ['This is a description of Col1', '2','', '3', '1'], 'Col2':['This is a description of Col2', 'b', 'b', '', 'a']}}

#final_nda = convert_long_to_wide(nda_test, 1, 'Day', 'NDA', indicator = False, aggfunc = 'mean')
