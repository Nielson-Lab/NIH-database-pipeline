#!/usr/bin/env python3

"""
# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

Description: This module serves the application. This file is run when the application is opened and created using PyInstaller

"""

from gevent.pywsgi import WSGIServer
import run_app
import webbrowser
import logging
from paste.translogger import TransLogger

### Define function to specify the path to the log file ###
from pathlib import Path
from appdirs import *

appname = "NFP"
appauthor = "tkirsh"

log_dir = Path(user_log_dir(appname, appauthor))
# Check that the directory exists, otherwise create it
log_dir.mkdir(parents=True, exist_ok=True)

# Create path to the file
log_path = Path(log_dir, 'error.log')
###########################################################

host = 'localhost'
port = 5271

base_url = f"http://{host}:{port}" #"http://localhost:5271"
webbrowser.open_new_tab(base_url)

# Log errors and print outs
logger = logging.getLogger('gevent')
logging.basicConfig(filename=log_path,
                    filemode='w',
                    #format='Date-Time : %(asctime)s : Line No. : %(lineno)d - %(message)s',
                    level=logging.INFO)

logging.info(log_path)

my_app = run_app.app

http_server = WSGIServer((host, port), my_app)
http_server.serve_forever()
