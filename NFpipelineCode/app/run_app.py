#!/usr/bin/env python3
"""
Created on Tue Jul 16 14:37:21 2019

@author: kirsh012

Description: The main application file.

This repository was developed with funding from the National Institute of Mental Health (NIMH),
grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
©2024 Regents of the University of Minnesota. All rights reserved.

This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
(https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)
"""

### Import libraries to build the app ###
import webbrowser
import random
from threading import Timer
from flask import *
from wtforms import *
from flask_wtf import Form
from werkzeug import secure_filename
from forms import *
import csv
import sqlite3 as sql
import pandas as pd
import os
import glob
import re
import numpy as np
import time
import io
import logging
import warnings
warnings.filterwarnings("ignore")

# Import code to run on data given to app
import merge_csvs as mcsvs
import long2wide as lw
import stats_pipeline as pstats
import scrape_NDA_data_dictionary as scrapeNDA
import scrape_FITBIR_data_dictionary as scrapeFITBIR
import scrape_all_NDA as scrapeNDAall
import scrape_all_fitbir_dictionaries as scrapeFITBIRall
from preprocessNDA import *
from preprocessFITBIR import *


# Import Bokeh libraries
from bokeh.plotting import figure
from bokeh.embed import components, server_document
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider
from bokeh.io import show, output_file
from bokeh.layouts import column, row, WidgetBox
from bokeh.models import Panel

# Import Dash libraries
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash_table.Format import Format, Scheme, Sign, Symbol
import plotly.graph_objs as go
import plotly.express as px
import cufflinks as cf
import base64

import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    application_path = Path(sys.executable)#sys._MEIPASS
else:
    application_path = Path(__file__) #os.path.abspath(__file__)
    logging.info('Using the script to run application...')

print(f"The application path is {application_path}")
#if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):#
#    application_path = Path(sys._MEIPASS)
#else:
#    application_path = Path(__file__).parent

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

#if getattr(sys, 'frozen', True):
#    print("sys is FROZEN!")
#    application_path = Path(sys._MEIPASS)
#else:
#    print("sys is NOT Frozen!")
#    application_path = Path(os.path.dirname(os.path.abspath(__file__)))

database_path = resource_path('database/aligned_first_element.db')
print(f"The database path is {database_path}")
#print(sys.executable)

#print(os.path.dirname(os.path.abspath(__file__)))
m = re.search('.+?(?=NFP\.)', str(application_path))
if m is None:
    #print("m is None!")
    new_path = application_path.parent.parent
    #print(new_path)
else:
    new_path = m.group(0) #application_path.parent

os.chdir(new_path)#os.chdir('/'.join(application_path.split('/')[:-1]))
print(f"The new path is {new_path}")
base_url = "http://localhost:5271"

app = Flask(__name__)
UPLOAD_FOLDER = str(new_path) + os.sep + 'Inputs' #'../Inputs'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# For debugging, comment out when running in waitress
#app.config['ENV'] = 'development'
#app.config['DEBUG'] = True
#app.config['TESTING'] = True

app.secret_key = os.urandom(24)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app_dash = dash.Dash(
    __name__,
    server = app,
    routes_pathname_prefix = '/preview/preview_data/',
    external_stylesheets = external_stylesheets
)

### Connect to the Aligned SQLite Database
def get_db_connection():
    conn = None
    try: # Try to connect
        #str(new_path) + os.sep + 'databases' + os.sep
        conn = sql.connect(database_path)
        logging.info('Connected to database...')
        temp_cursor = conn.execute("SELECT * FROM alignment")
        logging.info('Selected all from database...')
        names = list(map(lambda x: x[0], temp_cursor.description))
        #print(names)
    except Exception as e:
        logging.info(e)
        print(e)

    return conn


### Deprecated Bokeh visualizations in favor of Dash ###

#file_names = glob.glob(str(UPLOAD_FOLDER) + os.sep + '*.[ct]*')
# state = {}

# # Make the Histogram
# def update(attr, old, new):
#     bins = bin_selector.value

#     new_source = make_dataset(inp_df, feature_name, bins)

#     tsrc.data.update(new_source.data)


# def make_dataset(df, name, bins):

#     hist, edges = np.histogram(df[name], bins, range = [df[name].min() - 5, df[name].max() + 5])

#     temp_df = pd.DataFrame({"values": hist, 'left': edges[:-1], 'right': edges[1:]})
#     return temp_df#ColumnDataSource(temp_df)

# def update_time(attr, old, new):
#     bins = bin_selector.value

#     new_source = make_time_dataset(inp_df, feature_name, bins)

#     tsrc.data.update(new_source.data)


# def make_time_dataset(df, name, bins):

#     hist, edges = np.histogram(df["Days"], bins, range = [df["Days"].min() - 5, df["Days"].max() + 5])

#     temp_df = pd.DataFrame({"values": hist, 'left': edges[:-1], 'right': edges[1:]})
#     return temp_df#ColumnDataSource(temp_df)

# def create_histogram(inp_df, feature_name):
#     #source = ColumnDataSource(data = inp_df)

#     #print(inp_df.columns)
#     try:
#         inp_df[feature_name] = pd.to_numeric(inp_df[feature_name])
#         is_num = True
#     except ValueError:
#         is_num = False


#     if is_num: #(inp_df[feature_name].dtype == 'float64') or (inp_df[feature_name].dtype == 'int64'):
#         #bin_selector = Slider(start = 10, end = 100, step = 1, value = 10, title = "Choose Number of Bins")
#         #bin_selector.on_change('value', update)
#         #bins = bin_selector.value

#         # Remove missing values
#         inp_df[feature_name] = inp_df[feature_name].dropna()
#         bins = int(inp_df[feature_name].max() - inp_df[feature_name].min()) + 1
#         tsrc = make_dataset(inp_df, feature_name, bins)
#         h = figure(plot_height = 600, plot_width = 600, x_axis_label = feature_name, y_axis_label = "Counts")

#         h.quad(bottom = 0, top = tsrc['values'], left = tsrc['left'], right = tsrc['right'],
#                 fill_color = '#8EEAFF', line_color = 'black')

#         return h#(h, bin_selector)

#     else:
#         try:
#             # Plot datetimes
#             inp_df[feature_name] = pd.to_datetime(inp_df[feature_name])
#             is_date = True
#         except ValueError:
#             is_date = False
#             #print(f"{feature_name} being read as datetime type")
#             #bin_selector = Slider(start = 10, end = 100, step = 1, value = 10, title = "Choose Number of Bins")
#             #bin_selector.on_change('value', update)
#             #bins = bin_selector.value


#         if is_date:
#             inp_df[feature_name] = pd.to_datetime(inp_df[feature_name])

#             inp_df[feature_name] = inp_df[feature_name].dropna()

#             bins = (inp_df[feature_name].max() - inp_df[feature_name].min()).days + 1

#             inp_df.sort_values(by=feature_name, inplace = True)
#             start = inp_df[feature_name].iloc[0]
#             inp_df["Days"] = inp_df[feature_name].apply(lambda x: x - start).dt.days

#             tsrc = make_dataset(inp_df, 'Days', bins)
#             #print(tsrc)
#             h = figure(plot_height = 600, plot_width = 600, x_axis_label = feature_name + "  (days)", y_axis_label = "Counts")

#             h.quad(bottom = 0, top = tsrc['values'], left = tsrc['left'], right = tsrc['right'],
#                     fill_color = '#FF9B00', line_color = 'black')

#             '''
#             values = group.index.tolist()
#             counts = group.values.tolist()

#             h = figure(x_range = values, plot_height = 600, plot_width = 600, x_axis_label = feature_name, y_axis_label = "Counts")

#             h.vbar(x = values, top = counts, width = 0.9)

#             h.xgrid.grid_line_color = None
#             h.y_range.start = 0
#             '''

#             return h#(h, bin_selector)

#         else:

#             print(f"{feature_name} being read as object type")
#             values = inp_df[feature_name].value_counts(dropna = True).index.tolist()
#             counts = inp_df[feature_name].value_counts(dropna = True).values.tolist()

#             h = figure(x_range = values, plot_height = 600, plot_width = 600, x_axis_label = feature_name, y_axis_label = "Counts")

#             h.vbar(x = values, top = counts, width = 0.9)

#             h.xaxis.major_label_orientation = np.pi/4
#             h.xgrid.grid_line_color = None
#             h.y_range.start = 0

#             return h


#     '''
#     elif inp_df[feature_name].dtype == 'datetime64[ns]':
#         group = df[feature_name].groupby(df[feature_name].dt.month).count()

#         values = group.index.tolist()
#         counts = group.values.tolist()

#         h = figure(x_range = values, plot_height = 600, plot_width = 600, x_axis_label = feature_name, y_axis_label = "Counts")

#         h.vbar(x = values, top = counts, width = 0.9)

#         h.xgrid.grid_line_color = None
#         h.y_range.start = 0

#     elif inp_df[feature_name].dtype == 'object':
#         print(f"{feature_name} being read as object type")
#         values = inp_df[feature_name].value_counts().index.tolist()
#         counts = inp_df[feature_name].value_counts().values.tolist()

#         h = figure(x_range = values, plot_height = 600, plot_width = 600, x_axis_label = feature_name, y_axis_label = "Counts")

#         h.vbar(x = values, top = counts, width = 0.9)

#         h.xgrid.grid_line_color = None
#         h.y_range.start = 0
#     '''
#     #return h

# # Read the dataset
# def read_csv(file):

#     rows = []
#     with open(file, 'r') as fin:

#         reader = csv.reader((x.replace('\0', '') for x in fin))

#         for row in reader:
#             if row != []:
#                 rows.append(row)

#     return rows

# def file_to_df(file):

#     data = read_csv(file)
#     #processed_data = []
#     #for row in data:
#     #    processed_data.append(row[:len(data[2])])


#     df = pd.DataFrame(pdata, columns = data[0])
#     df.columns = [col.strip() for col in df.columns]



#     return df

#def shutdown_server():
#    func = request.environ.get('werkzeug.server.shutdown')
#    if func is None:
#        raise RuntimeError('Not running with the Werkzeug Server')
#    func()


@app.route("/", methods = ["GET", "POST"])
def main_form():

    #logging.debug('This message should go to the log file')
    logging.info(f"Application path location is {new_path}")
    #logging.warning('And this, too')
    #logging.error('And non-ASCII stuff, too, like Øresund and Malmö')
    form = BaseForm(request.form)
    if form.pn.data:
        return redirect(url_for("ppNDA"))
    elif form.pf.data:
        return redirect(url_for("ppFITBIR"))
    elif form.mt.data:
        return redirect(url_for("merge_and_transform"))
    elif form.merge.data:
        return redirect(url_for("merge"))
    elif form.transform.data:
        return redirect(url_for("transform"))
    elif form.stats.data:
        return redirect(url_for("get_stats"))
    elif form.preview.data:
        return redirect(url_for("/preview/preview_data/"))
    elif form.nda.data:
        return redirect(url_for("scrape_NDA"))
    elif form.fitbir.data:
        return redirect(url_for("scrape_FITBIR"))
    #elif form.shutdown.data:
    #    shutdown_server()
    #    return 'Server shutting down...'#redirect(url_for("shutdown"))
    #print(form.validate())
    #if request.method == "POST":# and form.validate():
    #    print(form.mt.data)
    #print(dir(request.form))

    return render_template("base.html", form = form)#, mt = mt_url,
                           #m=m_url, t=t_url, s=s_url, snda=nda_url, sfitbir=fitbir_url)

#@app.route('/shutdown', methods=['POST'])
#def shutdown():
#    shutdown_server()
#    return 'Server shutting down...'

@app.route("/preprocessNDA", methods = ['GET', 'POST'])
def ppNDA():

    #print(dir(request))
    form = processNDA(request.form)

    # Load the alignment names into a dictionary

    con = get_db_connection()
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT NDA_Element, FITBIR_Element, NF_Condition1, NF_Condition2, \
                NF_Operator, NF_formula FROM alignment')

    column_mapping = dict()
    column_scaling = dict()
    for row in cur.fetchall():
        if row['NDA_Element'].strip() not in column_mapping.keys():
            column_mapping[row['NDA_Element'].strip()] = row['FITBIR_Element'].strip()
            # Do the same for scaling
            # Need to make the keys the same for scaling, since the conditions
            # are based on the FITBIR names
            column_scaling[row['NDA_Element'].strip()] = {
                                                            'FITBIR_Element': row['FITBIR_Element'].strip(),
                                                            'Condition1': row['NF_Condition1'],
                                                            'Condition2': row['NF_Condition2'],
                                                            'Operator': row['NF_Operator'],
                                                            'Formula': row['NF_formula']
                                                            }
    con.close()

    # Display the following paths in the application
    #flash(application_path)
    #flash(database_path)
    #flash(new_path)
    #flash(UPLOAD_FOLDER)
    if form.execute.data:
        logging.info(UPLOAD_FOLDER)
        datafiles = glob.glob(f'{UPLOAD_FOLDER}{os.sep}*.[ct]*')

        for file in datafiles:


            pnda = NDAdataset()
            logging.info("Initialized dataset")
            # Read csv file
            pnda.read_csv(file)
            logging.info("Read file")
            # Remove certain columns
            remove_choice = form.remove.data
            #remove_choices = form.remove.choices
            #for name, val in remove_choices:
            #    if name == remove_choice:
            #        if val == 'Yes':


            if remove_choice == 'value1':
                drop_cols = form.drop_cols.data.split(';')
                #print(drop_cols)
                pnda.remove_cols(drop_cols)
                logging.info("removed some columns")

            # Collect the metadata
            metadata = pnda.collect_metadata()
            logging.info("collected metadata")
            # Write metadata to file
            with open(f'{new_path}{os.sep}Outputs{os.sep}metadata_{file.split(os.sep)[-1]}', 'w') as fout:
                writer = csv.DictWriter(fout, fieldnames = ['Variable', 'Description'])
                writer.writeheader()
                for key, value in metadata.items():
                    writer.writerow({'Variable': key, 'Description': value})

            logging.info("wrote metadata to file")
            # Remove empty columns
            na_choice = form.drop_na_cols.data
            if na_choice == 'value1':
                logging.info("Dropped empty columns")
                pnda.remove_empty_cols()

            # Scale to match values in FITBIR
            scale_choice = form.scale_cols.data
            if scale_choice == 'value1':
                logging.info("Scaling to match FITBIR...")
                pnda.convert_scaling_to_fitbir(column_scaling)

            # Change column names to match FITBIR's (do AFTER scaling!)
            change_choice = form.change_cols.data
            if change_choice == 'value1':
                pnda.change_cols_to_fitbir(column_mapping)
                logging.info("Using FITBIR column names!")

            # Create indicator columns
            no_cols = ['', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan', '1.#IND', \
                        '1.#QNAN', '<NA>', 'N/A', 'NA', 'NULL', 'NaN', 'n/a', 'nan', 'null', 'none']

            no_cols = list(map(lambda x: x.lower(), no_cols))

            if form.indic_cols.data.lower() != 'all':
                if form.indic_cols.data.lower() in no_cols:
                    indicator_cols = []
                else:
                    indicator_cols = form.indic_cols.data.split(';')
            else:
                indicator_cols = list(pnda.dataset.keys())

            logging.info(indicator_cols)

            # Handle missing data
            #if form.miss_val.data != 'NA'.lower():

            use_vals = form.miss_val.data.split(';')
            if indicator_cols != []:
                for col in indicator_cols:
                    for use_val in use_vals:
                        pnda.handle_missing_data(col, use_val)

            # Save the processed data set
            savename = str(new_path) + '{0}Outputs{0}'.format(os.sep) + 'processed_' + file.split(os.sep)[-1]
            pnda.to_csv(savename)

            flash(f"{file.split(os.sep)[-1]} has been processed and saved to the Outputs folder")
            #Response(generate(), mimetype= 'text/event-stream')

    return render_template('process_nda.html', form = form)


@app.route("/preprocessFITBIR", methods = ['GET', 'POST'])
def ppFITBIR():

    form = processFITBIR(request.form)

    # Load the alignment names into a dictionary
    con = get_db_connection()
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT NDA_Element, FITBIR_Element, FN_Condition1, FN_Condition2, \
                FN_Operator, FN_formula FROM alignment')

    column_mapping = dict()
    column_scaling = dict()
    for row in cur.fetchall():
        if row['FITBIR_Element'].strip() not in column_mapping.keys():
            column_mapping[row['FITBIR_Element'].strip()] = row['NDA_Element'].strip()
            # Do the same for scaling
            column_scaling[row['FITBIR_Element'].strip()] = {
                                                            'Condition1': row['FN_Condition1'],
                                                            'Condition2': row['FN_Condition2'],
                                                            'Operator': row['FN_Operator'],
                                                            'Formula': row['FN_formula']
                                                            }

    con.close()

    if form.execute.data:

        logging.info("FITBIR Preprocess Form has been executed.")
        datafiles = glob.glob(str(UPLOAD_FOLDER) + os.sep + '*.[ct]*')

        for file in datafiles:
            logging.info(file)
            # IMPORTANT: we create a new object for each file because each
            # file is processed separately.
            # Create dataset object
            pfitbir = FITBIRdataset()
            # Read in CSV file
            pfitbir.read_csv(file)

            # Split cols based on periods
            spc_choice = form.splitcols.data
            spc_choices = form.splitcols.choices
            for spc_name, spc_val in spc_choices:
                if spc_name == spc_choice:
                    if spc_val == 'Yes':

            #if form.splitcols.data == 'Yes':

                        # Keep certain parts of the column names
                        num_suffixes = int(form.num_suffixes.data)
                        split_columns = form.cols_to_split.data
                        use_columns = split_columns.split(';')
                        split_all = False
                        logging.info("Split cols yes")
                        #print(pfitbir.dataset)
                        pfitbir.split_cols(use_columns, split_all, num_suffixes)
                        logging.info("Splitted columns")
                        #print(pfitbir.dataset)

            # Split all the columns
            sall_choice = form.splitall.data
            sall_choices = form.splitall.choices
            for sall_name, sall_val in sall_choices:
                if sall_name == sall_choice:
                    if sall_val == 'Yes':

            #if form.splitall.data == 'Yes':
                        # Keep certain parts of the column names
                        num_suffixes = int(form.num_suffixes.data)

                        split_all = True
                        use_columns = list(pfitbir.dataset.keys())


                        pfitbir.split_cols(use_columns, split_all, num_suffixes)

            # Remove certain columns
            rm_choice = form.remove.data
            rm_choices = form.remove.choices
            for rname, rval in rm_choices:
                if rname == rm_choice:
                    if rval == 'Yes':
                        drop_cols = form.drop_cols.data
                        drop_cols = drop_cols.split(';')
                        pfitbir.remove_cols(drop_cols)

            #if form.remove.data == 'Yes':

            #    drop_cols = form.drop_cols.data

            #    pfitbir.remove_cols(drop_cols)

            # Drop empty columns
            #print("NA COLUMNS")
            #print(form.drop_na_cols.data)
            #print(form.drop_na_cols.choices)
            na_choice = form.drop_na_cols.data
            na_choices = form.drop_na_cols.choices
            for name, val in na_choices:
                if name == na_choice:
                    if val == 'Yes':
                        #print("NA columns")
                        pfitbir.remove_empty_cols()

            # Scale to match values in NDA
            scale_choice = form.scale_cols.data
            if scale_choice == 'value1':
                logging.info("Scaling to match NDA...")
                pfitbir.convert_scaling_to_nda(column_scaling)

            # Change column names to match NDA's
            change_choice = form.change_cols.data
            if change_choice == 'value1':
                logging.info("Using NDA column names...")
                pfitbir.change_cols_to_nda(column_mapping)



            # Handle missing data
            no_cols = ['', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan', '1.#IND', \
                        '1.#QNAN', '<NA>', 'N/A', 'NA', 'NULL', 'NaN', 'n/a', 'nan', 'null', 'none']

            no_cols = list(map(lambda x: x.lower(), no_cols))

            # Create indicator columns
            if form.indic_cols.data.lower() != 'all':
                if form.indic_cols.data.lower() in no_cols:
                    indicator_cols = []
                else:
                    indicator_cols = form.indic_cols.data.split(';')
            else:
                indicator_cols = list(pfitbir.dataset.keys())

            # Replace values in columns
            use_vals = form.miss_val.data.split(';')
            if indicator_cols != []:
                for col in indicator_cols:
                    for use_val in use_vals:
                        pfitbir.handle_missing_data(col, use_val)

            # Make list file of unflattened columns
            f_choice = form.flatten_cols.data
            f_choices = form.flatten_cols.choices
            for fname, fval in f_choices:
                if fname == f_choice:
                    f_val = fval

            ml_choice = form.make_list.data
            ml_choices = form.make_list.choices
            for mlname, mlval in ml_choices:
                if mlname == ml_choice:
                    ml_val =  mlval

            if f_val == 'Yes':

                group_cols = form.group_cols.data.split(';')

                # Check if they want to save the bad columns to a separate list
                if ml_val == 'Yes':

                    sprefix = str(new_path)
                    bcols, ucols = pfitbir.find_bad_columns(group_cols)
                    pfitbir.fix_bad_columns(True, bcols, ucols, sprefix)

                else:
                    sprefix = str(new_path)

                    bcols, ucols = pfitbir.find_bad_columns(group_cols)
                    pfitbir.fix_bad_columns(False, bcols, ucols, sprefix)

            # Save the data file to a new file
            savename = str(new_path) + '{0}Outputs{0}'.format(os.sep) + 'processed_' + file.split(os.sep)[-1]
            pfitbir.to_csv(savename)
            logging.info(f"{file} has been processed and saved to the Outputs folder")
            flash(f"{file} has been processed and saved to the Outputs folder")


    return render_template('process_fitbir.html', form = form)



@app.route("/mergetransform", methods = ["GET", "POST"])
def merge_and_transform():
    ''' This is where the script to merge and transform the data is called. '''
    form = MergeTransForm(request.form)
    start = time.time()
    if form.execute.data:
        #print(form.archive)

        # Get the source of the data
        # choice = form.archive.data
        # choices = form.archive.choices
        # for name, val in choices:
        #     if name == choice:
        #         source = val

        # Get the binding declaration
        bchoice = form.binding.data
        #print("BCHOICE: ", bchoice)
        bchoices = form.binding.choices
        #print("BCHOICES: ", bchoices)
        for bname, bval in bchoices:
            #print(bname, bval)
            if bname == bchoice:
                bind = bval.lower()
                #print("BIND: ", bind)

        datafiles = glob.glob(str(UPLOAD_FOLDER) + os.sep + '*.[ct]*') #glob.glob("{}/*.[ct]*".format(UPLOAD_FOLDER))#[]#form.files.data


        idcol = form.id_col.data
        datecol = form.date_col.data
        if datecol == 'NA':
            datecol = False

        ti = form.time_interval.data
        #tu = form.time_units.data
        prefix = form.prefix.data

        save_cols = form.savecols.data
        aggfunc = form.aggfunc.data
        logging.info(f"AGGFUN in run_app: {aggfunc}")

        iindc = form.int_indc.data
        int_choices = form.int_indc.choices
        for n, v in int_choices:
            if n == iindc:
                iindc = v

        if iindc == "Yes":
            intindc = True
        else:
            intindc = False

        savename = form.savename.data
        if '.' not in savename:
            savename = savename + '.csv'

        save = str(new_path) + '{0}Outputs{0}'.format(os.sep) + savename#"../Outputs/" + savename
        #print(save)
        #print(dir(form.archive))
        logging.info("Going to Merge and Transform")
        flash("Going to Merge and Transform")

        ### Run the merge and transform pipeline
        mcsvs.main(datafiles, save, idcol, save_cols, bind, date_col=datecol, l2w = True, suffix = prefix, ti = ti, aggfunc = aggfunc, intindc = intindc)

        logging.info("Merge and transform complete. Open file in the \'Outputs\' folder")
        flash("Merge and transform complete. Open file in the \'Outputs\' folder")
        end = time.time()
        total_time = end- start
        if total_time/60 > 60:
            logging.info("Total time to merge and transfrom: {:.5f} hours".format(total_time/3600))
            flash("Total time to merge and transfrom: {:.5f} hours".format(total_time/3600))

        elif (total_time/60 < 60) & (total_time > 60):
            logging.info("Total time to merge and transfrom: {:.5f} minutes".format(total_time/60))
            flash("Total time to merge and transfrom: {:.5f} minutes".format(total_time/60))
        else:
            logging.info("Total time to merge and transfrom: {:.5f} seconds".format(total_time))
            flash("Total time to merge and transfrom: {:.5f} seconds".format(total_time))

    return render_template('merge_transform.html', form = form)
    #return

@app.route("/merge", methods = ["GET", "POST"])
def merge():
    form = MergeForm(request.form)
    if form.execute.data: #request.method == "POST" and form.validate():
        #print(dir(form.archive))
        start = time.time()
        # choice = form.archive.data
        # choices = form.archive.choices
        # for name, val in choices:
        #     if name == choice:
        #         source = val

        # Get the binding declaration
        bselection = form.binding.data
        boptions = form.binding.choices
        for n, v in boptions:
            if n == bselection:
                bind = v.lower()

        s = os.sep
        datafiles = glob.glob(str(UPLOAD_FOLDER) + os.sep + '*.[ct]*')#glob.glob("{}/*.[ct]*".format(UPLOAD_FOLDER))
        #print(datafiles)
        idcol = form.id_col.data
        datecol = form.date_col.data
        if datecol == 'NA':
            datecol = False

        savename = form.savename.data
        if '.' not in savename:
            savename = savename + '.csv'
        save = str(new_path) + '{0}Outputs{0}'.format(os.sep) + savename#"../Outputs/" + savename
        logging.info("Going to Merge...")
        flash("Going to Merge")

        ### Run merge pipeline section
        mcsvs.main(datafiles, save, idcol, [], bind, date_col=datecol, l2w = False, suffix = False, ti = False, aggfunc = False)

        end = time.time()
        total_time = end- start
        if total_time/60 > 60:
            logging.info("Total time to merge: {:.5f} hours".format(total_time/3600))
            flash("Total time to merge: {:.5f} hours".format(total_time/3600))

        elif (total_time/60 < 60) & (total_time > 60):
            logging.info("Total time to merge: {:.5f} minutes".format(total_time/60))
            flash("Total time to merge: {:.5f} minutes".format(total_time/60))
        else:
            logging.info("Total time to merge: {:.5f} seconds".format(total_time))
            flash("Total time to merge: {:.5f} seconds".format(total_time))

        logging.info("Merge complete. Open file in the \'Outputs\' folder")
        flash("Merge complete. Open file in the \'Outputs\' folder")
    return render_template("merge.html", form = form)
    #return

@app.route("/transform", methods = ["GET", "POST"])
def transform():
    form = TransForm(request.form)
    if form.execute.data:#request.method == "POST" and form.validate():
        start = time.time()
        # choice = form.archive.data
        # choices = form.archive.choices
        # for name, val in choices:
        #     if name == choice:
        #         source = val

        datafiles = glob.glob(str(UPLOAD_FOLDER) + os.sep + '*.[ct]*')#glob.glob("{}/*.[ct]*".format(UPLOAD_FOLDER))
        idcol = form.id_col.data
        datecol = form.date_col.data
        if datecol == 'NA':
            datecol = False

        ti = form.time_interval.data
        iindc = form.int_indc.data
        #print(iindc)
        int_choices = form.int_indc.choices
        #print(int_choices)
        for n, v in int_choices:
            if n == iindc:
                iindc = v

        save_cols = form.savecols.data

        if iindc == "Yes":
            intindc = True
        else:
            intindc = False
        #print(intindc)
        aggfunc = form.aggfunc.data#[0] # added [0]

        suff = form.suffix.data
        savename = form.savename.data
        if '.' not in savename:
            savename = savename + '.csv'
        save = str(new_path) + '{0}Outputs{0}'.format(os.sep) + savename#"../Outputs/" + savename

        logging.info("Going to Transform...")
        flash("Going to Transform...")

        ### Run transform pipeline
        dd = lw.read_csv(datafiles[0], idcol, datecol)
        fdd, cols = lw.convert_long_to_wide(dd, ti, suff, intindc, save_cols, aggfunc=aggfunc)
        lw.write_to_csv(fdd, cols, save, idcol)

        end = time.time()
        total_time = end- start
        if total_time/60 > 60:
            logging.info("Total time to transfrom: {:.5f} hours".format(total_time/3600))
            flash("Total time to transfrom: {:.5f} hours".format(total_time/3600))

        elif (total_time/60 < 60) & (total_time > 60):
            logging.info("Total time to transfrom: {:.5f} minutes".format(total_time/60))
            flash("Total time to transfrom: {:.5f} minutes".format(total_time/60))
        else:
            logging.info("Total time to transfrom: {:.5f} seconds".format(total_time))
            flash("Total time to transfrom: {:.5f} seconds".format(total_time))

        logging.info("Transformation complete. Open file in the \'Outputs\' folder")
        flash("Transformation complete. Open file in the \'Outputs\' folder")

    return render_template("transform.html", form = form)
    #return

@app.route("/get_stats", methods = ["POST", "GET"])
def get_stats():

    form = StatsForm(request.form)
    if form.execute.data:#request.method == "POST" and form.validate():
        files = glob.glob(str(UPLOAD_FOLDER) + os.sep + '*.[ct]*') #glob.glob(UPLOAD_FOLDER + '/*.[ct]*')
        savename = form.savename.data
        if '.' not in savename:
            savename = savename + '.csv'
        save = str(new_path) + '{0}Outputs{0}'.format(os.sep) + savename #"../Outputs/" + savename
        logging.info("Getting stats...")
        flash("Getting Stats...")

        ### Run stats pipeline
        sd = pstats.read_csv(files[0])
        sdd = pstats.make_stats_dict_from_file(sd)
        pstats.dict_to_csv(sdd, save)
        logging.info("Complete. Open stats file in the \'Outputs\' folder")
        flash("Complete. Open stats file in the \'Outputs\' folder")

    return render_template("stats.html", form = form)

#@app.route("/preview", methods=["GET", "POST"])
#def preview():
#    form = TempForm(request.form)
#    if form.execute.data:
#        choice = form.archive.data
#        choices = form.archive.choices
#        for name, val in choices:
#            if name == choice:
#                session['source'] = val
#
#        return redirect(url_for('preview_data'))
#    return render_template("temp.html", form = form)



#@app.route("/preview/preview_data", methods=["GET", "POST"])
#def preview_data():
app_dash.layout = html.Div([
    dcc.Tabs([
        # Data table tab
        dcc.Tab(label = 'Data Table', children = [
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select File')
                ]),
                style={
                    'width': '50%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=False
            ),
            html.H5('Choose an Example Dataset'),
            dcc.Dropdown(
                id='edataset',
                options=[{'label': i, 'value': i} for i in ['tips', 'gapminder']],
                value = 'tips',
                style = {'width': '40%',
                        'align': 'left'}
            ),
            dash_table.DataTable(
            id = 'table',
            columns = [],
            data = [],

            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'lineHeight': '15px'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold',
                'whiteSpace': 'normal',
                'height': 'auto',
                'width': '10%'
            },
            style_table = {'overflowX': 'scroll',
                           'overflowY': 'auto'},

            filter_action = "native",
            sort_action = "native",
            sort_mode = "single",
            page_action = "native"
            )
        ]),
        # Histogram tab
        dcc.Tab(label = 'Histogram', children = [
            html.Div([

            ### Create the Histogram
            html.Div([
                html.H6("Plot Column"),
                dcc.Dropdown(
                    id='histogram-xaxis-column',
                    options=[]
                ),
                html.H6("Hue Column"),
                dcc.Dropdown(
                    id='histogram-hue-column',
                    options=[]
                ),
                html.H6("Orientation"),
                dcc.RadioItems(
                    id = 'orient',
                    options = [{'label': i, 'value': i} for i in ['Vertical', 'Horizontal']],
                    value = 'Vertical',
                    labelStyle = {'display': 'inline-block'}
                ),
                html.H6("Mode"),
                dcc.Dropdown(
                    id='barmode',
                    options = [{'label': i, 'value': i} for i in ['Group', 'Overlay', 'Stacked']],
                    value = 'Overlay'
                ),
                html.H6("Bar Normalization (for nominal variables)"),
                dcc.Dropdown(
                    id='normalization',
                    options = [{'label': i, 'value': i} for i in ['None', 'fraction', 'percent']],
                    value = 'None'
                ),
                html.H6("Histogram Normalization (for numercial variables)"),
                dcc.Dropdown(
                    id='hnorm',
                    options = [{'label': i, 'value': i} for i in ['None', 'Percent', 'Probability', 'Density', 'Probability Density']],
                    value = 'None'
                ),
                html.H6("Sort Categories"),
                dcc.Dropdown(
                    id='sort-category',
                    options = [{'label': i, 'value': i} for i in ['None', 'Alphabetical Ascending', 'Alphabetical Descending', 'Count Ascending', 'Count Descending']],
                    value = 'None'
                ),
                html.H6("Include Marginal Subplot"),
                dcc.RadioItems(
                    id='marginal',
                    options = [{'label': i, 'value': i} for i in ['Yes', 'No']],
                    value = 'No',
                    labelStyle = {'display': 'inline-block'}
                )
            ], style={'width': '40%', 'align':'left', 'display': 'inline-block'}),
            html.Div([
            dcc.Graph(id='histogram',
                        config = {'editable': True,
                                  'toImageButtonOptions': {
                                  'format': 'svg',
                                  'height': 480,
                                  'width': 640,
                                  'scale': 2
                                  }
                                 }
                                 )
            ],style = {'width': '60%', 'height': '100%', 'align': 'right', 'display': 'inline-block'})
          ])
          ]),
         # Lineplot tab
         dcc.Tab(label = 'Line plot', children = [
            html.Div([
            # Create the line plot
            html.Div([
                html.H5("X-axis column"),
                dcc.Dropdown(
                    id='crossfilter-xaxis-column',
                    options=[]
                ),
                dcc.RadioItems(
                    id='crossfilter-xaxis-type',
                    options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                    value='Linear',
                    labelStyle={'display': 'inline-block'}
                ),
                html.H5("Y-axis column"),
                dcc.Dropdown(
                    id='crossfilter-yaxis-column',
                    options=[]
                ),
                dcc.RadioItems(
                    id='crossfilter-yaxis-type',
                    options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                    value='Linear',
                    labelStyle={'display': 'inline-block'}
                ),
                html.H5("Hue Column"),
                    dcc.Dropdown(
                        id='line-hue-column',
                        options=[]
                        ),
            ], style={'width': '40%', 'align': 'left', 'display': 'inline-block'}
            ),
            html.Div([
            dcc.Graph(id='lineplot',
                    config = {'editable': True,
                              'toImageButtonOptions': {
                              'format': 'svg',
                              'height': 480,
                              'width': 640,
                              'scale': 2
                              }
                             }
                    )
            ], style = { 'width': '60%', 'align':'right', 'display':'inline-block'})
            ]),


        # Ends Tab children
        ]),

         # Scatter plot tab
         dcc.Tab(label = 'Scatter plot', children = [
            html.Div([

                html.Div([
                    html.H5("X-axis column"),
                    dcc.Dropdown(
                        id='sxcol',
                        options=[]
                    ),
                    html.H5("Y-axis column"),
                    dcc.Dropdown(
                        id='sycol',
                        options=[]
                    ),
                    html.H5("Hue Column"),
                    dcc.Dropdown(
                        id='shue_col',
                        options=[]
                    ),
                    html.H5("Marker Size Column (must be numeric)"),
                    dcc.Dropdown(
                        id='ssize_col',
                        options=[]
                    ),
                    html.H5("Marker Style Column"),
                    dcc.Dropdown(
                        id='sstyle',
                        options=[]
                    )
                ], style = {'width': '40%', 'align':'left', 'display': 'inline-block'}),
                html.Div([
                dcc.Graph(id='scatterplot',
                            config = {'editable': True,
                                      'toImageButtonOptions': {
                                      'format': 'svg',
                                      'height': 480,
                                      'width': 640,
                                      'scale': 2
                                      }
                                     }
                            )
                ], style = {'width':'60%', 'align': 'right', 'display':'inline-block'})
            ])
         ]),

         # Heatmap tab
         dcc.Tab(label = 'Heatmap', children = [
            html.Div([

                html.Div([
                    html.H5("X-axis column"),
                    dcc.Dropdown(
                        id='hxcol',
                        options=[]
                    ),
                    html.H5("Y-axis column"),
                    dcc.Dropdown(
                        id='hycol',
                        options=[]
                        ),
                    html.H5("Color Map"),
                    dcc.Dropdown(
                        id='colormap',
                        options=[{'label': i, 'value': i}
                        for i in ['Cividis', 'Plasma', 'Bluered', 'Rainbow',
                                'Reds', 'Blues', 'Greens', 'OrRd', 'RdBu',
                                'thermal']],
                        value = 'Cividis'
                    ),
                    html.H5("Centering Value"),
                    dcc.Input(
                        id='center',
                        type='number'
                    )
                ], style={'width': '40%', 'align': 'left', 'display': 'inline-block'}
                ),
                html.Div([
                    dcc.Graph(id='heatmap',
                            config = {'editable': True,
                                      'toImageButtonOptions': {
                                      'format': 'svg',
                                      'height': 480,
                                      'width': 640,
                                      'scale': 2
                                      }
                                     }
                            )
                ], style = {'width': '60%', 'align': 'right', 'display': 'inline-block'})
            ])

         ]),
         # Boxplot tab
         dcc.Tab(label = 'Boxplot', children = [
            html.Div([

                html.Div([
                    html.H5("X-axis column"),
                    dcc.Dropdown(
                        id='bxcol',
                        options=[]
                    ),
                    html.H5("Y-axis column"),
                    dcc.Dropdown(
                        id='bycol',
                        options=[]
                    ),
                    html.H5("Group Column"),
                    dcc.Dropdown(
                        id='bgroup_col',
                        options=[]
                    ),
                    html.H5("Orientation"),
                    dcc.RadioItems(
                        id = 'borient',
                        options = [{'label': i, 'value': i} for i in ['Vertical', 'Horizontal']],
                        value = 'Vertical',
                        labelStyle = {'display': 'inline-block'}
                    ),
                    html.H6("Sort Categories"),
                    dcc.Dropdown(
                        id='bsort-category',
                        options = [{'label': i, 'value': i} for i in ['None', 'Alphabetical Ascending', 'Alphabetical Descending', 'Mean Ascending', 'Mean Descending', 'Median Ascending', 'Median Descending']],
                        value = 'None'
                    ),
                    html.H5("Notch Boxes"),
                    dcc.RadioItems(
                        id = 'notched',
                        options = [{'label': i, 'value': i} for i in ['Yes', 'No']],
                        value = 'No',
                        labelStyle = {'display': 'inline-block'}
                    ),
                    html.H5("Include points"),
                    dcc.RadioItems(
                        id = 'bpoints',
                        options = [{'label': i, 'value': i} for i in ['All', 'Outliers', 'None']],
                        value = 'None',
                        labelStyle = {'display': 'inline-block'}
                    )
                ], style={'width': '40%', 'align': 'left', 'display': 'inline-block'}
                ),
                html.Div([
                    dcc.Graph(id='boxplot',
                            config = {'editable': True,
                                      'toImageButtonOptions': {
                                      'format': 'svg',
                                      'height': 480,
                                      'width': 640,
                                      'scale': 2
                                      }
                                     }
                            )
                ], style = {'width': '60%', 'align': 'right', 'display': 'inline-block'})
            ])

         ]),
         # Violinplot tab
         dcc.Tab(label = 'Violinplot', children = [
            html.Div([

                html.Div([
                    html.H5("X-axis column"),
                    dcc.Dropdown(
                        id='vxcol',
                        options=[]
                    ),
                    html.H5("Y-axis column"),
                    dcc.Dropdown(
                        id='vycol',
                        options=[]
                    ),
                    html.H5("Value Column"),
                    dcc.Dropdown(
                        id='vgroup_col',
                        options=[]
                    ),
                    html.H5("Orientation"),
                    dcc.RadioItems(
                        id = 'vorient',
                        options = [{'label': i, 'value': i} for i in ['Vertical', 'Horizontal']],
                        value = 'Vertical',
                        labelStyle = {'display': 'inline-block'}
                    ),
                    html.H5("Sort Categories"),
                    dcc.Dropdown(
                        id='vsort-category',
                        options = [{'label': i, 'value': i} for i in ['None', 'Alphabetical Ascending', 'Alphabetical Descending', 'Mean Ascending', 'Mean Descending', 'Median Ascending', 'Median Descending']],
                        value = 'None'
                    ),
                    html.H5("Include Boxplot"),
                    dcc.RadioItems(
                        id = 'box',
                        options = [{'label': i, 'value': i} for i in ['Yes', 'No']],
                        value = 'No',
                        labelStyle = {'display': 'inline-block'}
                    ),
                    html.H5("Include points"),
                    dcc.RadioItems(
                        id = 'vpoints',
                        options = [{'label': i, 'value': i} for i in ['All', 'Outliers', 'None']],
                        value = 'None',
                        labelStyle = {'display': 'inline-block'}
                    )
                ], style={'width': '40%', 'align': 'left', 'display': 'inline-block'}
                ),

                html.Div([
                    dcc.Graph(id='violinplot',
                            config = {'editable': True,
                                      'toImageButtonOptions': {
                                      'format': 'svg',
                                      'height': 480,
                                      'width': 640,
                                      'scale': 2
                                      }
                                     }
                            )
                ], style = {'width': '60%', 'align': 'right', 'display': 'inline-block'})
            ])

         ])
    ])
])

def parse_data(contents, filename):
    # print(contents)
    # print(filename)
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string).decode('utf-8')
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded)
                )
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Get the proper delimiter
            with io.StringIO(decoded) as f:
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(f.readline())
                f.seek(0)


            # txt files can be either tab-separated or comma-separated
            df = pd.read_csv(
                io.StringIO(decoded), delimiter = dialect.delimiter)#dialect.delimiter)
    except Exception as e:
        #print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    columns = list(df.columns)
    return df, columns

from pandas.api.types import is_object_dtype
def categorize_NAN(df, col):

    if is_object_dtype(df[col]):
        if df[col].isnull().any():
            # Convert to string
            df[col] = df[col].astype(str)

    return df
### Data Table
@app_dash.callback([
             Output("table", "data"),
             Output("table", 'columns')
             ],

             [
             Input("upload-data", 'contents'),
             Input("upload-data", 'filename'),
             Input("edataset", 'value')
             ]
)

def update_datatable(contents, filename, edataset):
    if contents is not None:
        data, cols = parse_data(contents, filename)

        if data is not None:

            columns = [{"name": i, "id": i, 'selectable': True} for i in cols]

            return data.to_dict('rows'), columns
        else:
            return [], []
    else:
        if edataset == 'tips':
            data = px.data.tips()#.to_dict('rows')
            columns = [{"name": i, "id": i, 'selectable': True, "format": Format(precision = 0, scheme = Scheme.fixed)} for i in data.columns]
        elif edataset == 'gapminder':
            data = px.data.gapminder().query("continent == 'Europe'")#.to_dict('rows')
            columns = [{"name": i, "id": i, 'selectable': True} for i in data.columns]
        else:
            data = []
            columns = []


        return data.to_dict('rows'), columns
        #return [], []

### Histogram
@app_dash.callback(Output("histogram-xaxis-column", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_plot_col(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output("histogram-hue-column", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_hue_col(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output('histogram', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('histogram-xaxis-column', 'value'),
                Input('histogram-hue-column', 'value'),
                Input('orient', 'value'),
                Input('normalization', 'value'),
                Input('hnorm', 'value'),
                Input('barmode', 'value'),
                Input('sort-category', 'value'),
                Input('marginal', 'value')
            ])

def update_histogram(contents, filename, xaxis_column_name, hue_col, orient, norm, hnorm, mode, sorting, marginal):

    # Set Orientation
    if orient == 'Vertical':
        orient = 'v'
    else:
        orient = 'h'
    # Set mode
    if mode == 'Stacked':
        mode = 'relative'
    else:
        mode = mode.lower()

    # Set normalization
    if norm == 'None':
        norm = None
    # Set histogram normalization
    if hnorm == 'None':
        hnorm = None
    else:
        hnorm = hnorm.lower()

    # Set category sorting
    category_dict = {'Alphabetical Ascending': 'category ascending',
                    'Alphabetical Descending': 'category descending',
                    'Count Ascending': 'total ascending',
                    'Count Descending': 'total descending',
                    'None': None}

    # Set marginal
    if marginal == 'Yes':
        marginal = 'rug'
    else:
        marginal = None

    if contents:
        contents = contents#[0]
        filename = filename#[0]
        df, available_indicators = parse_data(contents, filename)

    else:

        df = px.data.tips()
        available_indicators = df.columns
        if xaxis_column_name is None:
            xaxis_column_name = 'total_bill'


    if hue_col is not None:
        # Check hue_col for NaN
        df = categorize_NAN(df, hue_col)

        if orient == 'h':
            fig = px.histogram(df,
                        y = xaxis_column_name,
                        color = hue_col,
                        barnorm = norm,
                        histnorm = hnorm,
                        barmode = mode,
                        orientation = orient,
                        marginal = marginal
                        )
        else:
            fig = px.histogram(df,
                        x = xaxis_column_name,
                        color = hue_col,
                        barnorm = norm,
                        histnorm = hnorm,
                        barmode = mode,
                        orientation = orient,
                        marginal = marginal
                        )

    else:
        if orient == 'h':
            fig = px.histogram(df,
                        y = xaxis_column_name,
                        barmode = mode,
                        barnorm = norm,
                        histnorm = hnorm,
                        orientation = orient,
                        marginal = marginal
                        )
        else:
            fig = px.histogram(df,
                        x = xaxis_column_name,
                        barmode = mode,
                        histnorm = hnorm,
                        barnorm = norm,
                        orientation = orient,
                        marginal = marginal
                        )

    # Sort the variables
    if orient == 'v':
        fig.update_xaxes(categoryorder=category_dict[sorting])
    else:
        fig.update_yaxes(categoryorder=category_dict[sorting])
    return fig

### Line plot
@app_dash.callback(Output("crossfilter-xaxis-column", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_xaxis(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.gapminder().query("continent == 'Europe'") # remove Asia for visibility
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output("crossfilter-yaxis-column", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_yaxis(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.gapminder().query("continent == 'Europe'") # remove Asia for visibility
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output("line-hue-column", 'options'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]
            )

def update_hue_col(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.gapminder().query("continent == 'Europe'") # remove Asia for visibility
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output('lineplot', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('crossfilter-xaxis-column', 'value'),
                Input('crossfilter-yaxis-column', 'value'),
                Input('crossfilter-xaxis-type', 'value'),
                Input('crossfilter-yaxis-type', 'value'),
                Input('line-hue-column', 'value')
            ])
def update_lineplot(contents, filename, xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type, hue_col):


    if contents is not None:
        contents = contents#[0]
        filename = filename#[0]
        df, available_indicators = parse_data(contents, filename)

    else:
        df = px.data.gapminder().query("continent == 'Europe'") # remove Asia for visibility
        available_indicators = df.columns

        if xaxis_column_name is None:
            xaxis_column_name = 'year'

        if yaxis_column_name is None:
            yaxis_column_name = 'lifeExp'

    # Sort the values by x-column
    #df.sort_values(by = xaxis_column_name, inplace = True)
    fig = px.line(df,
                x = xaxis_column_name,
                y = yaxis_column_name,
                color = hue_col,
                )

    fig.update_xaxes(title=xaxis_column_name,
                     type='linear' if xaxis_type == 'Linear' else 'log')

    fig.update_yaxes(title=yaxis_column_name,
                     type='linear' if yaxis_type == 'Linear' else 'log')
    return fig

### Scatter Plot
@app_dash.callback(Output("sxcol", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_sxaxis(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output("sycol", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_syaxis(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output("shue_col", 'options'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]
            )

def update_shue_col(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output("ssize_col", 'options'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]
            )

def update_ssize_col(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output("sstyle", 'options'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]
            )

def update_sstyle(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output('scatterplot', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('sxcol', 'value'),
                Input('sycol', 'value'),
                Input('shue_col', 'value'),
                Input('ssize_col', 'value'),
                Input('sstyle', 'value')
            ])
def update_scatter(contents, filename, sxcol, sycol, shue_col, ssize_col, sstyle):

    if contents:
        contents = contents#[0]
        filename = filename#[0]
        df, available_indicators = parse_data(contents, filename)

    else:

        df = px.data.tips()
        available_indicators = df.columns

        if sxcol is None:
            sxcol = 'total_bill'
        if sycol is None:
            sycol = 'tip'

    # Check symbol columns for NaN
    if sstyle is not None:
        df = categorize_NAN(df, sstyle)

    fig = px.scatter(df,
                    x = sxcol,
                    y = sycol,
                    color = shue_col,
                    size = ssize_col,
                    symbol = sstyle
                    )
    #if (shue_col is not None) and (ssize_col is not None):
#        fig = px.scatter(df, x = sxcol, y = sycol, color = shue_col, \
#                        size = ssize_col)
#    elif (shue_col is not None) and (ssize_col is None):
#        fig = px.scatter(df, x = sxcol, y = sycol, color = shue_col)
#    elif (shue_col is None) and (ssize_col is not None):
#        fig = px.scatter(df, x = sxcol, y = sycol, size = ssize_col)
#
#    else:
#        fig = px.scatter(df, x = sxcol, y = sycol)

    return fig

### Heatmap
@app_dash.callback(Output("hxcol", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_hxaxis(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output("hycol", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_hyaxis(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:

        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]
        #return []

@app_dash.callback(Output('heatmap', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('hxcol', 'value'),
                Input('hycol', 'value'),
                Input('colormap', 'value'),
                Input('center', 'value')
            ])
def update_heatmap(contents, filename, hxcol, hycol, colormap, center):

    if contents:
        contents = contents#[0]
        filename = filename#[0]
        df, available_indicators = parse_data(contents, filename)


    else:

        df = px.data.tips()
        available_indicators = df.columns

        if hxcol == None:
            hxcol = 'sex'
        if hycol == None:
            hycol = 'smoker'
        #hxcol = 'sex'
        #hycol = 'smoker'
        #df = pd.DataFrame({"X": [1, 2, 3], "Y": [4, 1, 2]})
        #hxcol = "X"
        #hycol = "Y"
        #value_col = None

    data = pd.crosstab(df[hycol], df[hxcol])

    fig = px.imshow(data,
                labels = dict(x = hxcol, y = hycol),
                x = data.columns, #df[hxcol].sort_values().unique(),
                y = data.index, #df[hycol].sort_values().unique(),
                color_continuous_scale=colormap,
                color_continuous_midpoint=center
                )
    '''
    if (value_col is not None) and (hxcol is not None) and (hycol is not None):

        fig = px.imshow(data,
                        labels = dict(x = hxcol, y = hycol, color = value_col)
                        )
    elif (value_col is None) and (hxcol is not None) and (hycol is not None):

        fig = px.imshow(data)

    else:
        fig = px.imshow(data,
                        labels = dict(x = hxcol, y = hycol)
                        )
    '''
    fig.update_xaxes(side = 'top')
    return fig

### Boxplot
@app_dash.callback(Output("bxcol", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_bxaxis(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output("bycol", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_byaxis(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:

        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output("bgroup_col", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_bgroup_col(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:

        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output('boxplot', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('bxcol', 'value'),
                Input('bycol', 'value'),
                Input('bgroup_col', 'value'),
                Input('borient', 'value'),
                Input('notched', 'value'),
                Input('bsort-category', 'value'),
                Input('bpoints', 'value')
            ])
def update_boxplot(contents, filename, bxcol, bycol, bgroup_col, borient, notched, sorting, bpoints):

    # Set orientation
    if borient == 'Vertical':
        borient = 'v'
    else:
        borient = 'h'

    # Set points value
    if bpoints == 'None':
        bpoints = False
    else:
        bpoints = bpoints.lower()

    # Set category sorting
    category_dict = {'Alphabetical Ascending': 'category ascending',
                    'Alphabetical Descending': 'category descending',
                    'Mean Ascending': 'mean ascending',
                    'Mean Descending': 'mean descending',
                    'Median Ascending': 'median ascending',
                    'Median Descending': 'median descending',
                    'None': None}

    # Set notched
    if notched == 'Yes':
        notched = True
    else:
        notched = False

    # Load dataset
    if contents:
        contents = contents#[0]
        filename = filename#[0]
        df, available_indicators = parse_data(contents, filename)


    else:

        df = px.data.tips()
        available_indicators = df.columns

        if borient == 'h':
            if (bxcol is None) and (bycol is None):
                bxcol = 'total_bill'
        else:
            if (bxcol is None) and (bycol is None):
                bycol = 'total_bill'



    if bxcol is not None:
        if bgroup_col is not None:
            # Check group for NaN
            df = categorize_NAN(df, bgroup_col)
            fig = px.box(df,
                    x = bxcol,
                    y = bycol,
                    color = bgroup_col,
                    orientation = borient,
                    points = bpoints,
                    notched = notched
                    )

        else:
            fig = px.box(df,
                    x = bxcol,
                    y = bycol,
                    orientation = borient,
                    points = bpoints,
                    notched = notched
                    )
    else:
        if bgroup_col is not None:
            # Check group for NaN
            df = categorize_NAN(df, bgroup_col)
            fig = px.box(df,
                    y = bycol,
                    color = bgroup_col,
                    orientation = borient,
                    points = bpoints,
                    notched = notched
                    )
        else:
            fig = px.box(df,
                    y = bycol,
                    orientation = borient,
                    points = bpoints,
                    notched = notched
                    )


    # Sort the variables
    if borient != 'h':
        fig.update_xaxes(categoryorder=category_dict[sorting])
    else:
        fig.update_yaxes(categoryorder=category_dict[sorting])

    return fig

### Violinplot
@app_dash.callback(Output("vxcol", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_vxaxis(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output("vycol", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_vyaxis(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:

        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output("vgroup_col", 'options'),

            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ]

            )
def update_vgroup_col(contents, filename):
    if contents is not None:
        df, columns = parse_data(contents, filename)
        if df is not None:
            return [ {'label': x, 'value': x} for x in columns]
        else:
            return []
    else:
        df = px.data.tips()
        return [ {'label': x, 'value': x} for x in df.columns]

@app_dash.callback(Output('violinplot', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('vxcol', 'value'),
                Input('vycol', 'value'),
                Input('vgroup_col', 'value'),
                Input('box', 'value'),
                Input('vorient', 'value'),
                Input('vsort-category', 'value'),
                Input('vpoints', 'value')
            ])
def update_violinplot(contents, filename, vxcol, vycol, vgroup_col, box, vorient, sorting, vpoints):

    # Add boxplot
    if box == 'Yes':
        box = True
    else:
        box = False
    # Set points
    if vpoints == 'None':
        vpoints = False
    else:
        vpoints = vpoints.lower()
    # Set orientation
    if vorient == 'Vertical':
        vorient = 'v'
    else:
        vorient = 'h'

    # Set category sorting
    category_dict = {'Alphabetical Ascending': 'category ascending',
                    'Alphabetical Descending': 'category descending',
                    'Mean Ascending': 'mean ascending',
                    'Mean Descending': 'mean descending',
                    'Median Ascending': 'median ascending',
                    'Median Descending': 'median descending',
                    'None': None}

    if contents:
        contents = contents#[0]
        filename = filename#[0]
        df, available_indicators = parse_data(contents, filename)


    else:

        df = px.data.tips()
        available_indicators = df.columns

        if vorient == 'h':
            if vxcol == None:
                vxcol = 'total_bill'
        else:
            if vycol == None:
                vycol = 'total_bill'


    if vxcol is not None:
        if vgroup_col is not None:
            # Check group for NaN
            df = categorize_NAN(df, vgroup_col)

            fig = px.violin(df,
                    x = vxcol,
                    y = vycol,
                    color = vgroup_col,
                    box = box,
                    points = vpoints,
                    orientation = vorient
                    )

        else:
            fig = px.violin(df,
                    x = vxcol,
                    y = vycol,
                    box = box,
                    points = vpoints,
                    orientation = vorient
                    )
    else:
        if vgroup_col is not None:
            # Check group for NaN
            df = categorize_NAN(df, vgroup_col)

            fig = px.violin(df,
                    y = vycol,
                    color = vgroup_col,
                    box = box,
                    points = vpoints,
                    orientation = vorient
                    )
        else:
            fig = px.violin(df,
                    y = vycol,
                    box = box,
                    points = vpoints,
                    orientation = vorient
                    )

    # Sort the variables
    if vorient != 'h':
        fig.update_xaxes(categoryorder=category_dict[sorting])
    else:
        fig.update_yaxes(categoryorder=category_dict[sorting])


    return fig


'''
def preview_data():

    file_names = glob.glob(str(UPLOAD_FOLDER) + os.sep + '*.[ct]*')
    short_names = [s.split(os.sep)[-1] for s in file_names]
    file_dict = {short_file: og_name for short_file, og_name in zip(short_names, file_names)}

    #file_names = glob.glob(str(UPLOAD_FOLDER) + os.sep + '*.[ct]*') #glob.glob(UPLOAD_FOLDER + '/*.[ct]*')
    #print(request.form)
    # Get the name of the Database
    src = session.get('source', None)


    if (request.args.get("file_submit") is None) and (request.args.get("feature_submit") is None):
        print("NEITHER BUTTON WAS CLICKED")
        #state = {}
        current_file = file_names[0]

        with open(current_file, 'r') as tf:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(tf.readline())

        dataset = pd.read_csv(current_file, header = 0, sep = dialect.delimiter, na_values = ' ')

        feature_names = list(dataset.columns)

        current_feature = feature_names[0]

        state['cfile'] = current_file

    elif (request.args.get("file_submit") is not None):
        print("FILE SUBMIT WAS CLICKED")
        temp_file = request.args.get("file_name")
        current_file = file_dict[temp_file]#request.args.get("file_name")
        state['cfile'] = current_file

        with open(current_file, 'r') as tf:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(tf.readline())

        dataset = pd.read_csv(current_file, header = 0, sep = dialect.delimiter, na_values = ' ')

        feature_names = list(dataset.columns)

        current_feature = feature_names[0]

    elif (request.args.get("feature_submit") is not None):
        print("FEATURE SUBMIT WAS CLICKED")
        current_file = state['cfile']

        with open(current_file, 'r') as tf:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(tf.readline())

        dataset = pd.read_csv(current_file, header = 0, sep = dialect.delimiter, na_values = ' ')

        feature_names = list(dataset.columns)

        current_feature = request.args.get("feature_name")

    else:
        print("SOMETHING ELSE HAPPENED")

    if src == 'NDA':
        dataset.drop(0, axis = 0, inplace = True)
        #print(current_feature)
    plot = create_histogram(dataset, current_feature)#, bins)

    #controls = WidgetBox(bin_selector)
    #layout = row(controls, plot)
    #tab = Panel(child = layout)
        # Embed plot into HTML
    #if len(plot) == 2:
#        script, div = components(plot[0], plot[1])
#    else:
    script, div = components(plot)

    #script = server_document(base_url + '/preview_data')
    return render_template("preview.html", script = script, div = div, \
                feature_names = feature_names, current_feature = current_feature, \
                file_names = short_names, current_file = current_file)
'''

@app.route("/scrape_NDA", methods = ["POST", "GET"])
def scrape_NDA():
    form = NDAscrapeForm(request.form)
    if form.execute_some.data:#request.method == "POST" and form.validate():
        #datafile = glob.glob("{}/*.[ct]*".format(UPLOAD_FOLDER))[0]
        #with open(datafile, 'w') as fin:
        #    reader = csv.reader(fin)
        #    names = next(reader)

        files = glob.glob(str(UPLOAD_FOLDER) + os.sep + '*.[ct]*')
        logging.info("Executing some...")
        flash("Executing some...")
        scrapeNDA.run_scraping(files)

        logging.info("Scrape complete. Open file in the \'Outputs\' folder")
        flash("Scrape complete. Open file in the \'Outputs\' folder")
        #print("Scraping NDA")
    if form.execute_all.data:
        logging.info("Scraping all of NDA...")
        flash("Scraping all of NDA...")
        scrapeNDAall.main()

        logging.info("Scrape complete. Open file in the \'Outputs\' folder")
        flash("Scrape complete. Open file in the \'Outputs\' folder")

    return render_template("scrape_NDA_template.html", form = form)
    #return

@app.route("/scrape_FITBIR", methods = ["POST", "GET"])
def scrape_FITBIR():
    form = FITBIRscrapeForm(request.form)
    if form.execute_some.data:#request.method == "POST" and form.validate():
        datafiles = glob.glob(str(UPLOAD_FOLDER) + os.sep + '*.[ct]*') #glob.glob("{}/*.[ct]*".format(UPLOAD_FOLDER))[0]
        #print(datafile)
        names = []
        for datafile in datafiles:
            with open(datafile, 'r') as fin:
                reader = csv.reader(fin)
                header = next(reader)
                for h in header:
                    nh = h.split('.')[-1]
                    if nh not in names:
                        names.append(nh)

        #names = [n.split('.')[-1] for n in names]
        names = [n for n in names if n not in ['Study ID', 'Dataset']]
        #names = list(np.unique(names))
        logging.info("Collecting data dictionary...")
        flash("Collecting data dictionary...")
        scrapeFITBIR.main(names)

        logging.info("Scrape complete. Open file in the \'Outputs\' folder")
        flash("Scrape complete. Open file in the \'Outputs\' folder")

    if form.execute_all.data:

        logging.info("Scraping all FITBIR...")
        flash("Scraping all FITBIR...")
        scrapeFITBIRall.scrape_all()

        logging.info("Scrape complete. Open file in the \'Outputs\' folder")
        flash("Scrape complete. Open file in the \'Outputs\' folder")

    return render_template("scrape_fitbir_template.html", form = form)
    #return

# def shutdown_server():
#     func = request.environ.get('werkzeug.server.shutdown')
#     if func is None:
#         raise RuntimeError('Not running with the Werkzeug Server')
#     func()

# @app.route('/shutdown', methods = ['POST', 'GET'])
# def shutdown():
#     form = ShutdownForm(request.form)
#     if form.execute.data:
#         Request.close()
#         # shutdown_server()

#     return render_template("base.html", form = form)

def open_browser():
    webbrowser.open_new_tab(base_url)
    return


'''
if __name__ == '__main__':

    base_url = "http://localhost:5271" #5271
    webbrowser.open_new_tab(base_url)

    # Log errors and print outs
    logger = logging.getLogger('waitress')
    logging.basicConfig(filename='error.log',filemode='w',
                        #format='Date-Time : %(asctime)s : Line No. : %(lineno)d - %(message)s',
                        level=logging.INFO)

    # Add option to shutdown the server
    def run_token_server(q: multiprocessing.Queue) -> None:
        @Request.application
        def rapp(request: Request) -> Response:
            q.put(request.args["token"])
            return Response("", 204)

        serve(TransLogger(run_app.app, setup_console_handler=False), host='localhost', port = 5271)
        #run_simple("localhost", 5000, app)


    def get_token():
        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=run_token_server, args=(q,))
        p.start()
        token = q.get(block=True)
        p.terminate()
        return token
'''
#
#base_url = "http://localhost:5271"

#if __name__ == '__main__':
#    webbrowser.open_new_tab(base_url)
#      #Timer(1, open_browser).start();
#    app.run(port=int(base_url.split(':')[-1]), debug = True)
