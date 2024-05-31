# NFpipeline - DEVELOPERS ONLY
This is the source code for the NFP (NDA-FITBIR pipeline) application.

This repository was developed with funding from the National Institute of Mental Health (NIMH), grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota. ©2024 Regents of the University of Minnesota. All rights reserved.

This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):(https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)


### Requirements
---
Python 3.8 or later (Python 2 will be deprecated starting January 1st, 2020), python-pip, virtualenv

### How to Create a New Release of the Application
---

Download the app by **forking** the repository.

```
$ cd NFpipelineCode
```

The application was built with Python 3.8.8 and currently works with that version. On Windows, you will need to install `virtualenv` and `Python` if you don't already have them on your computer. Specify the Python version when creating the virtual environment. Create a virtualenv and activate it

```
$ virtualenv venv
$ source venv/bin/activate --> MacOS
$ source venv/Scripts/activate --> Windows
```
If you have Anaconda or see `(base) (venv) username@computer NFpipelineCode $` you need to deactivate Anaconda

```
$ conda deactivate
```

Install the necessary requirements. NOTE: If on Windows you cannot install `lxml`, change the version to `lxml=5.2.2`.

```
$ pip3 install -r requirements.txt
```

If you need to update the alignment database, use the data file `"alignment_table_first_element_test_condition.csv"`. To create a new database, run the alignment Python file. Be sure to change the "filename" path first.

```
python alignment.py
```

Once the new "alignment_first_element.db" is created, transfer it to the "database" directory in "app". If the subdirectory "database" does not exist in "app", create it and then move the database there; Pyinstaller will look for the database in that directory.

The "waitress" package was used in the past to serve the application. I switched to "gevent" because it can handle larger applications better. The file to serve the application is `run_gevent.py`.

Once you're ready to create the new application executable, choose `"run_pyinstaller.sh"` if you're on MacOS, or `"run_pyinstaller_windows.sh"` if you're on Windows. Open the shell script and update the path to Python to match `/path/to/NFpipeline/venv/lib/python3.8/site-packages`.

```
./run_pyinstaller.sh --> Mac
./run_pyinstaller_windows.sh --> Windows
```

The new application will be located in the "dist" folder inside "app". You can move it out into a new "MacOS_app" or "Windows_app" folder. Add the Inputs with the sample datasets folder (use from last release) and the *empty* Outputs folder. Also include the latest version of the Manual PDF.

Then make sure you're signed in and create a new Release. Include updates about your OS, features, and fixed bugs.

### Pro Tips

1. This application is designed to make working with NDA and FITBIR data easier. However,
you can also use it to make merging other text files easier. If you have data files
from another database and you want to merge them, you can use this application to do so. If your files do not have the first row filled with metadata (like NDA), select FITBIR when merging or transforming.

2. The file from the stats page and the data dictionary can be merged to create
a full data dictionary by putting these files into the Inputs folder, changing the
Variable column to the same name, and running the Merge page.


### Issues
---

If you have any problems or suggestions for this app, please create a new issue using the "Issues" tab at the top of the page.
