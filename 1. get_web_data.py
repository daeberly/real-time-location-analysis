#
## Purpose
#
    # 1. Download real-time data files - 10 min reporting interval last 72 hrs
    # 2. Save to folder for processing 

## Next .py is 'clean_input_data.py'

## User-input:
    # Supply url
    # Folder where to save & 
    # File of interest (i.e. .txt, .spec)

import pandas as pd
import urllib      # download from a specific web file 
#pip install wget  # use this to add wget (first time only)
import wget        # batch download web files 
import glob
import os
import csv

#%%
##
##  Part 1. Get create from web a master list of 'current' weather stations
##


#
# Get file from web with all buoys and respective lat&long (.txt)
#

response = urllib.request.urlopen(' https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt ')
data = response.read()
filename = 'latest_obs.txt'
fh = open(filename, 'wb')
fh.write(data)
fh.close()

#%%

#
# Create master list for wget to download currently reporting stations
# 

path = filename

# Blank dataframe to append all .spec files
buoy_data = pd.DataFrame()

for file in glob.glob(path):
    print(file)
    n = 0
    
    # Read file, delete 2nd row & add column w/file name
    
    with open(file, 'r') as input_file:
        stem = os.path.splitext(os.path.basename(file))[0]
        o_name = stem + '.csv'
        print(o_name)
        out = open('data_clean/'+ o_name,'w',newline='')
        o_csv = csv.writer(out)
        
        for line in input_file:
            parts = line.split()        # similar to deliminator, but cooler
            if n == 0:
                o_csv.writerow(parts)
            elif n > 1:                 # skip 2nd row with units of measure
                o_csv.writerow(parts)
            n += 1    
        out.close()
        
#%%

##
##  Part 2. Download data files.
##

## Two data files per weather reporting station 
    # general info "'station id'.txt" (i.e. time, wind, swells)
    # wave specifics "'station id'.spec" (i.e. wave height, steepness, period)
    

# Create master list [] of stations for wget to download
stations = pd.read_csv('data_clean//latest_obs.csv', dtype=(str), usecols=[0])

''' sample used for proof of concept '''
stations = stations.sample(frac=.2)
stations = stations['#STN'].to_list()

#%%

#
# Download all 'general info .txt' files in repository
#
no_csv_data = []

for station in stations:
    try:
        url = 'https://www.ndbc.noaa.gov/data/realtime2/'
        file_type = '.txt'
        payload= url + station + file_type
        wget.download(payload, out= 'data_raw/')  # saves specified to folder
    
    except:
        no_csv_data.append(station)
    
#    assert False       # stops for loop after 1 interation
    
# Export missing station report
print('\n Stations missing .csv files:', len(no_csv_data))
missing_csv = pd.DataFrame(no_csv_data)
missing_csv = missing_csv.rename({0:'station_id'}, axis= 'columns')
missing_csv.to_csv('stations_missing_.csv', index=False)

#%%

#
# Download all 'wave specific info .spec' files in repository
#
no_spec_data = []

for station in stations:
    try:
        url = 'https://www.ndbc.noaa.gov/data/realtime2/'
        file_type = '.spec'
        payload= url + station + file_type
        wget.download(payload, out= 'data_raw/spec/')
    except:
        no_spec_data.append(station)

#    assert False

# Export report of missing stations
print('\n Stations missing .spec files:', len(no_spec_data))
missing_spec = pd.DataFrame(no_spec_data)
missing_spec = missing_spec.rename({0:'station_id'}, axis= 'columns')
missing_spec.to_csv('stations_missing_.spec', index=False)

print("Download Complete: Great success!")
