#!/usr/bin/env python3

"""
# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

Description: This module scrapes all the data dictionaries in NDA and saves thems to a CSV file.

"""
import requests
import json
import bs4
from bs4 import BeautifulSoup
import re
from lxml import html
import numpy as np
import pandas as pd
import glob
import pickle
from getpass import getpass
import os

# We do this to ignore a specific Pandas warning
import warnings
warnings.filterwarnings("ignore")

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
    sdictionary = requests.get(url.format(shortname), headers={'Accept':'application/json'})#.json()
    # Convert json dictionary to python dictionary
    structure =  json.loads(sdictionary.text)

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
        data['aliases'] = temp[-1]
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
        # Retrive the data dictionary for the dataset
        structure1 = get_structure(name, url)

        if 'error' in structure1.keys():
            n = name.split("0")
            nn = n[0] + "02"
            structure2 = get_structure(nn, url)
            #all_data_dictionaries[name] = structure
            #structure2 = requests.get('https://ndar.nih.gov/api/datadictionary/v2/datastructure/{}/changes'
            #     .format(name),
            #      headers={'Accept':'application/json'}).json()

            if 'error' in structure2.keys():

                structure = get_no_submission_structure(name)
            else:
                structure = structure2

        else:
            structure = structure1
        # Add the data dictionary to the new dictionary
        all_data_dictionaries[name] = structure

    return all_data_dictionaries#, no_submission, version_updates

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
        #print(key)
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
        if len(element) != 0:
            columns.append(element[i].keys())

    # Change to numpy arrays
    data = np.array(data)
    idx_list = np.array(idx_list)

    return (data, idx_list, columns, titles, study_des)

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



def main():

    api = 'https://ndar.nih.gov/api/datadictionary/v2/datastructure/'
    url = 'https://ndar.nih.gov/api/datadictionary/v2/datastructure/{}'

    dd = requests.get(api)
    st =  json.loads(dd.text)

    snames = [st[i]['shortName'] for i in range(len(st))]

    # Collect all data dictionaries in a single dictionary
    all_dd = get_all_data_dicts(snames, url)

    # Get all the data from the dictionaries
    data = get_all_rows_cols(all_dd)

    # Separate the column and indices from the data
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
    df.rename(columns = {'required': 'Required', 'condition': 'Condition', 'aliases': 'Aliases',
                        'name': 'ElementName', 'type': 'DataType', 'size': 'Size', 'description': 'ElementDescription',
                        'valueRange': 'ValueRange', 'notes': 'Notes', 'translations': 'Translations'}, inplace = True)

    df.to_csv('..{}Outputs{}All_Data_Dictionaries.csv'.format(os.sep), index_label = 'FileName')

#if __name__ == '__main__':

#    main()
