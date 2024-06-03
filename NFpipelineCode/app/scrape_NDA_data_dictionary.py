#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 11:16:18 2019

@author: kirsh012

# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

Description: This module scrapes the information for the matching data elements found in each file
in the application's "Inputs" folder.
"""

# Load potentially useful libraries
import requests
from bs4 import BeautifulSoup
import re
from lxml import html
import numpy as np
import pandas as pd
import glob
from flask import flash
from sys import argv
from pathlib import Path
import os

# We do this to ignore a specific Pandas warning
import warnings
warnings.filterwarnings("ignore")


import time


#data_path = argv[1]

#if data_path[-1] == '/':
#    files = glob.glob(data_path + '*[0-9].txt')
#    data_path = data_path[:-1]
#else:
#    files = glob.glob(data_path + '/*[0-9].txt')

#df_name = data_path.split('/')[-1]

def get_shortnames(filenames):
    '''
    Returns the list of shortnames for the data dictionaries. Read in a list of .txt files, removes the ".txt",
    and returns the shortnames.

    Parameters
    -----------
    filenames: a list - contains the names of the datasets

    Returns
    -----------
    shortnames: a list - the shortnames of the datasets
    '''
    # Splits the filename on the '.', then removes the 'txt'
    files = [name.split(os.sep)[-1] for name in filenames]
    shortnames = [name.split('.')[0] for name in files]
    #shortnames = [Path(file).stem for file in filenames]
    return shortnames

# Clean the file names to something the api can read
#shortnames = sorted(get_shortnames(files))
# Define api
#api = 'https://ndar.nih.gov/api/datadictionary/v2/datastructure/{}'

def get_structure(shortname, url):
    '''
    Returns the structure of the data dictionary for a specific dataset.

    Parameters
    -----------
    shortname: a str - the name of the dataset
    url: a str - name of the NDAR API

    Returns
    -----------
    structure: a dict - dictionary of the data dictionary for the dataset
    '''

    # Retrieves a json dictionary from the website
    structure = requests.get(url.format(shortname)).json()
    # Convert json dictionary to python dictionary
    #structure =  json.loads(dictionary.text)

    return structure

def get_no_submission_structure(shortname):
    ts = requests.get('https://ndar.nih.gov/data_structure.html?short_name={}'.format(shortname))
    soup = BeautifulSoup(ts.content, 'lxml')
    tables = soup.find_all('table')

    # Find study title
    info = soup.find(id = "data_structure_details")
    info_list = info.find_all('div')[0]
    pvals = info_list.find_all('p')
    title = pvals[0].contents[0].strip()

    # get data elements
    tb = tables[6].tbody
    tr = tb.find_all('tr')
    data_list = []

    for row in tr:
        tdx = [val for val in row.find_all('td')]
        data = {}
        temp = []
        for row in tdx:
            if row.contents:
                if str(row.contents[0]).strip().startswith('<'):
                    temp.append(np.nan)
                else:
                    temp.append(row.contents[0].strip())
            else:
                temp.append(np.nan)
        #data.append(temp)

        data['id'] = np.nan#temp[8]
        data['required'] = temp[4]
        data['condition'] = np.nan#temp[8]
        data['aliases'] = temp[8]
        data['filterElement'] = temp[0]
        data['position'] = np.nan#temp[8]
        data['dataElementID'] = np.nan#temp[8]
        data['name'] = temp[1]
        data['type'] = temp[2]
        data['size'] = temp[3]
        data['description'] = temp[5]
        data['valueRange'] = temp[6]
        data['notes'] = temp[7]
        data['translations'] = np.nan#temp[8]


        data_list.append(data)

    dd = {}
    dd['title'] = title
    dd['shortName'] = shortname
    dd['dataElements'] = data_list

    return dd

def get_all_data_dicts(shortnames, url):
    '''
    Collects all data dictionaries into a single dictionary where the key is the name of the dataset
    and the value is its data dictionary

    Parameters
    -----------
    shortnames: a list - list of all datasets

    Returns
    -----------
    all_data_dictionaries: a dict - dictionary of all data dictionaries
    '''

    # Initialize the dictionary
    all_data_dictionaries = {}
    #no_submission = []
    #version_updates = []
    # Loop over each dataset name
    for name in shortnames:
        print(name)
        # Retrive the data dictionary for the dataset
        structure1 = get_structure(name, url)

        if 'error' in structure1.keys():
            structure2 = requests.get('https://ndar.nih.gov/api/datadictionary/v2/datastructure/{}/changes'
                 .format(name),
                  headers={'Accept':'application/json'}).json()
            #strucutre = structure2
            if 'error' in structure2.keys():
             #   structure = structure1
                structure = get_no_submission_structure(name)
            else:
                structure = structure2
            #pass
        else:
            structure = structure1
        # Add the data dictionary to the new dictionary
        all_data_dictionaries[name] = structure

    return all_data_dictionaries#, no_submission, version_updates

# Collect all data dictionaries in a single dictionary
#all_dd = get_all_data_dicts(shortnames)

def get_all_rows_cols(dd):
    '''
    Collects all the data and stores it into a numpy array that will be used to create a dataframe.

    Parameters
    -----------
    dd: a dict - dictionary that contains all the data dictionaries

    Returns
    -----------
    data: a numpy.ndarray - all the values to be filled in the dataframe
    idx_list: a numpy.array - the corresponding index for each element
    '''
    # Initialize arrays
    data = []
    idx_list = []
    columns = []
    titles = []
    study_des = []

    # Loop over all entries in the dictionary
    for key, val in dd.items():
        # Select all values in the 'dataElements' key
        element = val['dataElements']
        # Get title of the assessment
        title = val['title']
        for i in range(len(element)):
            # Add all values from the element as a row in the upcoming dataframe
            data.append(list(element[i].values()))
            titles.append(title)
            # Add key so that the index for the row is this key
            idx_list.append(key)
        if 'description' in val.keys():
            des = val['description']
            study_des.append(des)
        else:
            study_des.append(np.nan)
        # Columns should be the same throughout, so we don't need them for each row of data
        columns.append(element[i].keys())

    # Change to numpy arrays
    data = np.array(data)
    idx_list = np.array(idx_list)

    return (data, idx_list, columns, titles, study_des)

# Get all the data from the dictionaries
#data = get_all_rows_cols(all_dd)

# Separate the column and indices from the data
#columns = np.array(list(data[2][0]))
#indices = data[1]
#all_data = data[0]
#titles = data[3]
#study_des = data[4]

def get_dataframe(data, indices, cols):
    '''
    Creates a dataframe where the dataset names are the indices, the columns are the elements of the data
    dictionary, and the rows contain the data dictionary information

    Parameters
    -----------
    data: a numpy.ndarray - the information from each data dictionary
    indices: a numpy.array - the name of the dataset each row came from
    cols: a list - the list of columns for the dataframe

    Returns
    -----------
    df: a pandas.DataFrame - dataframe of all the elements in the data dictionaries
    '''
    # Make dataframe
    df = pd.DataFrame(data, index = indices, columns = cols)

    return df

# Create dataframe of all data dictionaries
#df = get_dataframe(all_data, indices, columns)

# Add title column
#df['Title'] = titles
# Add Study Description column
#if not np.all(np.isnan(study_des)):#
#    df['StudyDescription'] = study_des
#else:
#    df['StudyDescription'] = np.nan

# Create raw data dictionary for all
#drop_cols = ['id', 'position']
#df = df.drop(drop_cols, axis = 1)
#df.reset_index(inplace = True)
#df.rename(columns = {'required': 'Required', 'condition': 'Condition', 'aliases': 'Aliases', \
#                    'name': 'ElementName', 'type': 'DataType', 'size': 'Size', 'description': 'ElementDescription', \
#                    'valueRange': 'ValueRange', 'notes': 'Notes', 'translations': 'Translations', \
#                    'index': 'FileName'}, inplace = True)

#col_order = ['ElementName', 'ElementDescription', 'DataType', 'ValueRange', 'Size', 'Required',
#             'dataElementId', 'Aliases', 'FileName', 'Condition', 'filterElement', 'Notes', 'Translations',
#            'Title', 'StudyDescription']
#df = df.loc[:, col_order]
#df.to_csv(data_path + '/' + df_name + '_Data_Dictionaries.csv', sep = ',', index = False)#, index_label = 'FileName')

def run_scraping(files):
    start = time.time()
    # Define api
    api = 'https://ndar.nih.gov/api/datadictionary/v2/datastructure/{}'
    # Clean the file names to something the api can read
    shortnames = sorted(get_shortnames(files))

    print(files)

    # Collect all data dictionaries in a single dictionary
    #all_dd, no_sub, ver = get_all_data_dicts(shortnames)
    all_dd = get_all_data_dicts(shortnames, api)

    # Get all the data from the dictionaries
    data = get_all_rows_cols(all_dd)

    # Separate the column and indices from the data
    print(data)
    columns = np.array(list(data[2][0]))
    indices = data[1]
    all_data = data[0]
    titles = data[3]
    study_des = data[4]

    # Create dataframe of all data dictionaries
    df = get_dataframe(all_data, indices, columns)

    # Add title column
    df['Title'] = titles
    # Add Study Description column
    if not np.all(np.isnan(study_des)):
        df['StudyDescription'] = study_des
    else:
        df['StudyDescription'] = np.nan

    # Create raw data dictionary for all
    drop_cols = ['id', 'position']
    df = df.drop(drop_cols, axis = 1)
    df.reset_index(inplace = True)
    df.rename(columns = {'required': 'Required', 'condition': 'Condition', 'aliases': 'Aliases', \
                        'name': 'ElementName', 'type': 'DataType', 'size': 'Size', 'description': 'ElementDescription', \
                        'valueRange': 'ValueRange', 'notes': 'Notes', 'translations': 'Translations', \
                        'index': 'FileName'}, inplace = True)

    col_order = ['ElementName', 'ElementDescription', 'DataType', 'ValueRange', 'Size', 'Required',
                 'dataElementId', 'Aliases', 'FileName', 'Condition', 'filterElement', 'Notes', 'Translations',
                'Title', 'StudyDescription']
    df = df.loc[:, col_order]
    df.to_csv('Outputs{}NDA_Data_Dictionaries.csv'.format(os.sep), sep = ',', index = False)#, index_label = 'FileName')
    end = time.time()
    flash("Time to make data dictionary is {} minutes.".format((end-start)/60))
    return
