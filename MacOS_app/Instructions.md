# Instructions on How to Use the Application

## Folder Location
When you download the folder that contains the application, you'll see that it contains an `Inputs` folder, an `Outputs` folder, and the application. The `Inputs` folder is where you put the files you want to merge, transform, analyze, or collect data dictionaries for. You can put as many files as you like here. Note that because NDA, FITBIR, and NIDA files are either text (.txt) files or comma-separated value (CSV) files, the application currently only handles those two formats. The `Outputs` folder is where the results of your analysis or processing are sent. You collect your results here. The application should stay in this folder as is, you don't need to place it somewhere else. In fact, if you place it somewhere else, you're going to get an error when you try to use the application because the application won't be able to find the `Inputs` folder. 

The functions are ordered in the recommended way to explore and process your data.

## Scrape NDA
This option will use the names of the files to get the corresponding data dictionaries from the NDA website. If you choose to collect **all** the data dictionaries, that will take some time so be patient. 

## Scrape FITBIR
This option will use the column names within each file to get the corresponding data dictionaries from the FITBIR website. If you choose to collect **all** the data dictionaries, that will take some time so be patient. 

## Preview Dataset
First, choose which database your file(s) originated. Again, the first row of raw NDA files contains metadata. This metadata needs to be filtered out so that the histograms can be displayed accurately.

Choose the file you want to preview and click "Submit". Choose the feature you want to see and click "Submit". Issues should be reported to the Issues tab.

## Preprocess NDA
This section is the section where you can process the NDA datasets. 

### *Empty columns*
This section removes all columns that have no data in them.

### *Drop columns*
You can choose to drop unnecessary columns such as the ones listed in the application. These columns are duplicates of "collection_id" and "subjectkey".

Additionally, you can remove columns you don't need. An example would be "dataset_id".

### *Missing Value Indicator Columns*
This creates columns of 1's and 0's to indicate if the subject has a value in this column. The default missing data indicator value is an empty string (or an empty cell in Excel). If you want to tell the application that another value indicates missingness, enter that value or a list of values separated by a ‘;’. Examples of other values that indicate missingness are -777, -999, NA, NaN (as a string), etc. 

### *Important Notes*
Because NDA datafiles have the first row of each file as metadata, the script automatically removes them and saves those to separate files in the Outputs folder. 

## Preprocess FITBIR 
This section processes FITBIR datasets for merging and transforming.

### *Split columns*
Splitting the column names means separating the column names by period, so each name will be split into three parts. The option for how many parts of the name to keep tells the application to keep the last n parts. For example, if one part is requested to be kept in the column name “FakeStudy.Info.GUID” , the new column name will be “GUID”. If two parts are requested, the new column name will be “Info.GUID”. If zero or more than 3 parts are requested, the new column name will be “FakeStudy.Info.GUID”. 

### *Empty columns*
This section removes all columns that have no data in them.

### *Drop columns*
This section removes columns you don't want to include. These columns need to be separated by a semi-colon if you have more than one.

### *Missing Value Indicator Columns*
This creates columns of 1's and 0's to indicate if the subject has a value in this column. The default missing data indicator value is an empty string (or an empty cell in Excel). If you want to tell the application that another value indicates missingness, enter that value or a list of values separated by a ‘;’. Examples of other values that indicate missingness are -777, -999, NA, NaN (as a string), etc. 

### *Unflattened CSV files*
When downloading the datasets from FITBIR, users have the option to download the files as “flattened” or “unflattened”. We strongly recommend you default to downloading as “flattened”. This option creates binary variables for each value in the list columns.

If however, you're given an unflattened file, you can handle this in two ways: 

1. Remove them and copy the GUID column and store them in a separate file.  
2. Merge all the cells by group and combine the values in the list column into one string separating values by a ';'.

The "group columns by" columns should be columns that don't have more than one value per row (like the list column). Good example are "GUID;AgeYrs;GeneralNotesTxt", etc.

## Merge & Transform
This section is the big meat of the application. Here, you're able to merge files and convert them from longitudinal format to a wide format in one process. You'll have the option to do these processes separately in other sections.

### *Choose your database*
The first step is to choose which database your data comes from. This step is necessary because in NDA data files, the first row contains the metadata descriptions of the column names. FITBIR and NIDA do not have this metadata. In order to merge and transform the data files properly, the metadata needs to be taken into account.

### *GUID column*
Enter the name of the column that contains the GUIDs, or whatever identification that is used for each row.

### *Time point column*
Enter the name of the column that contains the times each row was measured at. This input is not necessary. If you only have a GUID column, leave this input as 'NA', the default option. If you do have a time column, you should enter it so that the merging is more accurate.

### *Columns to Exclude*
Certain columns do not change over time in the study (i.e. age, gender). Therefore, we found it helpful to exclude these from the transformation from longitudinal to wide format, and merge these at the end. Enter the columns you wish to exclude by listing them as separated by semi-colons such as "age;gender;name".

### *Aggregate Function*
Because there can be multiple rows with different values, you need a method to handle these values. Choosing 'mean', 'median', etc will perform that operation on duplicated rows. 'None' means no aggregation will occur; use 'None' when you know you have one measurement per time.

### *Time Interval between Measurements*
The time interval is the time between measurements in *days*. If you're unsure of how long the time is between measurements, you can use the "Preview Datasets" option on the home page to look at a histogram of the dates in days. If your time column is categorical (i.e. "3-month", "6-month", "12-month"), leave this blank and see the next option.

### *Using the Values in the Time Columns as Data Points*
This option lets you use the values in the column for the new column names. If "No" is selected, the time intervals calculated will be used instead. You should select "No" for NDA files that have dates that look lik "4/13/2000". 

### *Time Points Denotement*
Choose how you want to style the new column names if you chose "No" for the last option.

### *Name for merged file*
Enter what you want the final result file to be called.

## Merge

### *Choose your database*
The first step is to choose which database your data comes from. This step is necessary because in NDA data files, the first row contains the metadata descriptions of the column names. FITBIR and NIDA do not have this metadata. In order to merge and transform the data files properly, the metadata needs to be taken into account.

### *GUID column*
Enter the name of the column that contains the GUIDs, or whatever identification that is used for each row.

### *Time point column*
Enter the name of the column that contains the times each row was measured at. This input is not necessary. If you only have a GUID column, leave this input as 'NA', the default option. If you do have a time column, you should enter it so that the merging is more accurate.

### *Name for merged file*
Enter what you want the final result file to be called.

## Transform
You should only be transforming a single file here. If you have multiple files, merge them first if they can be merged.

### *Choose your database*
The first step is to choose which database your data comes from. This step is necessary because in NDA data files, the first row contains the metadata descriptions of the column names. FITBIR and NIDA do not have this metadata. In order to transform the data files properly, the metadata needs to be taken into account.

### *GUID column*
Enter the name of the column that contains the GUIDs, or whatever identification that is used for each row.

### *Time point column*
Enter the name of the column that contains the times each row was measured at. This input is necessary. The application uses this column to group rows.

### *Columns to Exclude*
Certain columns do not change over time in the study (i.e. age, gender). Therefore, we found it helpful to exclude these from the transformation from longitudinal to wide format, and add these back in at the end. Enter the columns you wish to exclude by listing them as separated by semi-colons such as "age;gender;name".

### *Aggregate Function*
Because there can be multiple rows with different values, you need a method to handle these values. Choosing 'mean', 'median', etc will perform that operation on duplicated rows. 'None' means no aggregation will occur; use 'None' when you want to concatenate files upon each other or you have no need to aggregate your data.

### *Time Interval between Measurements*
The time interval is the time between measurements in *days*. If you're unsure of how long the time is between measurements, you can use the "Preview Datasets" option on the home page to look at a histogram of the dates in days. If your time column is categorical (i.e. "3-month", "6-month", "12-month"), leave this blank and see the next option.

### *Using the Values in the Time Columns as Data Points*
This option lets you use the values in the column for the new column names. If "No" is selected, the tiem intervals calculated will be used instead.

### *Time Points Denotement*
Choose how you want to style the new column names if you chose "No" for the last option.

### *Name for merged file*
Enter what you want the final result file to be called.


## Get Stats
Enter the name of the file you want to collect descriptive statistics on.

The current statistics returned for each column in your dataset are: 

  - Name
  - Percent of missing data in column (out of 100)
  - Number of unique values in the column
  - Mean\*
  - Median\*
  - Mode 
  - Min\*
  - Max\*
  - Variance\*
  - Standard Deviation\*
  - 5th percentile\*
  - 95th percentile\*
  - Skewness\*
  - Kurtosis\*
  - Value Range (if the column has more than 10 unique values, "Element has more than 10 unique values" is returned)
  
\* (returns `nan` for categorical variables)
Suggestions for additional useful statistics to include can be made by opening a New Issue and prefixing your issue with "Statistics Request"

The resultant file is put in the `Outputs` folder. Note that stats files are automatically output for the datasets created using the **Merge** section. 


