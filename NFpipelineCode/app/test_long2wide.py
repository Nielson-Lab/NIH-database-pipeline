#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

Description: Unit tests for the long2wide module. This requires the use of pytest to run.

"""
import pytest
import unittest
import pandas as pd
import csv
from io import StringIO
import numpy as np
from datetime import datetime
from collections import defaultdict
import sys
# sys.path.insert(1, '../app')
import long2wide as l2w

class TestLong2Wide(unittest.TestCase):


    def test_read_csv(self):

        test_dd = l2w.read_csv('../tests/l2w_test_data.csv', 'ID', 'Date')
        self.maxDiff = None
        self.assertDictEqual(test_dd, {('AAA', '08/16/2019'): {'Col1': ['2.45'], 'Col2': ['0']},
                                       ('BBB', '08/16/2019'): {'Col1': [''], 'Col2': ['1']},
                                       ('CCC', '08/16/2019'): {'Col1': ['3.2'], 'Col2': ['1']}})


    def test_convert_to_date_float_date(self):
        test_date = l2w.convert_to_time('6', False, False)
        self.assertEqual(test_date, 6.0)


    def test_convert_to_date_mdy_slash_date(self):
        test_date = l2w.convert_to_time('03/18/1995', False, False)
        self.assertEqual(test_date, datetime(1995, 3, 18, 0, 0))


    def test_convert_to_date_mdy_dash_date(self):
        test_date = l2w.convert_to_time('03-18-1995', False, False)
        self.assertEqual(test_date, datetime(1995, 3, 18, 0, 0))


    def test_convert_to_date_ymd_slash_date(self):
        test_date = l2w.convert_to_time('1995/03/18', False, False)
        self.assertEqual(test_date, datetime(1995, 3, 18, 0, 0))


    def test_convert_to_date_ymd_dash_date(self):
        test_date = l2w.convert_to_time('1995-03-18', False, False)
        self.assertEqual(test_date, datetime(1995, 3, 18, 0, 0))


    def test_convert_to_date_string_date(self):
        test_date = l2w.convert_to_time('3 months', True, False)
        self.assertEqual(test_date, '3_months')


    # def test_convert_to_date_unknown(self):

    #     with self.assertRaises(ValueError) as context:
    #         l2w.convert_to_time('Not a date', False, False)

    #     self.assertTrue("Unknown date format. Please revise" in str(context.exception))

    def test_aggregate_data_mean(self):
        test_dd = {('AAA', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('BBB', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('AAA', '08/22/2019'): {'Col1': ['2','', '3', '1'], 'Col2':['b', 'b', '', 'a']}}

        self.maxDiff = None
        self.assertDictEqual({('AAA', '08/21/2019'): {'Col1': 7/3, 'Col2': 'a'},
                        ('BBB', '08/21/2019'): {'Col1': 7/3, 'Col2': 'a'},
                        ('AAA', '08/22/2019'): {'Col1': 2., 'Col2': 'b'}}, l2w.aggregate_data(test_dd, 'mean'))

    def test_aggregate_data_mean2(self):
        test_dd = {('AAA', '08/21/2019'): {'Col1': ['1','','','4'], 'Col2':['','', '', '']},
                    ('BBB', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('AAA', '08/22/2019'): {'Col1': ['2','', '3', '1'], 'Col2':['b', 'b', '', 'a']}}

        self.maxDiff = None
        self.assertDictEqual({('AAA', '08/21/2019'): {'Col1': 2.5, 'Col2': ''},
                        ('BBB', '08/21/2019'): {'Col1': 7/3, 'Col2': 'a'},
                        ('AAA', '08/22/2019'): {'Col1': 2., 'Col2': 'b'}}, l2w.aggregate_data(test_dd, 'mean'))

    def test_aggregate_data_median(self):
        test_dd = {('AAA', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('BBB', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('AAA', '08/22/2019'): {'Col1': ['2','', '3', '1'], 'Col2':['b', 'b', '', 'a']}}

        self.maxDiff = None
        self.assertDictEqual({('AAA', '08/21/2019'): {'Col1': 2., 'Col2': 'a'},
                        ('BBB', '08/21/2019'): {'Col1': 2., 'Col2': 'a'},
                        ('AAA', '08/22/2019'): {'Col1': 2., 'Col2': 'b'}}, l2w.aggregate_data(test_dd, 'median'))

    def test_aggregate_data_mode(self):
        test_dd = {('AAA', '08/21/2019'): {'Col1': ['1','2','','1'], 'Col2':['a','b', 'a', '']},
                    ('BBB', '08/21/2019'): {'Col1': ['1','2','','1'], 'Col2':['a','b', 'a', '']},
                    ('AAA', '08/22/2019'): {'Col1': ['2','', '3', '1'], 'Col2':['b', 'b', '', 'a']}}


        self.assertDictEqual({('AAA', '08/21/2019'): {'Col1': '1', 'Col2': 'a'},
                        ('BBB', '08/21/2019'): {'Col1': '1', 'Col2': 'a'},
                        ('AAA', '08/22/2019'): {'Col1': '', 'Col2': 'b'}}, l2w.aggregate_data(test_dd, 'mode'))

    def test_aggregate_data_first(self):
        test_dd = {('AAA', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('BBB', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('AAA', '08/22/2019'): {'Col1': ['2','', '3', '1'], 'Col2':['b', 'b', '', 'a']}}
        self.maxDiff = None
        self.assertDictEqual({('AAA', '08/21/2019'): {'Col1': '1', 'Col2': 'a'},
                        ('BBB', '08/21/2019'): {'Col1': '1', 'Col2': 'a'},
                        ('AAA', '08/22/2019'): {'Col1': '2', 'Col2': 'b'}}, l2w.aggregate_data(test_dd, 'first'))

    def test_aggregate_data_last(self):
        test_dd = {('AAA', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('BBB', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('AAA', '08/22/2019'): {'Col1': ['2','', '3', '1'], 'Col2':['b', 'b', '', 'a']}}

        self.assertDictEqual({('AAA', '08/21/2019'): {'Col1': '4', 'Col2': ''},
                        ('BBB', '08/21/2019'): {'Col1': '4', 'Col2': ''},
                        ('AAA', '08/22/2019'): {'Col1': '1', 'Col2': 'a'}}, l2w.aggregate_data(test_dd, 'last'))

    def test_aggregate_data_none(self):
        test_dd = {('AAA', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('BBB', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('AAA', '08/22/2019'): {'Col1': ['2','', '3', '1'], 'Col2':['b', 'b', '', 'a']}}

        self.assertDictEqual(test_dd, l2w.aggregate_data(test_dd, 'None'))

    def test_split_keys(self):
        test_dd = {('AAA', '08/21/2019'): {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]},
                    ('BBB', '08/21/2019'): {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]},
                    ('AAA', '08/22/2019'): {'Col1': [2,np.nan, 3, 1], 'Col2':['b', 'b', np.nan, 'a']}}

        output_dd = {'AAA': [{'08/21/2019': {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]}},
                             {'08/22/2019': {'Col1': [2,np.nan, 3, 1], 'Col2':['b', 'b', np.nan, 'a']}}],
                     'BBB': [{'08/21/2019': {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]}}]}
        self.maxDiff = None
        self.assertDictEqual(output_dd, l2w.split_keys(test_dd, False))

    def test_make_time_keys_float(self):
        test_dd = {('AAA', '0'): {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]},
                    ('BBB', '0'): {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]},
                    ('AAA', '1'): {'Col1': [2,np.nan, 3, 1], 'Col2':['b', 'b', np.nan, 'a']}}

        test_dd = l2w.split_keys(test_dd, False)
        #print(test_dd.keys())
        self.maxDiff = None
        self.assertDictEqual({'AAA': [{'Day0': {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]}},
                                      {'Day1': {'Col1': [2,np.nan, 3, 1], 'Col2':['b', 'b', np.nan, 'a']}}],
                              'BBB': [{'Day0': {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]}}]},
                              l2w.make_time_keys(test_dd, 1, 'Day', False, False))

    def test_make_time_keys_ymd(self):
        test_dd = {('AAA', '2019/08/21'): {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]},
                    ('BBB', '2019/08/21'): {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]},
                    ('AAA', '2019/08/22'): {'Col1': [2,np.nan, 3, 1], 'Col2':['b', 'b', np.nan, 'a']}}

        test_dd = l2w.split_keys(test_dd, False)

        self.maxDiff = None
        self.assertDictEqual({'AAA': [{'Day0': {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]}},
                                      {'Day1': {'Col1': [2,np.nan, 3, 1], 'Col2':['b', 'b', np.nan, 'a']}}],
                              'BBB': [{'Day0': {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]}}]},
                              l2w.make_time_keys(test_dd, 1, 'Day', False, False))

    def test_make_time_keys_mdy(self):
        test_dd = {('AAA', '08/21/2019'): {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]},
                    ('BBB', '08/21/2019'): {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]},
                    ('AAA', '08/22/2019'): {'Col1': [2,np.nan, 3, 1], 'Col2':['b', 'b', np.nan, 'a']}}

        test_dd = l2w.split_keys(test_dd, False)

        self.maxDiff = None
        self.assertDictEqual({'AAA': [{'Day0': {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]}},
                                      {'Day1': {'Col1': [2,np.nan, 3, 1], 'Col2':['b', 'b', np.nan, 'a']}}],
                              'BBB': [{'Day0': {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]}}]},
                              l2w.make_time_keys(test_dd, 1, 'Day', False, False))

    def test_make_time_keys_string(self):
        test_dd = {('AAA', 'TILLB'): {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]},
                    ('BBB', 'TILLB'): {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]},
                    ('AAA', 'TILL6'): {'Col1': [2,np.nan, 3, 1], 'Col2':['b', 'b', np.nan, 'a']}}

        test_dd = l2w.split_keys(test_dd, True)

        self.maxDiff = None
        self.assertDictEqual({'AAA': [{'TILLB': {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]}},
                                      {'TILL6': {'Col1': [2,np.nan, 3, 1], 'Col2':['b', 'b', np.nan, 'a']}}],
                              'BBB': [{'TILLB': {'Col1': [1,2,np.nan,4], 'Col2':['a','b', 'a', np.nan]}}]},
                              l2w.make_time_keys(test_dd, 1, '', True, False))


    def test_convert_long_to_wide_nda(self):
        src = 'NDA'
        test_dd = {('AAA', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('BBB', '08/21/2019'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('AAA', '08/22/2019'): {'Col1': ['2','', '3', '1'], 'Col2':['b', 'b', '', 'a']}}
        self.maxDiff = None
        self.assertDictEqual(defaultdict(dict,{'AAA': {'Col1_Day0': ['1','2','','4'], 'Col1_Day1': ['2','', '3', '1'],
                                                       'Col2_Day0': ['a','b', 'a', ''], 'Col2_Day1': ['b', 'b', '', 'a']},
                              'BBB': {'Col1_Day0': ['1','2','','4'], 'Col2_Day0': ['a','b', 'a', '']}}),
                              l2w.convert_long_to_wide(test_dd, 1, 'Day', intindc = False, savecols='',
                                                       indicator = False, aggfunc = 'mean')[0])

    def test_convert_long_to_wide_fitbir(self):
        src = 'FITBIR'
        test_dd = {('AAA', '3_months'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('BBB', '3_months'): {'Col1': ['1','2','','4'], 'Col2':['a','b', 'a', '']},
                    ('AAA', '6_months'): {'Col1': ['2','', '3', '1'], 'Col2':['b', 'b', '', 'a']}}
        self.maxDiff = None
        self.assertDictEqual(defaultdict(dict,{'AAA': {'Col1_3_months': ['1','2','','4'], 'Col1_6_months': ['2','', '3', '1'], 'Col2_3_months': ['a','b', 'a', ''],
                                                       'Col2_6_months': ['b', 'b', '', 'a']},
                              'BBB': {'Col1_3_months': ['1','2','','4'], 'Col2_3_months': ['a','b', 'a', '']}}),
                              l2w.convert_long_to_wide(test_dd, 1, '', intindc = True, savecols='',
                                                       indicator = True, aggfunc = 'mean')[0])




# if __name__ == '__main__':
#     unittest.main()
