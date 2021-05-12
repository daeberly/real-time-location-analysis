#
## Purpose. Convert raw data for raster interpolation & spatial analysis.
#
    # 1. Batch process files from 2 input folders (glob)
    # 2. Merge/Append data & join lat/long on each entry
    # 3. Export result (geopackage, csv & .pkl)
        # Note: merged dataframe is > 1.6 million records.
        # A 10% sample is used in this case study for proof of concept

    # Note. All EPSG set to 3597 (Web Mercator)

## User-input:
    # Folder where to save cleaned data
        # data_clean/csv
        # data_clean/spec
    # Files of interest (i.e. .txt, .spec)

## Outputs:
    # CHECK_buoy_all.svg to verify active reporting wx stations on map
    # splash_down.gpkg with layers 'buoys_all' & 'wx_data'
    # 'cleaned_wx_data.csv'     # 10% sample version
    # 'cleaned_wx_data.pkl.zip' # 10% sample version

## Next .py is 'landing_sites.py'

import pandas as pd
import csv
import os
import glob
import geopandas
import matplotlib.pyplot as plt
import numpy as np

#
# 1. Import multiple files & create dataframes
#

# Steps:
    # create dictionary of new column names 
    # define path for input files
    # loop through each file & append to new Dataframe
 
# create dictionary of old & new column names
mydict = pd.read_csv('NOAA_columns.csv', header=None, index_col=0, squeeze=True).to_dict()
#print(mydict)

#%%

#
# Combine downloaded files into one dataframe
#


## Buoy Data - GENERAL readings

# Path of input files
path = 'data_raw/*.txt'

# Process all files
for file in glob.glob(path):
    print(file)
    n = 0
    
    # Read each file, delete 2nd row & add column w/file name in each row
    #   - Necessary step to create one master dataframe
    with open(file, 'r') as input_file:
        stem = os.path.splitext(os.path.basename(file))[0]
        o_name = stem + '.csv'
#        print(o_name)
        out = open('data_clean/csv/'+ o_name,'w',newline='')
        o_csv = csv.writer(out)
        
        for line in input_file:
            parts = line.split()
            if n == 0:
                o_csv.writerow(['station_id'] + parts)
            elif n > 1:
                o_csv.writerow([stem] + parts)
            n += 1    
        out.close()
        
#        assert False   # stops code after 1 iteration

#%%
# Append files into a Dataframe
buoy_data = pd.DataFrame()

path = 'data_clean/csv/*.csv'

for file in glob.glob(path):
    raw_data = pd.read_csv(file)
    raw_data = raw_data.rename(mydict, axis='columns')
    buoy_data = buoy_data.append(raw_data)
    
# create timestamp for index
buoy_data['timestamp'] = pd.to_datetime(buoy_data[['year', 
                                                     'month',
                                                     'day', 
                                                     'hour',
                                                     'minute']])

print('\n Number of .txt records:', buoy_data.count())
    # Note the lat/long count = 792. Those are the records in latest_obs.txt.
    # These lat/long are used after the data sets are joined
    # and duplicate records are removed since the latest obs for each station
    # is the first observation in each station's record.
    
''' ```` remove when complete'''
buoy_data = buoy_data.sample(frac=.1)
''' ^^^^ remove when complete '''

#%%

## Buoy Data - WAVE SPECIFICS

# Path of input files
path = 'data_raw/spec/*.spec'
out_path = 'data_clean/spec/'

# Process & append each file
for file in glob.glob(path):
    print(file)
    n = 0
    
    with open(file, 'r') as input_file:
        stem = os.path.splitext(os.path.basename(file))[0]
        o_name = stem + '.csv'
#        print(o_name)
        out = open(out_path + o_name,'w',newline='')
        o_csv = csv.writer(out)
        
        for line in input_file:
            parts = line.split()
            if n == 0:
                o_csv.writerow(['station_id'] + parts)
            elif n > 1:
                o_csv.writerow([stem] + parts)
            n += 1    
        out.close()
        
#        assert False   # stops code after 1 iteration
        
# Append files into a Dataframe
spec_data = pd.DataFrame()

for file in glob.glob(out_path + '*.csv'):
    raw_data = pd.read_csv(file)
    raw_data = raw_data.rename(mydict, axis='columns')
    spec_data = spec_data.append(raw_data)

# create timestamp for index
spec_data['timestamp'] = pd.to_datetime(spec_data[['year', 
                                                     'month',
                                                     'day', 
                                                     'hour',
                                                     'minute']])

print('\n Number of .spec records:', spec_data.count())

''' ```` remove when complete'''
spec_data = spec_data.sample(frac=.1)
''' ^^^^ remove when complete '''

#%%
#
# 2.a Create master buoy layer with lat/long 
#

## Master list of buoys with lat/long
buoys_raw = pd.read_csv('data_clean//latest_obs.csv')
buoys_raw = buoys_raw.rename(mydict, axis='columns')
buoys_all = buoys_raw[['station_id','latitude','longitude']]

# Convert DataFrame to GeoDataFrame
buoys_all = geopandas.GeoDataFrame(buoys_all, geometry=geopandas.points_from_xy(buoys_all.longitude,buoys_all.latitude))
buoys_all = buoys_all.set_crs(epsg=3857, inplace= True)     
    # not having inplace= True killed me for hours! haha.
buoys_all.crs

''' 
buoys_all does not project the same as sites, buffers or wx_data
'''
# CHECK. Plot buoy locations
fig,ax1 = plt.subplots(dpi=300, figsize=(12,12))
print('\n buoys_all.crs: ', buoys_all.crs)
buoys_all.plot(ax=ax1, edgecolors= 'black')
plt.title('All NOAA Buoys')
fig.savefig('2a_CHECK_buoy_all.svg', format='svg')


# Export layer to geopackage 
buoys_all.to_file('splash_down.gpkg', layer='buoys_all', driver='GPKG')

#%%

#
# 2.b Merge datasets, attach lat/long & export
#

# Ensure merge column data types are the same
print('\nbuoy_data:\n', buoy_data.dtypes)
print('\nspec_data:\n', buoy_data.dtypes)
print('\nbuoys:\n', buoy_data.dtypes)
convert_type = {'station_id':str}
buoy_data = buoy_data.astype(convert_type)
buoy_data.dtypes
spec_data = spec_data.astype(convert_type)
buoys_all = buoys_all.astype(convert_type)

# Merge data w/same station id & timestamp
merge = pd.merge(buoy_data, spec_data, how='left',on=['station_id', 'timestamp'])

# Attach lat/long to entry, by station
data = pd.merge(merge, buoys_all, how='left',on=['station_id'])

# Look for duplicates
dups = data.duplicated( subset=['station_id','timestamp'], keep=False )
print( '\nduplicate records:', dups.sum() ) 
data = data.drop_duplicates( subset=['station_id','timestamp'] )

# CHECK. Duplicates
dups = data.duplicated( subset=['station_id','timestamp'], keep=False )
print( '\nduplicate records:', dups.sum() ) 

# Keep pertinent data 
keep = ['station_id','timestamp', 'latitude', 'longitude', 
        'wind_spd', 'wind_gust', 'swell_height', 'swell_period',
        'wind_wave_height', 'ave_period_x','steepness']
data = data[ keep ]
fix_names = {'latitude_y':'latitude', 
             'longitude_y':'longitude' , 
             'ave_period_x':'ave_period'}
data = data.rename( fix_names, axis='columns' )


#
## Clean merged data
#

# Replace missing data with None
data = data.replace(to_replace= 'MM' ,value= np.nan)# MM = missing measurement
#data = data.fillna(0)

# Ensure data types are correct for rasterizing
col_name = ['wind_spd','wind_gust', 'swell_height', 'swell_period', 'wind_wave_height', 'ave_period']

for col in col_name:
    data[ col ] = data[ col ].astype('float')

# Convert units
data['wind_spd'] = round(data['wind_spd'] * 1.68781,2)  # convert units: 1 knot = 1.68781 ft/sec

#%%

#
# 3. Export results
#

# Convert to GeoDataFrame 
data = geopandas.GeoDataFrame(data,geometry=geopandas.points_from_xy(data.longitude, data.latitude))
data = data.set_crs(epsg = 3857) # inplace=True?
    # was MISSING this set_crs step

print("\n Exporting 'wx_data':", data.crs)

# Export
data.to_file('splash_down.gpkg', layer='wx_data', driver='GPKG')
data.to_pickle('cleaned_wx_data.pkl.zip')   #.zip auto compresses

print('\n Total:', len(data), 'records in file.')
print('\n Column names:', list(data.columns))
