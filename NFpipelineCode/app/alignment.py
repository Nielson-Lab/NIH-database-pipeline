"""
# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

DESCRIPTION: This script creates the data element alignment database that is used to convert datasets from NDA
scales and names to FITBIR scales and names, and vice versa. It uses the "alignment_table_first_element_test_condition.csv"
file found in the repository. This file should be updated periodically to reflect changes to the NDA and FITBIR databases.

"""

import csv
import sqlite3

filename = "alignment_table_first_element_test_condition.csv"
# Get column names
with open(filename, 'r') as fin:
    csvreader = csv.reader(fin)
    # Get just the first row, which should hold the column names
    columns = next(csvreader)

# Create table and database if the table does not exist
con = sqlite3.connect("aligned_first_element.db") # name the database something appropriate
cur = con.cursor()

col_tuple = tuple([col + ' TEXT' for col in columns]) #tuple(columns) #
# Create the table, removing the previous table if it exists (done to update results)
schema1 = '''DROP TABLE IF EXISTS alignment; '''
schema2 = f'''CREATE TABLE IF NOT EXISTS alignment {col_tuple};'''
# Remove quotes from schema2
schema2 = schema2.replace("'", "")

# Exceute the schemas to create the database
cur.execute(schema1)
cur.execute(schema2)

with open(filename, 'r', encoding='utf-8-sig') as f:

    reader = csv.DictReader(f)

    to_database = [tuple(map(lambda x: row[x], columns),) for row in reader]
    #to_database = [(i['NDA Element Name'], i['FITBIR Element Name'], i['NDA Form'], i['FITBIR Form']) for i in reader]

qmark_tuple = tuple(['?']*len(col_tuple))

# Insert the GUID and interview_date conversions into the database
cur.execute('''INSERT INTO alignment(NDA_Element, FITBIR_Element) VALUES(?,?)''', ('subjectkey', 'GUID'))
cur.execute('''INSERT INTO alignment(NDA_Element, FITBIR_Element) VALUES(?,?)''', ('interview_date', 'VisitDate'))
# Insert the other conversions
schema_many = f"""INSERT INTO alignment{tuple(columns)} VALUES{qmark_tuple};""" # "INSERT INTO alignment (NDA_Element, FITBIR_Element, NDA_Form, FITBIR_Form) VALUES (?, ?, ?, ?);"
schema_many = schema_many.replace("'", "")


#for row in to_database:
#    cur.execute(schema_many, row)
cur.executemany(schema_many, to_database)

con.commit()
con.close()
