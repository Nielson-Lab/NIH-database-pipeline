"""
# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

Description: This runs the unit tests for the merge_csvs module. This requires pytest to run.
"""

import os
print(os.getcwd())

import pytest
from merge_csvs import merge_all, merge_lists, compare_lists

class TestMergeLists:

    def test_can_be_merged(self):
        l1 = ['AAA', '2013-03-14', '', '', '2', '4', '6', 'ADHD']
        l2 = ['AAA', '2013-03-14', '0', '1', '2', '4', '6', '']

        merged_row = merge_lists(l1, l2)
        assert merged_row == ['AAA', '2013-03-14', '0', '1', '2', '4', '6', 'ADHD']

    def test_can_be_merged_l1(self):
        l1 = ['AAA', '2013-03-14', '0', '1', '2', '4', '6', 'ADHD']
        l2 = ['AAA', '2013-03-14', '0', '1', '2', '4', '6', '']

        merged_row = merge_lists(l1, l2)
        assert merged_row == ['AAA', '2013-03-14', '0', '1', '2', '4', '6', 'ADHD']

    def test_can_be_merged_l2(self):
        l1 = ['AAA', '2013-03-14', '', '', '2', '4', '6', 'ADHD']
        l2 = ['AAA', '2013-03-14', '0', '1', '2', '4', '6', 'ADHD']

        merged_row = merge_lists(l1, l2)
        assert merged_row == ['AAA', '2013-03-14', '0', '1', '2', '4', '6', 'ADHD']

    def test_cannot_be_merged_l1(self):
        l1 = ['AAA', '2013-03-14', '', '', '3', '4', '6', 'ADHD']
        l2 = ['AAA', '2013-03-14', '0', '1', '2', '4', '6', 'ADHD']

        merged_row = merge_lists(l1, l2)
        assert merged_row == [l1, l2]

# class TestCompareLists:

#     def test_
