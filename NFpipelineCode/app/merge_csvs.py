#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 10:55:06 2019

@author: kirsh012

# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

Description: Merges mutliple CSV files from NDA or FITBIR
"""
import csv
import copy
import numpy as np
import pandas as pd
import glob
from collections import defaultdict
import time
import long2wide
import stats_pipeline as statsp
from flask import flash
import scrape_FITBIR_data_dictionary as sfitbir
import scrape_NDA_data_dictionary as snda
import os
import logging
import chardet
import re

import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    application_path = Path(sys.executable)#sys._MEIPASS
else:
    application_path = Path(os.path.dirname(os.path.abspath(__file__)))

m = re.search('.+?(?=NFP\.)', str(application_path))
if m is None:
    #print("m is None!")
    new_path = application_path.parent.parent
    #print(new_path)
else:
    new_path = m.group(0) #application_path.parent

#For testing
import pprint
########### NOTE ###############
# NDA doesn't merge properly because of the redundant columns in the datasets - IGNORED - that's how Jessica wants it for now.
# FITBIR doesn't merge properly because of the comp_df - FIXED - removed `sorted()` in lines 99 and 120


##### Possible additions ######
# Add method to not read in certain columns --> added!
# Add method to drop columns that have all empty strings - DONE
# Add feature to merge on N columns





def merge_all(files, id_col, date_col, bind, mapping): # sep
    ### Best idea as of April 16th, 2019

    ## Collect all the unique columns across files
    columns = []
#    flash("***** Collecting the names of the columns across all files *****")
    missing_files = []
    for file in files:
        logging.info(file.split(os.sep)[-1])
        with open(file, 'rb') as rawdata:
            result = chardet.detect(rawdata.read(10000))
            encod = result['encoding']

        with open(file, 'r', encoding = encod, newline = "") as f:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(f.readline())
            f.seek(0)
            #delim = str(dialect.delimiter)
            csvreader = csv.reader(f, dialect)
            # Get just the first row, which should hold the column names
            headers = next(csvreader)
            # Only execute if column binding
            if bind == 'column':
                # Check if the merge columns are in the file
                if date_col:
                    if id_col not in headers or date_col not in headers:
                        missing_files.append(file)
                else:
                    if id_col not in headers:
                        missing_files.append(file)
            # Loop over all the columns in the file
            for h in headers:
                # If the column has not already been seen, add it to our list
                if h not in columns:
                    columns.append(h)

    merge_files = [f for f in files if f not in missing_files]
#    flash("***** The following list of files could not be merged because they are missing one or more of the columns you tried merging on *****")
#    for mf in missing_files:
#        flash(mf.split(os.sep)[-1])
#    flash("***** Finished collecting the column names from all files *****")
    # Initialize the dictionary we will store the merged data in
    data = {}

    # Check if row binding or column binding
    if bind == 'row':
        data = defaultdict(list)
        # Read all files, add each row to the dictionary to concatentate files (similar to pandas.concat)
        for file in merge_files:
            logging.info("Reading in file {} ...".format(file.split(os.sep)[-1]))
            with open(file, 'r', encoding = encod, newline = "") as f:

                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(f.readline())
                f.seek(0)
                delim = str(dialect.delimiter)
                reader = csv.DictReader(f, delimiter = delim)

                for row in reader:

                    for col in columns:

                        value = row.get(col, '')
                        # Insert mapping here

                        if mapping is not None:
                            if col in mapping:
                                new_col = mapping[col]
                                data[new_col].append(value)
                            else:
                                data[col].append(value)
                        else:
                            data[col].append(value)

                    '''# Check all columns
                    for col in columns:

                        if col not in data:
                            data[col] = []
                        #else: # Not necessar otherwise the first row of data is excluded

                        # Get the value from the column, if the column is
                        # not in the file, return an empty string
                        value = row.get(col, '')

                        data[col].append(value)
                        '''
    else:
        # Read all the files, add rows to dictionary if haven't been added, or
        # merge if they can be merged
        for file in merge_files:
#            flash("Reading in file {} ...".format(file.split(os.sep)[-1])) #.split('/')[-1]))
            with open(file, 'r') as fin:
                # Use DictReader so we can add empty strings if a column is not
                # in that file
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(fin.readline())
                fin.seek(0)
                delim = str(dialect.delimiter)
                reader = csv.DictReader(fin, delimiter = delim) #sep)
                # Loop over all the rows in the file
                for row in reader:
                    # If the user wants to include a date column (or a second column to join on)
                    if date_col:
                        # Check that the date and id columns are mapped correctly
                        if mapping is not None:
                            if date_col in mapping.keys():
                                date_col = mapping[date_col]
                            if id_col in mapping.keys():
                                id_col = mapping[id_col]
                        # Make the key a tuple with the values of the id_col and date_col in the row
                        key = (row[id_col], row[date_col])

                    # Otherwise, for a single column join (i.e. FITBIR)
                    else:
                        # Check that the date and id columns are mapped correctly
                        if mapping is not None:
                            if id_col in mapping.keys():
                                id_col = mapping[id_col]

                        key = row[id_col]

                    # Check if the key is not already in the dictionary
                    if key not in data:
                        # Initialize a dictionary of lists as the values for each key
                        # Each key in this dictionary represents a column, each element
                        # in the list is a row
                        data[key] = defaultdict(list)
                        # Check all columns
                        for col in columns:
                            # Check that column being tested is not the id_col or date_col
                            if col not in [id_col, date_col]:
                                # Get the value from the column, if the column is
                                # not in the file, return an empty string
                                value = row.get(col, '')
                                # Insert mapping here
                                if mapping is not None:
                                    if col in mapping:
                                        new_col = mapping[col]
                                        data[key][new_col].append(value)
                                    else:
                                        data[key][col].append(value)
                                else:
                                    data[key][col].append(value)
                                ## Add the value to the list
                                #data[key][col].append(value)

                    # The key is already in the dictionary
                    else:
                        # Get list of the new row values, replacing missing cols with '' if the column is not in the row
                        r_vals = [row.get(col, '') for col in columns if col not in [id_col, date_col]]
                        # Compare the two rows, merging if possible
                        data[key], get_row = compare_lists(data[key], r_vals)
                        # get_row is either True or False. Indicates whether the
                        # new row needs to be added to the dictionary, i.e. the
                        # new row could not be merged, or was not a duplicate of
                        # an existing row
                        if get_row:
                            for col in columns:
                                # Do not get the values for ID and Date cols again
                                if col not in [id_col, date_col]:
                                    # Get the value from the column, if the column is
                                    # not in the file, return an empty string
                                    value = row.get(col, '')
                                    # Insert mapping here
                                    if mapping is not None:
                                        if col in mapping:
                                            new_col = mapping[col]
                                            data[key][new_col].append(value)
                                        else:
                                            data[key][col].append(value)
                                    else:
                                        data[key][col].append(value)
                                    ## Add the value to the list
                                    #data[key][col].append(value)


    return data#, columns

def compare_lists(dd, row_vals):
    '''
    Provides the conditions to run the merge_lists function, as well as how the results of that function
    should be incorporated into the original dataset.

    Parameters
    -----------
    dd: a dict - the dictionary for a given key in data
    row_vals: a list - the incoming row that we should compare values to

    Returns
    -----------
    dd: a dict - updated dictionary (if updated)
    get_values: a boolean - tells the main script whether or not it needs to add the row_vals as a new row
    '''

    keys = list(dd.keys())
    # Get the length of the values in each column
    n = len(dd[keys[-1]]) # This will be a problem if the datasets end with the id_col or date_col. Solution: preprocess data so this won't happen

    # Loop over all values in the column
    for i in range(n):
        # Make a list for the old values in the ith row
        old_vals = [v[i] for c, v in dd.items()]
        #old_vals = []
        #for c, v in dd.items():
        #    old_vals.append(v[i])

        # Try merging the lists
        new_vals = merge_lists(row_vals, old_vals)
        #print(new_vals)
        #print(new_vals)
        # If the lists couldn't be merged
        if len(new_vals) == 2:
            # If you haven't tested every list
            if i != (n-1):
                continue
            else:
                # The new row can't be merged with any existing row
                get_values = True
                #print(get_values)
                break

        # The lists could be merged or they were identical
        else: # returns original list or merged list
            # Replace the values in the ith row with the values in the merged/original row
            for j, c in enumerate(keys):
                dd[c][i] = new_vals[j]
#            for c, v in sorted(dd.items()):
#                v[i] = new_vals[i]
            #print(get_values)
            # Do not need to add a new row
            get_values = False
            break
    #print((l1, l2))
    #print(get_values)
    return dd, get_values

def merge_lists(l1, l2):
    '''
    Description: Compares the values of two lists. If all the values match except for the '' values, then replace those '' values
    with the value in the corresponding index of the other list. Otherwise, return both lists.

    Parameters
    -----------
    l1: a list - the new list to be compared with the existing lists
    l2: a list - an existing list

    Returns
    -----------
    new_list: a list - the merged list if applicable
    [l1, l2]: a list of lists - both lists if they cannot be merged
    '''
    #print((l1, l2))
    #print(l1)
    #print(l2)
    # Check if the lists are identical. If so, return the original
    if sorted(l1) == sorted(l2):
        return l2

    # Check if the values in the list that aren't '' match.
    truth_list = []
    for x, y in zip(l1, l2): # use zip for element-to-element by index comparison
        # Check that x and y are not empty strings
        if x != '' and y != '':
            # If they match, add True to the truhList
            if x == y:
                truth_list.append(True)
            else:
                truth_list.append(False)
    #print(truth_list)
    # Only merge the lists if the values that aren't empty strings match
    if np.all(truth_list):
        # Initialize the merged list
        new_list = []
        for x, y in zip(l1, l2):
            # Find all '', val pairs
            if x != y:
                # Check if x is the empty string, then add the y value
                if x == '':
                    new_list.append(y)
                # If x is not the empty string, then y is, and we should add x to the merged list
                else:
                    new_list.append(x)
            # For all pairs that match, add x
            else:
                new_list.append(x)

        return new_list

    # If the lists can't be merged, return both of them
    else:
        return [l1, l2]

def explode(df1, l, id_col, date_col=False):
    '''
    For cells that have lists as their values, expand the list so that for
    each value, new rows are created.

    Parameters
    -----------

    '''
    #df_list = []
    #for col in cols_to_explode:
    #    flat_col = [e for sublist in df1[col] for e in sublist]
    #    rnums = df1[col].apply(len)
    #    vals = range(df1.shape[0])
    #    locs = np.repeat(vals, rnums)
    #    col_idx = [i for i, e in enumerate(df1.columns) if e != col]
    #    new_df = df1.iloc[locs, col_idx].copy()
    #    new_df[col] = flat_col
    #    df_list.append(new_df)

    #fdf = pd.concat(df_list, sort = False)
    drop_col = f"level_{l}"

    fdf = (df1.apply(lambda x: x.apply(pd.Series).stack())
             .reset_index()
             .drop(drop_col, 1)) # 'level_2'
    if date_col:
        fdf.rename(columns={'level_0': id_col, 'level_1': date_col}, inplace = True)
    else:
        fdf.rename(columns={'level_0': id_col}, inplace = True)
    return fdf

def dd_to_df(dd, l):
    #print(dd)
    '''
    Converts the data to a pandas DataFrame

    Parameters
    -----------
    dd: a dict of dict of lists - where the data is stored
    l: an int - level to unstack on

    Returns
    -----------
    rdf: a pandas.DataFrame - dataframe of merged data
    '''
    rdf = pd.DataFrame(dd).T.stack().unstack(level=[l])
    return rdf

def remove_empty_columns(dd, binding):
    '''
    Removes the columns that have all empty strings in them

    Parameters
    -----------
    dd: a dict of dicts of lists - where the merged data is stored

    Returns
    -----------
    dd: a dict of dicts of lists - modified dd without empty columns
    '''

    # Get all the columns in the file. Could be faster
    # Can do it this way because I know each subject will have the same columns,
    # which is faster than the section commented out below because I'm only
    # getting the columns from a single subject

    ### Figure out which columns are empty
    drop_cols = []

    # Row-binding dictionary is formatted differently
    if binding.lower() == 'row':
        # Get columns
        columns = list(dd.keys())
        # Each key is a column
        for col, val in dd.items():
            # Check if all values in the column are ''
            all_vals = list(set(val))
            if (len(all_vals) == 1) and (all_vals[0] == ''):
                drop_cols.append(col)

    else:
        # Get columns
        columns = [k for k in dd[list(dd.keys())[0]]]
        # Column-binding dictionary is formatted as a dictionary of dictionaries of lists
        for col in columns:
            # Initialize list to store all values in column
            test_col_vals = []
            # Keep track of the row we're on, solely because NDA makes the metdata
            # the second row in the csv file. When determining if a column is empty,
            # the metadata gets in the way, so we need to ignore it.
            # rnum = 0
            for sub, dt in dd.items():
                # # Check if files are from NDA, just because of the metadata check
                # if src.strip().upper() == 'NDA':
                #     # Ignore the metadata
                #     if rnum == 0:
                #         pass
                #     else:
                #         # Get values in the column for this subject
                #         val = dt[col]
                #         # Loop over values (could be more than one per row)
                #         for v in val:
                #             # Add to test_col_vals if not already in there. Empty
                #             # columns will have test_col_vals = ['']
                #             if v not in test_col_vals:
                #                 test_col_vals.append(v)
                #     rnum += 1
                # Files are not from NDA
                # else:
                # Get values in the columns for this subject
                val = dt[col]
                # Loop over values (could be more than one per row)
                for v in val:
                    # Add to test_col_vals if not already in there. Empty
                    # columns will have test_col_vals = ['']
                    if v not in test_col_vals:
                        test_col_vals.append(v)

            # Check if the values in col are the same.
            if len(test_col_vals) == 1:
                # Check if the only value in the column is '' whichs means the column is empty
                if test_col_vals[0] == '':
                    # Add the column to the list of empty columns
                    drop_cols.append(col)

    ### Remove empty columns from the dataset, by removing for each subject
    if binding.lower() == 'row':
        # Loop over columns in the row
        for c, v in list(dd.items()):
            # Check if c is in drop_cols, so we can drop it
            if c in drop_cols:
                # Remove c from the dictionary
                dd.pop(c, None)
    else: # Column binding has more complex keys
        for ID, dty in list(dd.items()):
            # Loop over columns in the row
            for c, v in list(dty.items()):
                # Check if c is in drop_cols, so we can drop it
                if c in drop_cols:
                    # Remove c from the dictionary
                    dty.pop(c, None)

    # Save and return the remaining columns
    final_columns = [col for col in columns if col not in drop_cols]
    return dd, final_columns

def write_to_csv(dd, columns, filename, id_col, date_col, l2w, binding):
    '''
    Writes the dictionary to a CSV file. Default uses comma as delimiter.
    I could add a variable to change as necessary.

    Parameters
    -----------
    dd: a dict of dict of lists - where the merged data is stored
    columns: a list - names of columns in all datasets
    filename: a str - path to name of file
    id_col: a str - ID key to join datasets on
    date_col: a str if provided, a bool (False) otherwise - Date key to join datasets on

    Returns
    -----------
    CSV of merged data.
    '''
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(dd)
    # if id_col not in dd:
    #     raise ValueError(f"The ID column '{id_col}' is has not been added to the dictionary prior to saving.")
    # if date_col not in dd:
    #     raise ValueError(f"The date column '{date_col}' is has not been added to the dictionary prior to saving.")

    # Row-binding save to csv
    if (binding.lower() == 'row') and not l2w: # merge only after row-binding
        # Open file to write

        with open(filename, 'w') as fout:
            # Use fieldnames as columns
            writer = csv.DictWriter(fout, fieldnames = columns, lineterminator = '\n')
            # Write column names
            writer.writeheader()

            # Write dictionary row by row
            for i in range(len(dd[columns[0]])):
                temp_dd = {c: v[i] for c, v in dd.items()}
                #if i == 0:
                #    print(temp_dd)
                writer.writerow(temp_dd)


    else:

        #if l2w:
    #        columns = [col for col in columns if col not in [id_col, date_col]]
        # Open file to write
        #print(columns)
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(dd)
        print("INSIDE THE RIGHT ELSE STATMENT")
        with open(filename, 'w') as fout:
            # print(columns)
            # Need fieldnames to be all the columns
            writer = csv.DictWriter(fout, fieldnames = columns, lineterminator = '\n')
            # Write column names
            writer.writeheader()
            # Write dictionary row by row, duplicating keys as necessary
            for k, col_dict in dd.items():

                n = len(dd[k][columns[-1]])
                for i in range(n):
                    temp = {c: v[i] for c, v in col_dict.items()}
                    # Add the GUID and Date depending on existence and data type
                    if isinstance(k, str):
                        temp[id_col] = k
                    elif isinstance(k, list) or isinstance(k, tuple):
                        temp[id_col] = k[0]
                    else:
                        print("The GUID is of type {}. You need to account for this type: ".format(type(k)))
                    # Write the date key if it exists
                    if date_col:
                        temp[date_col] = k[1]

                    writer.writerow(temp)
    return

def main(files, filename, id_col, savecols, bind, mapping = None, date_col=False, l2w = False, suffix = False, ti = False, aggfunc = False, intindc = False, *args, **kwargs):#, sep = ','):
    # Read and merge all files, store in dictionary, get set of all columns
    s = time.time()
    logging.info(f"\n{filename}")
    dd = merge_all(files, id_col, date_col, bind, mapping) # sep 2n
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(dd)

    logging.info("***** Removing empty columns from dataset *****")
    flash("***** Removing empty columns from dataset *****")
    dd, cols = remove_empty_columns(dd, bind)

    logging.info("***** Finished removing empty columns from dataset *****")
    flash("***** Finished removing empty columns from dataset *****")
    # Copy the original copy names for web scraping the data dictionaries
    og_cols = copy.deepcopy(cols)
    ### THESE STATEMENTS ARE ONLY NECESSARY IF YOU WANT TO RETURN A DATAFRAME
    ### I used this for unit-testing
    #if date_col:
    #    level = 2
    #    df = dd_to_df(dd, level)
    #    df = explode(df, level, id_col, date_col)
    #    usecols = [id_col, date_col] + [c for c in df.columns if c not in [id_col, date_col]]
    #    df = df.loc[:, usecols]

        #df = dd_to_df(dd, 2)
    #else:
    #    level = 1
    #    df = dd_to_df(dd, level)
        #print(df)
    #    df = explode(df, level, id_col)
    #    usecols = [id_col] + [c for c in df.columns if c not in [id_col, date_col]]
    #    df = df.loc[:, usecols]
        #df = dd_to_df(dd, 1)
    if l2w:

        if bind.lower() != 'row':
            logging.info("NOT SUPPOSED TO BE ROW")
            dd, cols = long2wide.convert_long_to_wide(dd, ti, suffix, intindc, savecols, indicator=False, aggfunc=aggfunc, *args, **kwargs)
            #pp = pprint.PrettyPrinter(indent=4)
            #pp.pprint(dd)
            # Add the date
        else:
            logging.info("ROW BINDING")
            # In development
            '''
            new_data = {}

            # Loop over all values
            for i, ns in enumerate(dd[id_col]):

                # This is long to wide so a date_col is assumed
                key = (ns, dd[date_col][i])

                # Check that the key is not already in the dictionary
                if key not in new_data:
                    new_data[key] = defaultdict(list)

                # Check all columns
                for col in cols:
                    if col not in [id_col, date_col]:

                        value = dd[col][i]# dd[col].get(col, '') #
                        new_data[key][col].append(value)

            '''
            # Save to CSV file then reload
            temp_name = str(new_path) + '{0}Outputs{0}'.format(os.sep) + "merged_file.csv"
            logging.info(temp_name)
            # Save the merged dataset to a CSV (works well)
            write_to_csv(dd, cols, temp_name, id_col, date_col, False, bind) # Input as False because the write_to_csv function here needs further debugging

            # load data
            new_data = long2wide.read_csv(temp_name, id_col, date_col)
            logging.info(f"AGGFUNC in Merge: {aggfunc}")
            dd, cols = long2wide.convert_long_to_wide(new_data, ti, suffix, intindc, savecols, indicator=False, aggfunc=aggfunc, *args, **kwargs)

            # The long2wide write_to_csv function adds the id_col to the file, so including it is unnecessary



    # If not converting long2wide, add id_col and date_col to the file
    else:
        if date_col:
            cols = [id_col, date_col] + cols # cols +
        else:
            cols = [id_col] + cols # cols +
    #if (bind.lower() == 'row') and not l2w: # merge only for row-binding
    #    pass
    #else:

    #    if date_col:
    #        cols = [id_col, date_col] + cols
    #    else:
    #        cols = [id_col] + cols

    #print(cols)
    #if bind.lower() != 'row':
    #    if date_col:
    #        cols = [id_col, date_col] + cols
    #    else:
    #        cols = [id_col] + cols

    # Write the dictionary to a CSV file

    flash("***** Saving dataset to CSV file *****")
    if not l2w:
        # Save merge only files
        if filename.endswith('.csv'): #filename.suffix == '.csv':#
            write_to_csv(dd, cols, filename, id_col, date_col,l2w, bind)
        elif filename.endswith('.xlsx'): #filename.suffix == '.xlsx':#
            flash("File is saved as a CSV that can be opend with Excel.")
            write_to_csv(dd, cols, filename, id_col, date_col, l2w, bind)
        elif filename.endswith('.txt'): #filename.suffix == '.txt':#
            write_to_csv(dd, cols, filename, id_col, date_col, l2w, bind)
        else:
            flash(f"Support for files that end in {filename.split('.')[-1]} is not available right now. Please contact us about adding it.")

    else:
        logging.info("LONG 2 WIDE")
        #print([dd[k]['gender'] for k in dd.keys()])
        # Save merged and transformed files
        if filename.endswith('.csv'): #filename.suffix == '.csv':#
            long2wide.write_to_csv(dd, cols, filename, id_col)
        elif filename.endswith('.xlsx'): #filename.suffix == '.xlsx':#
            flash("File is saved as a CSV that can be opend with Excel.")
        elif filename.endswith('.txt'): #filename.suffix == '.txt':#
            long2wide.write_to_csv(dd, cols, filename, id_col)
        else:
            flash(f"Support for files that end in {filename.split('.')[-1]} is not available right now. Please contact us about adding it.")

    logging.info("***** Finished writing dataset to CSV file *****")
    flash("***** Finished writing dataset to CSV file *****")
    logging.info("Time to save file is {:.2f} minutes...".format((time.time()-s)/60))
    flash("Time to save file is {:.2f} minutes...".format((time.time()-s)/60))
    logging.info("***** Collecting stats for columns in dataset *****")
    flash("***** Collecting stats for columns in dataset *****")
    ### Formatting depends on the binding
    if (bind.lower() == 'row') and not l2w:
        stats_dd = statsp.make_stats_dict_from_file(dd)
    else:
        ndd = statsp.read_csv(filename)
        stats_dd = statsp.make_stats_dict_from_file(ndd)
        #stats_dd = statsp.make_stats_dict_in_pipeline(dd)
    # Save stats file
    statsp.dict_to_csv(stats_dd, "Outputs{0}stats_file.csv".format(os.sep))
    logging.info("***** Saved stats to dictionary *****")
    flash("***** Saved stats to dictionary *****")


    #flash("***** Getting Data Dictionary for elements in file *****")
    #if src == 'FITBIR':

        # Split the columns on the period to get the actual variable name
    #    sfitbir.main(og_cols) #[c.split('.')[-1] for c in og_cols])

    #else:
    #    snda.run_scraping(files)
    #flash("***** Retrieved Data Dictionary *****")
    return #df

################            Running Pipeline Section             ###############
#start = time.time()

#folder_path = input("Please enter the path to the files you'd like to merge: ")
#output_name = input("Please enter the path and name of the merged file: ")

#if folder_path.startswith('\"'):
#    folder_path = folder_path.strip('\"')

#elif folder_path.startswith("\'"):
#    folder_path = folder_path.strip("\'")

#else:
#    folder_path = folder_path

#if output_name.startswith('\"'):
#    output_name = output_name.strip('\"')

#elif output_name.startswith("\'"):
#    folder_path = output_name.strip("\'")

#else:
#    output_name = output_name


#while True:
#    source = input("Are the files from NDA or FITBIR? ")
#    if source.strip().upper() == "NDA":
#        pattern = '*[0-9].txt'
#        break
#    elif source.strip().upper() == "FITBIR":
#        pattern = '*.csv'
#        break
#    else:
#        print("You must enter either NDA or FITBIR.")

#while True:
#    n = input("Please enter the number of columns you'd like to merge the files on: ")
#    n = int(n)
#    if n == 1:
#        id_column = input("Please enter the name of the column you'd like to merge on: ")
#        break
#    elif n == 2:
#        id_column = input("Please enter the name of the first column you'd like to merge on: ")
#        date_column = input("Please enter the name of the second column you'd like to merge on: ")
#        break
#    elif n == 0:
#        print("You must enter at least one column to merge on. If you'd like to concatenate or stack the files, enter 1 and choose any column.")
#    else:
#        print("Unfortunately, support for merging on more than 2 columns is not available at this time.")

#if folder_path.endswith('/'):
#    folder_path = folder_path
#else:
#    folder_path = folder_path + '/'

#files = glob.glob(folder_path+pattern)#glob.glob('/Users/kirsh012/Box/NDA Datasets/PTSD Checklist Queried Data/*[0-9].txt')#['t3.txt', 't6.txt'] #['/Users/kirsh012/Box/NDA Datasets/ABCD11all/abcd_ant01.txt',
        # '/Users/kirsh012/Box/NDA Datasets/ABCD11all/abcd_asrs01.txt']

#if n == 2:
#    main(files, output_name, source, id_column, date_col = date_column)#, sep = separator) #'test_merge_PCQD_no_date_col.csv', 'subjectkey', sep = '\t')
#elif n == 1:
#    main(files, output_name, source, id_column)#, sep = separator)
#else:
#    print("The number of columns you want to merge on is not supported at this time. Please use only 1 or 2 columns.")

#end = time.time()
#print("Time to merge all and save to csv: ", (end-start)/60)
