#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

Description: This module contains the code to create inputs and buttons on each webpage of the application.
"""

from flask import *
from flask_wtf import Form
from wtforms import *

class BaseForm(Form):
    pf            = SubmitField("Preprocess FITBIR")
    pn            = SubmitField("Preprocess NDA")
    mt            = SubmitField("Merge & Transform")
    merge         = SubmitField("Merge")
    transform     = SubmitField("Transform")
    stats         = SubmitField("Get Stats")
    preview       = SubmitField("Visualize Dataset")
    nda           = SubmitField("Collect NDA Data Dictionaries")
    fitbir        = SubmitField("Collect FITBIR Data Dictionaries")
    shutdown      = SubmitField("Quit")

class DBForm(Form):

    archive       = RadioField("Database", choices = [("value1","NDA"), ("value2","FITBIR/NIDA")])
    execute       = SubmitField("Submit")

class MergeTransForm(Form):

    # archive = RadioField("Database", choices = [("value1","NDA"), ("value2","FITBIR/NIDA")])
    colkeep       = RadioField("KeepCol", choices = [("value1", "NDA"), ("value2", "FITBIR")])
    binding       = RadioField("Binding", choices = [("value1", "Row"), ("value2", "Column")])
    #files = MultipleFileField(validators=[validators.regexp(r'.csv$|.txt$')])
    savecols      = StringField("leavealone")
    id_col        = StringField("guids")
    date_col      = StringField("times", default = "NA")
    time_interval = FloatField("ti", validators=[validators.NumberRange(min=1, message="Time interval must be an integer greater than zero.")])
    #time_units = SelectMultipleField("units", choices = [("days", "Days"), ("weeks", "Weeks"), ("months", "Months"), ("years", "Years")])
    aggfunc       = SelectMultipleField("aggfunction", choices = [("mean", "mean"), ("median", "median"), ("mode", "mode"), ("first", "first"), ("last", "last"), ("none", "none")])
    int_indc      = RadioField("Usevals", choices = [("value1", "Yes"), ("value2","No")])
    prefix        = StringField("prefix", default = "TP")
    savename      = StringField("savename", default = "merged_and_transformed_file.csv")
    execute       = SubmitField("Merge & Transform")

class MergeForm(Form):
    # archive = RadioField("Database", choices = [("value1","NDA"), ("value2","FITBIR/NIDA")])
    colkeep       = RadioField("KeepCol", choices = [("value1", "NDA"), ("value2", "FITBIR")])
    binding       = RadioField("Binding", choices = [("value1", "Row"), ("value2", "Column")])
    id_col        = StringField("guids")
    date_col      = StringField("times", default = "NA")
    savename      = StringField("savename", default = "merged_file.csv")
    execute       = SubmitField("Merge Files")

class TransForm(Form):
    # archive = RadioField("Database", choices = [("value1","NDA"), ("value2","FITBIR/NIDA")])
    # file = FileField(validators=[validators.regexp(r'.csv$|.txt$')])
    savecols      = StringField("leavealone")
    id_col        = StringField("guids")
    date_col      = StringField("times")
    time_interval = FloatField("ti", validators=[validators.NumberRange(min=1, message="Time interval must be an integer greater than zero.")])
    # time_units = SelectMultipleField("units", choices = [("days", "Days"), ("weeks", "Weeks"), ("months", "Months"), ("years", "Years")])
    aggfunc       = SelectMultipleField("aggfunction", choices = [("mean", "mean"), ("median", "median"), ("mode", "mode"), ("first", "first"), ("last", "last"), ("none", "none")])
    int_indc      = RadioField("Usevals", choices = [("value1", "Yes"), ("value2","No")])
    suffix        = StringField("prefix", default = "TP")
    savename      = StringField("savename", default = "transformed_file.csv")
    execute       = SubmitField("Transform File")

class TempForm(Form):

    archive       = RadioField("Database", choices = [("value1","NDA"), ("value2","FITBIR/NIDA")])
    execute       = SubmitField("Submit")

class PreviewForm(Form):

    file_names    = SelectField('file_names', coerce=str)
    feature_names = SelectField('features', coerce=str)
    execute       = SubmitField("Submit")

class StatsForm(Form):
    #file = FileField(validators=[validators.regexp(r'.csv$|.txt$')])

    savename      = StringField("savename", default = "stats_file.csv")
    execute       = SubmitField("Get Stats")

class processNDA(Form):

    remove        = RadioField("drop_cols", choices = [("value1", "Yes"), ("value2", "No")], default = 'value1')
    drop_cols     = StringField("drop_columns")
    scale_cols    = RadioField("scale_cols", choices = [("value1", "Yes"), ("value2", "No")], default = 'value2')
    change_cols   = RadioField("change_cols", choices = [("value1", "Yes"), ("value2", "No")], default = 'value2')
    indic_cols    = StringField("icols", default = 'ALL')
    miss_val      = StringField("missing_value", default = '')
    drop_na_cols  = RadioField("dropnacols", choices = [("value1", "Yes"), ("value2", "No")], default = 'value1')
    execute       = SubmitField("Process NDA files")

class processFITBIR(Form):


    splitcols     = RadioField("splitcols", choices = [("value1", "Yes"), ("value2", "No")], default = 'value2')
    splitall      = RadioField("allcols", choices = [("value1", "Yes"), ("value2", "No")], default = 'value1')
    cols_to_split = StringField("cols_split")
    num_suffixes  = FloatField("ns", validators=[validators.NumberRange(min=1, message="Time interval must be an integer greater than zero.")], default = 1)
    remove        = RadioField("drop_cols", choices = [("value1", "Yes"), ("value2", "No")], default = 'value1')
    drop_cols     = StringField("drop_columns")
    scale_cols    = RadioField("scale_cols", choices = [("value1", "Yes"), ("value2", "No")], default = 'value2')
    change_cols   = RadioField("change_cols", choices = [("value1", "Yes"), ("value2", "No")], default = 'value2')
    indic_cols    = StringField("icols", default = 'ALL')
    miss_val      = StringField("missing_value", default = '')
    flatten_cols  = RadioField("flatten", choices = [("value1", "Yes"), ("value2", "No")], default = 'value2')
    make_list     = RadioField("list", choices = [("value1", "Yes"), ("value2", "No")], default = 'value2')
    group_cols    = StringField("group_cols")
    drop_na_cols  = RadioField("dropnacols", choices = [("value1", "Yes"), ("value2", "No")], default = 'value1')
    execute       = SubmitField("Process FITBIR files")

class NDAscrapeForm(Form):
    shortnames    = MultipleFileField(validators=[validators.regexp(r'.csv$|.txt$')])
    execute_some  = SubmitField("Get NDA Data Dictionaries")
    execute_all   = SubmitField("Get ALL NDA Data Dictionaries")

class FITBIRscrapeForm(Form):
    shortnames    = MultipleFileField(validators=[validators.regexp(r'.csv$|.txt$')])
    execute_some  = SubmitField("Get FITBIR Data Dictionaries")
    execute_all   = SubmitField("Get ALL FITBIR Data Dictionaries")

class ShutdownForm(Form):
    execute = SubmitField("Quit")
