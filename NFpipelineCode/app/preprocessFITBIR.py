#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

Description: This module processes FITBIR datasets according to the patterns observed in the data.
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
import logging

class FITBIRdataset:

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
        parsed = ast.parse(formula, mode='eval')
        fixed = ast.fix_missing_locations(parsed)
        compiled = compile(fixed, '<string>', 'eval')
        # the formula has 'x' that needs to be defined
        return lambda x: eval(compiled)

    def _convert(self, data_element, converter):

        cond1, cond2, operator, formula = converter[data_element].values()
        logging.info(data_element)
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
                logging.info("Two conditions to modify...")
                # Check both conditions
                col1, val1 = [v.strip() for v in cond1.split('=')]
                col2, val2 = [v.strip() for v in cond2.split('=')]

                mask1 = list(map(lambda x: x == val1, self.dataset[col1]))
                mask2 = list(map(lambda x: x == val2, self.dataset[col2]))

                new_vals = list(self._two_comparison(mask1, mask2, self.dataset[data_element]))
                # If there is a formula apply that
                if formula != '':
                    logging.info("Apply formula after two conditions...")
                    #fn = lambda x: eval(formula)
                    values = list(map(float, [v if v != '' else 'nan' for v in new_vals]))
                    self.dataset[data_element] = list(map(str, list(map(self._eval_formula(formula), list(map(float, values)))))) # convert back to strings
                else:
                    logging.info("No formula after two conditions...")
                    self.dataset[data_element] = new_vals

            elif operator == 'sum':
                logging.info("Sum of data elements...")
                # Get list of columns to add together
                add_cols = cond1.split(',')
                add_vals = list(map(self.dataset.get, add_cols))
                matrix = np.array(add_vals, dtype = float)
                final_sums = matrix.sum(axis = 1)
                self.dataset[data_element] = list(map(str, final_sums)) # convert back to string after operations

            elif (operator == '') or (operator is None):

                # Only one condition
                if (cond1 != '') and (cond1 is not None):
                    logging.info("Only one condition to modify...")
                    # Split Condition 1
                    col1, val1 = [v.strip() for v in cond1.split('=')]
                    mask = list(map(lambda x: x == val1, self.dataset[col1]))
                    # Apply formula where the condition is met
                    if formula != '':
                        logging.info("Apply formula after one condition...")
                        #fn = lambda x: eval(formula)
                        # Apply the formula to rows where the condition is met
                        values = []
                        for idx, v in enumerate(self.dataset[data_element]):
                            if mask[idx]:
                                # Check if the value is '' or not
                                if v == '':
                                    values.append('nan')
                                else:
                                    values.append(v)
                            else:
                                values.append('nan')
                        values = list(map(float, values))
                        #values = list(map(float, [v if v != '' else 'nan' for v in self.dataset[data_element]]))
                        self.dataset[data_element] = list(map(str, list(map(self._eval_formula(formula), values)))) # convert back to string
                    else:
                        logging.info("No formula after one condition...")
                        new_vals = []
                        for idx, m in enumerate(mask):
                            if m:
                                new_vals.append(self.dataset[data_element][idx])
                            else:
                                new_vals.append('')
                        #new_vals = list(map(lambda x: self.dataset[data_element][idx] if m else '' for idx, m in enumerate(mask)))
                        self.dataset[data_element] = new_vals

                else:

                    if (formula == '') or (formula is None):
                        logging.info("Do nothing to scale...")
                        self.dataset[data_element] = self.dataset[data_element]
                    else:
                        #fn = lambda x: eval(formula)
                        logging.info("Apply formula only...")
                        values = list(map(float, [v if v != '' else 'nan' for v in self.dataset[data_element]]))
                        self.dataset[data_element] = list(map(str, list(map(self._eval_formula(formula), values)))) # convert back to string



            else:
                #print(data_element)
                #print("Operator is below: ")
                #print(operator)
                #print(type(operator))
                raise ValueError(f"Invalid operator for element: {data_element}. Please check and correct.")

        return self

    def read_csv(self, file):
        #''' Reads the file that you want to process '''

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


    def split_cols(self, cols, all_cols, num_suffixes):
        '''
        Parameters
        -----------
        cols: a list - the columns to split
        all_cols: a boolean - decides whether to split all the columns
        num_suffixes: an int - number of last parts of the variable name to keep

        Returns
        -----------
        self: updated dictionary
        '''

        use_cols = [key for key in self.dataset.keys() \
                    for col in cols if key.endswith(col)]


        if all_cols:
            mapper = {old_col: '.'.join(old_col.split('.')[-int(num_suffixes):])
                                for old_col in self.dataset.keys()}
        else:
            mapper = {old_col: '.'.join(old_col.split('.')[-int(num_suffixes):])
                                for old_col in use_cols}


        for old_col, new_col in mapper.items():
                self.dataset[new_col] = self.dataset[old_col]
                self.dataset.pop(old_col)
        #new_dataset = {new_col: self.dataset[old_col] for old_col, new_col in mapper.items()}

        #self.dataset = new_dataset

        return self

    def remove_cols(self, cols):

        # Remove the columns
        for col in cols:
            # Check the column if blank
            if col != '':
                # Check if column is in the dataset
                if col in self.dataset.keys():
                    self.dataset.pop(col)

        return self

    #def collect_metadata(self):

    #    metadata = {}
    #    for col in self.dataset.keys():
    #        metadata[col] = self.dataset[col][0]
    #        self.dataset[col] = self.dataset[col][1:]

    #    return metadata

    def remove_empty_cols(self):

        dd = {}
        for col, values in self.dataset.items():
            if not all([v == '' for v in values]):
                dd[col] = values

        self.dataset = dd.copy()

        return self

    def change_cols_to_nda(self, mapper):
        '''
        Description: Change the column names to their NDA counterparts
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

    def convert_scaling_to_nda(self, converter):

        # get
        # Check the operator first
        for data_element in self.dataset.keys():
            # Only scale the matched items
            if data_element in converter.keys():
                # Convert the values in the dataset
                self._convert(data_element, converter)

        return self

    def handle_missing_data(self, col, val):

        if isinstance(val, float):
            if np.isnan(val):
                new_col = f"{col}_{val}_indic"
                self.dataset[new_col] = np.where(np.isnan(np.array(self.dataset[col])), '1', '0')


        elif (val.lower() == 'nan') or (val.lower() == 'na'):
            val = ''
            new_col = f"{col}_{val}_indic"
            self.dataset[new_col] = np.where(np.array(self.dataset[col]) == val, '1', '0')

        else:
            new_col = f"{col}_{val}_indic"
            self.dataset[new_col] = np.where(np.array(self.dataset[col]) == val, '1', '0')


        return self

    def find_bad_columns(self, fill_cols):

        df = pd.DataFrame(self.dataset).replace({'': np.nan})

        for fc in fill_cols:
            if fc in df.columns:
                df[fc] = df[fc].fillna(method='ffill')



        use_cols = [dcol for f in fill_cols for dcol in df.columns \
                    if dcol.endswith(f)]
        cols = []
        for _, group in df.groupby(use_cols):
            if len(group) > 1:
                for col in group.columns:

                    if (np.sum(group[col].notnull()) > 1) and (col not in fill_cols):

                        if col not in cols:
                            cols.append(col)

        return cols, use_cols

    def fix_bad_columns(self, make_list, bad_cols, use_cols, path):

        '''
        Parameters
        -----------
        make_list: a boolean - if True, remove the bad columns from the dateset
                               and save in a separate file
        group_cols: a list - columns to group by

        Returns
        -----------
        self
        '''

        df = pd.DataFrame(self.dataset).replace({'': np.nan})
        guid_col = df.filter(regex = '[gGuUiIdD]').columns[0]

        if df[guid_col].isnull().any():

            #bad_cols, use_cols = self.dataset.find_bad_columns(group_cols)

            #print(use_cols)

            if make_list:
                df[[guid_col] + bad_cols].to_csv(path + '{0}Outputs{0}'.format(os.sep) + "list_columns.csv", index = False)

                df.drop(bad_cols, axis = 1, inplace = True)

            else:
                df[bad_cols] = df[bad_cols].astype(str)

                ndf = df[[guid_col] + bad_cols].fillna(method='ffill').groupby(guid_col).transform(lambda x: ';'.join(x))

                df[bad_cols] = ndf[bad_cols]

                df.drop_duplicates(inplace = True)


            df.dropna(how = 'all', axis = 0, inplace = True)
            df.dropna(axis = 0, subset = [guid_col], inplace = True)
            ddict = df.to_dict()

            self.dataset = {col: [val for val in ddict[col].values()] for col in ddict}


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
                #else:
                writer.writerow(row)
                rnum += 1

        return
