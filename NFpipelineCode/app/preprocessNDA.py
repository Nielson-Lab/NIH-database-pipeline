#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

Description: This module processes NDA datasets according to the patterns observed in the data.
It includes its own method for writing the processed dataset to a CSV file.

"""
import pandas as pd
import numpy as np
import csv
import sys
import os
import re
import glob
from collections import defaultdict
from dateutil.parser import parse
from datetime import datetime
import ast
import pprint
import logging

class NDAdataset:

    def __init__(self):

        self.dataset = defaultdict(list)

    def _two_comparison(self, mask1, mask2, vals):

        for idx, (m1, m2) in enumerate(zip(mask1, mask2)):
            if m1 and m2:
                yield vals[idx]
            else:
                yield ''

    def _eval_formula(self, formula):
        ''' Securely evaluate the formula presented from the table
        Based on the suggested modification to `ast.literal_eval` at https://stackoverflow.com/a/51713577/10852841
        '''

        if (formula != '') and (formula is not None):
            parsed = ast.parse(formula, mode='eval')
            fixed = ast.fix_missing_locations(parsed)
            compiled = compile(fixed, '<string>', 'eval')
            # the formula has 'x' that needs to be defined
            return lambda x: eval(compiled)
        else: # formula is '' or None
            return lambda x: x

    def _convert(self, data_element, converter):

        felement, cond1, cond2, operator, formula = converter[data_element].values()
        logging.info(data_element)

        # Turn formula into a function
        fn = self._eval_formula(formula)

        # First check if the data-element is a time variable
        if data_element in ['AdvrsEvntStartDateTime', 'AdverseEvntEndDateTime']: #['aestdd', 'aeendd']:
            logging.info("Fixing data...")
            dates = self.dataset[data_element]
            # Parse the dates into components and datetime object type
            parsed_dates = [parse(date) if date != '' else '' for date in dates]
            # Convert to MM/DD/YYYY
            new_dates = [dt.strftime('%m/%d/%Y') if dt != '' else '' for dt in parsed_dates]
            # Save new dates
            self.dataset[data_element] = new_dates

        # Otherwise, based on the operator
        else:

            if operator == 'dict':
                logging.info("Dictionary mapping...")
                # Split on the '='
                func_split = re.split(',|;', cond1)

                dd = dict()
                for pair in func_split:
                    k = pair.split('=')
                    dd[k[0].strip()] = k[1].strip()#.replace('"', '')

                # Map the values
                new_values = list(map(lambda x: dd[x] if x in dd.keys() else x, self.dataset[data_element]))

                self.dataset[data_element] = new_values

            elif operator == '==':
                logging.info("Exception modeling == ...")
                # Check where this column equals the value
                #print(cond1)
                #col1, val1 = [v.strip() for v in cond1.split('=')]

                # Create values based on that condition (value except if value == 30)
                self.dataset[data_element] = list(map(lambda x: x if x != cond1 else '', self.dataset[data_element]))

            elif operator == '&':
                """
                    NDA does the condition conversion differently.
                    The two condition columns do not exist and are created and
                    added pending the values of the columns.

                    Because these kinds of variables have multiple NDA variables
                    mapping to them, you'll need to keep track of the indices
                    of the values to change.
                """
                logging.info("Two conditions to modify...")
                # Check both conditions
                col1, val1 = [v.strip() for v in cond1.split('=')]
                col2, val2 = [v.strip() for v in cond2.split('=')]

                # Applies values from a single data_element
                # If the new column hasn't been created yet, create it empty
                # but only create it if there are values in the data_element
                # (don't want to create an empty column)
                if np.all(self.dataset[data_element] != ''):
                    if col1 not in self.dataset.keys():
                        self.dataset[col1] = ['']*len(self.dataset[data_element])
                    if col2 not in self.dataset.keys():
                        self.dataset[col2] = ['']*len(self.dataset[data_element])
                    if felement not in self.dataset.keys():
                        self.dataset[felement] = ['']*len(self.dataset[data_element])

                    # Loop over values and add to the new column
                    # Since multiple variables will map to the newly named column
                    # of this data_element, I'll need to save that somehow to modify
                    # those values too...
                    for idx, value in enumerate(self.dataset[data_element]):

                        if value != '': #The value exists
                            # Save value to the mapped FITBIR column (applying formula as needed!)
                            # Have to apply formula to this value otherwise the formula will be
                            # applied more than once to each value
                            self.dataset[felement][idx] = str(fn(float(value))) # convert back to string
                            # Save the proper value to the first column
                            self.dataset[col1][idx] = val1
                            # Save the proper value to the second column
                            self.dataset[col2][idx] = val2
                        else:
                            # The value does not exist
                            self.dataset[felement][idx] = value
                            self.dataset[col1][idx] = ''
                            self.dataset[col2][idx] = ''
                else:
                    logging.info(f'{data_element} is empty. No condition applied...')


                    # No longer applies
                    #mask1 = list(map(lambda x: x == val1, self.dataset[col1]))
                    #mask2 = list(map(lambda x: x == val2, self.dataset[col2]))
                    #new_vals = list(self._two_comparison(mask1, mask2, self.dataset[data_element]))

                    ## If there is a formula apply that to the
                    #if formula != '':
                    #    print("Apply formula after two conditions...")
                    #    #fn = lambda x: eval(formula)
                    #    values = list(map(float, [v if v != '' else 'nan' for v in new_vals]))
                    #    self.dataset[data_element] = list(map(self._eval_formula(formula), list(map(float, values))))
                    #else:
                    #    print("No formula after two conditions...")
                    #    self.dataset[data_element] = new_vals

            elif operator == 'sum':
                logging.info("Sum of data elements...")
                # Get list of columns to add together
                add_cols = cond1.split(',')
                add_vals = list(map(self.dataset.get, add_cols))
                matrix = np.array(add_vals, dtype = 'object').T
                matrix[matrix == ''] = 'nan'
                matrix = matrix.astype(float)
                final_sums = np.nansum(matrix, axis = 1)
                self.dataset[felement] = list(map(str, final_sums)) # convert back to string
                # Remove original columns
                #for acol in add_cols:
                #    self.dataset.pop(acol)

            elif (operator == '') or (operator is None):

                # Only one condition
                if (cond1 != '') and (cond1 is not None):
                    logging.info("Only one condition to modify...")
                    # Split Condition 1
                    col1, val1 = [v.strip() for v in cond1.split('=')]
                    #mask = list(map(lambda x: x == val1, self.dataset[col1]))

                    # Do nothing if the entire column of values is empty
                    if np.all(self.dataset[data_element] != ''):
                        if col1 not in self.dataset.keys():
                            self.dataset[col1] = ['']*len(self.dataset[data_element])
                        if felement not in self.dataset.keys():
                            self.dataset[felement] = ['']*len(self.dataset[data_element])

                        # Loop over values and add to the new column
                        # Since multiple variables will map to the newly named column
                        # of this data_element, I'll need to save that somehow to modify
                        # those values too...
                        for idx, value in enumerate(self.dataset[data_element]):

                            if value != '': #The value exists
                                # Save value to the mapped FITBIR column (applying formula as needed!)
                                # Have to apply formula to this value otherwise the formula will be
                                # applied more than once to each value
                                self.dataset[felement][idx] = str(fn(float(value))) # convert back to strings
                                # Save the proper value to the first column
                                self.dataset[col1][idx] = val1
                            else:
                                # The value does not exist
                                self.dataset[felement][idx] = value
                                self.dataset[col1][idx] = ''
                    else:
                        logging.info(f'{data_element} is empty. No condition applied...')


                    # Apply formula where the condition is met
                    #if formula != '':
                    #    print("Apply formula after one condition...")
                    #    #fn = lambda x: eval(formula)
                    #    values = list(map(float, [v if v != '' else 'nan' for v in self.dataset[data_element]]))
                    #    self.dataset[data_element] = list(map(self._eval_formula(formula), values))
                    #else:
                    #    print("No formula after one condition...")
                    #    new_vals = []
                    #    for idx, m in enumerate(mask):
                    #        if m:
                    #            new_vals.append(self.dataset[data_element][idx])
                    #        else:
                    #            new_vals.append('')
                    #    #new_vals = list(map(lambda x: self.dataset[data_element][idx] if m else '' for idx, m in enumerate(mask)))
                    #    self.dataset[data_element] = new_vals

                else:

                    #if (formula == '') or (formula is None):
                    #    print("Do nothing to scale...")
                    #    self.dataset[data_element] = self.dataset[data_element]
                    #else:
                    if (formula != '') and (formula is not None):
                        #fn = lambda x: eval(formula)
                        logging.info("Apply formula only...")
                        values = list(map(float, [v if v != '' else 'nan' for v in self.dataset[data_element]]))
                        self.dataset[data_element] = list(map(str, list(map(fn, values)))) # convert back to strings
                    else:
                        logging.info("Do nothing to scale...")



            else:

                raise ValueError(f"Invalid operator for element: {data_element}. Please check and correct.")

        return self

    def read_csv(self, file):
        # Reads the file that you want to process

        with open(file, 'r') as fin:

            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(fin.readline())
            fin.seek(0)
            delim = str(dialect.delimiter)
            reader = csv.DictReader(fin, delimiter = delim)

            #data = defaultdict(list)
            for row in reader:

                for key, value in row.items():
                    # Keys are the columns in the data

                    self.dataset[key].append(value)


        return self


    def remove_cols(self, cols):

        # Automatically remove collection_title and promoted_subjectkey
        if 'collection_title' not in cols:
            cols.append('collection_title')
        if 'promoted_subjectkey' not in cols:
            cols.append('promoted_subjectkey')

        # Remove the columns
        for col in cols:
            # Check if the input is blank
            if col != '':
                # Check if column is in the dataset
                if col in self.dataset.keys():
                    self.dataset.pop(col)

        return self

    def collect_metadata(self):

        metadata = {}
        for col in self.dataset.keys():
            metadata[col] = self.dataset[col][0]
            self.dataset[col] = self.dataset[col][1:]

        return metadata

    def remove_empty_cols(self):

        dd = {}
        for col, values in self.dataset.items():
            if not all([v == '' for v in values]):
                dd[col] = values

        self.dataset = dd.copy()

        return self

    def change_cols_to_fitbir(self, mapper):
        '''
        Description: Change the column names to their FITBIR counterparts
        '''

        dd = dict()
        for old_key in list(self.dataset.keys()):
            # Alert user to dataset issue if data elements are missing
            if old_key == '':
                raise KeyError("You are missing data element names in your dataset.\nPlease correct and try again.")

            if old_key in mapper.keys():
                new_key = mapper[old_key]
                if new_key != '':
                    dd[new_key] = self.dataset[old_key.strip()]
                else: # If there is no match, keep the old key
                    dd[old_key] = self.dataset[old_key.strip()]
            else:
                dd[old_key] = self.dataset[old_key.strip()]

        self.dataset = dd.copy()

        return self

    def convert_scaling_to_fitbir(self, converter):

        # Check the operator first
        for data_element in list(self.dataset): # uses list because the size of the dictionary changes in the loop
            # Only scale the matched items
            if data_element in converter.keys():
                # Convert the values in the dataset
                self._convert(data_element, converter)

        return self

    def handle_missing_data(self, col, val):

        #if (val.lower() == 'nan'):
        #    val = np.nan
        #if (val.lower() == 'na'):# or (val.lower() == 'nan'):
        #    val = ''

        new_col = f"{col}_{str(val)}_indic"
        self.dataset[new_col] = np.where(np.array(self.dataset[col]) == val, '1', '0')

        return self



    def to_csv(self, savefile):

        with open(savefile, 'w') as fout:

            writer = csv.writer(fout, lineterminator = '\n')#, fieldnames = list(self.dataset.keys()))

            #writer.writeheader()

            super_data = [self.dataset[col] for col in self.dataset.keys()]

            row_data = list(zip(*super_data))

            rnum = 0
            for row in row_data:

                # Write column names
                if rnum == 0:
                    writer.writerow(list(self.dataset.keys()))

                writer.writerow(row)
                rnum += 1

        return
