#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 14:31:45 2019

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
import json
import bs4
from bs4 import BeautifulSoup
import urllib3
import re
import numpy as np
import pandas as pd
import glob
import re
import csv
import ast
from functools import reduce
import os
from pathlib import Path
from flask import flash
import logging

# We do this to ignore a specific Pandas warning
import warnings
warnings.filterwarnings("ignore")


def get_urls(names):
    base_url = "https://fitbir.nih.gov/dictionary/publicData/dataElementAction!view.action?dataElementName={}&publicArea=true&style.key=fitbir-style"
    return [base_url.format(name) for name in names]

def make_soup(varname, url= "https://fitbir.nih.gov/dictionary/publicData/dataElementAction!view.action?dataElementName={}&publicArea=true&style.key=fitbir-style"):
    logging.info(f"Issue data element is {varname}")
    logging.info(f"Issue URL is {url}")
    page = requests.get(url.format(varname))
    html = page.content
    soup = BeautifulSoup(html, 'lxml')
    return soup

def get_labels(tag_id):
    labels = []
    for div_tag in tag_id.find_all('div'):
        if div_tag.label is not None:
            labels.append(div_tag.label.text)
        elif div_tag.find('div', {'class': 'label'}) is not None:
            labels.append(div_tag.find('div', {'class': 'label'}).text)

    return labels

def get_texts(tag_id):
    pattern = re.compile(r'^readonly')
    texts = []
    for t in tag_id.find_all('div', attrs = {'class': pattern}):
        texts.append(t.text.lstrip().rstrip())

    return texts

def combine_labels_texts(labels, texts):
    dd = {k: v for k, v in zip(labels, texts)}
    return dd

def write_to_csv(savename, names, method):

    with open(savename, method) as fout:
        fieldnames = ['Variable Name', 'Title', 'Definition', 'Short Description',
                      'Element Type', 'Data Type', 'Historical Notes',
                      'Guidelines/Instructions', 'value_range', 'value_description',
                      'Input Restrictions', 'Minimum Value', 'Unit of Measure', 'Maximum Value',
                      'Population', 'Version', 'Notes',
                      'References', 'Creation Date', 'Preferred Question Text',
                      'Pre-Defined Values']

        writer = csv.DictWriter(fout, fieldnames = fieldnames, lineterminator = '\n')
        writer.writeheader()

        urls = get_urls(names)

        for name, url in zip(names, urls):

            flash(f"Scraping data for variable {name}")
            logging.info(f"Scraping data for {name}")

            soup = make_soup(name, url)

            tag_general = soup.find(id='general')
            # Some data elements are not in FITBR (ex: Associated GUID)
            if tag_general is None:
                logging.info(f"{name} does not have a URL to scrape from.")
                continue
            #print(tag_general)
            tag_basic = soup.find(id='basic')
            #print(tag_basic)
            labels = get_labels(tag_general)
            labels = [l.strip(':') for l in labels]
            basic_labels = get_labels(tag_basic)
            basic_labels = [bl.strip(':') for bl in basic_labels]

            texts = get_texts(tag_general)
            basic_texts = get_texts(tag_basic)

            general_dict = combine_labels_texts(labels, texts)
            basic_dict = combine_labels_texts(basic_labels, basic_texts)

            dd = reduce(lambda x, y: {**x, **y}, [general_dict, basic_dict])

            script_tag = soup.find_all(type = 'text/javascript')

            for tag in script_tag:
                #print(tag)
                if 'dataElementPvTable' in tag.get_text():
                    script = tag

                    script_txt = script.contents[0].strip()
                #pattern = re.compile(r'(\{[^}]+\})')

            #match = re.search(pattern, script_txt)

            #json_txt = json.loads(match.group(0))

                    test = re.sub(r'\r|\t|\n|\s', '', script_txt)

                    try:
                        usestring = test[test.find(',data:')+1:test.find(']}')]

                        valuerange = ast.literal_eval(usestring[5:-1] + ']')

                        vr = {'value_range': [dd.get('valueRange') for dd in valuerange],
                               'value_description': [dd.get('description') for dd in valuerange]}

                    except SyntaxError:

                        vr = {'value_range': '',
                                'value_description': ''}
                    dd.update(vr)

                    ndd = {k: dd.get(k, '') for k in dd if k in fieldnames}
                    writer.writerow(ndd)

def main(given_names):

    # Remove duplicate names
    names = []
    for n in given_names:
        if n not in names:
            names.append(n)

    # Check the file already exists
    savename = 'Outputs{}fitbir_data_dictionary.csv'.format(os.sep)
    pathname = Path(savename)
    #print(names[-5:])

    if not pathname.exists():
        logging.info("File DOES NOT exist yet.")
        write_to_csv(savename, names, 'w')

    else:
        ### File exists and you have to add more rows
        logging.info("File ALREADY exists.")
        # Read the current CSV and collect which names exist already
        used_names = []
        with open(savename, 'r') as fin:

            reader = csv.DictReader(fin)

            for line in reader:
                used_names.append(line['Variable Name'])

        new_names = list(set(names) - set(used_names))
        #print(new_names[:5])
        #print(new_names[-5:])
        # Use the new names to add to the CSV file
        write_to_csv(savename, new_names, 'a')
