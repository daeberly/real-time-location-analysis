#
# Sites Evaluation
# 

import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import seaborn as sns
import fiona

#%%

# List all layers within a geopackage
for layername in fiona.listlayers('splash_down.gpkg'):
    with fiona.open('splash_down.gpkg', layer=layername) as src:
        print('layer name:', layername, '|| records:', len(src))
        
    # Ref: https://fiona.readthedocs.io/en/latest/README.html#reading-multilayer-data
    
#%%%

#
# Number of weather stations per site
#

nearby = geopandas.read_file('splash_down.gpkg', layer='nearby_wx_stations')
nearby.crs

per_site = nearby.value_counts('Name')

# Plot Bar Chart

fig, ax1 = plt.subplots(dpi=300)
fig.subplots_adjust(left=0.25)
ax = per_site.plot.barh()
ax.set_ylabel('Splashdown Site')
ax.set_xlabel('NOAA Stations within 120nm')
ax.set_title('Nearby Active NOAA Weather Stations')
ax.tick_params(axis='y', rotation= 40)

fig.savefig('4a_WxStations_per_site.svg', format='svg')



#%%

#
#   Join & pull last 72 hr weather reports from stations in buffer
#

# Read in data
wx = pd.read_pickle( 'cleaned_wx_data.pkl.zip' )
wx.columns
wx.shape

nearby.columns
nearby.shape

# Combine both databases
nearby_wx = nearby.merge(wx, 
                      on="station_id", 
                      how='inner', 
                      validate='m:m', 
                      indicator=True)
print('\nResult of Inner Join:', nearby_wx.value_counts('_merge'))
print(nearby_wx.columns)

# Remove unnecessary columns
nearby_wx = nearby_wx.drop(['_merge','latitude_x', 'longitude_x', 'geometry_x'], axis='columns')
fix_names = {'latitude_y':'latitude', 
             'longitude_y':'longitude' , 
             'geometry_y':'geometry'}
nearby_wx = nearby_wx.rename( fix_names, axis='columns' )
print(nearby_wx.columns)

# Set index for groupby
#nearby_wx = nearby_wx.set_index(['station_id', 'timestamp'])

# Add wind speed & swell bins
nearby_wx ['wind_bin'] = round(nearby_wx ['wind_spd'])
print('\nResults of wind_bin (ft/sec):', nearby_wx.value_counts('wind_bin'))

nearby_wx ['wave_ht_bin'] = round(nearby_wx ['wind_wave_height'],2)
print('\nResults of wave_ht (ft):', nearby_wx.value_counts('wave_ht_bin'))

nearby_wx.sample(10)

#
# By Timestamp per location, wind and waves last 72 hours
#

# Group by datetime & site, wind
by_site_wind = nearby_wx.groupby([nearby_wx['timestamp'], 'Name'])['wind_bin'].mean()
by_site_wind = by_site_wind.to_frame()

# Group by datetime & site, wave height
by_site_waveHt = nearby_wx.groupby([nearby_wx['timestamp'], 'Name'])['wave_ht_bin'].mean()
by_site_waveHt = by_site_waveHt.to_frame()

# Combine (merge) both databases
by_timestamp = by_site_wind.merge(by_site_waveHt, 
                      on=['timestamp','Name'], 
                      how='inner', 
                      validate='1:1', 
                      indicator=True)
# CHECK
print('\nResult of Inner Join:', by_timestamp.value_counts('_merge'))
by_timestamp = by_timestamp.drop(['_merge'], axis='columns')


#%%

#
# Plots
#


#
# Violin. Location with wind & wave
#

#   Reference: https://seaborn.pydata.org/generated/seaborn.violinplot.html
#              https://datavizpyr.com/how-to-make-violinpot-with-data-points-in-seaborn/

fig, ax1 = plt.subplots()
sns.set_context('paper') # quality of output

ax1 = sns.violinplot(y='wind_bin', x='Name',data= nearby_wx)
fig.suptitle('Previous 72 hours, wind')
ax1.set_ylabel('ft/sec')
ax1.set_xlabel('Splashdown Site')
ax1.tick_params(axis='x', rotation= 20)
ax1.axhline(15)
fig.tight_layout()
fig.savefig("4b_wind_byLocation_violinplot.png", format='png',dpi=300)

#
# BoxenPlot. Location with wind & wave
#

fig, ax1 = plt.subplots()
sns.set_context('paper') # quality of output
ax1 = sns.boxenplot(y='wave_ht_bin', x='Name',data= nearby_wx)
    # usage = Y variable
    # by= = X variable
    # ax=ax1 - put the graph on ax1
    # grid=False - no grid lines
fig.suptitle('Previous 72 hours, swell height')
ax1.set_ylabel('feet')
ax1.set_xlabel('Splashdown Site')
ax1.tick_params(axis='x', rotation= 20)
fig.tight_layout()
fig.savefig("4c_wave_byLocation_boxenplot.png", format='png',dpi=300)


#%%

#
# Timeseries plot of 72 hours
#

#All Data

# hourly timestamp 
by_time = by_timestamp.sample(frac= 1)

# Wind, by location
fig, ax1 = plt.subplots()
fig.suptitle('Previous 72 hours, average wind by site')
ax1.set_title('All 1.6 million records')
sns.set_context('paper') # quality of output
ax1.axhline(15)
ax1 = by_time.groupby('Name')['wind_bin'].plot(legend=True)
plt.legend(loc='upper left', prop={'size':6})
fig.tight_layout()
fig.savefig("4d_timeseries_wind_byLocation.png", format='png',dpi=300)

#Sample #1

# hourly timestamp 
by_time = by_timestamp.sample(frac= 0.1)

# Wind, by location
fig, ax1 = plt.subplots()
fig.suptitle('Previous 72 hours, average wind by site')
ax1.set_title('Sample #1 - 10% of 1.6 million records')
sns.set_context('paper') # quality of output
ax1.axhline(15)
ax1 = by_time.groupby('Name')['wind_bin'].plot(legend='left')
plt.legend(loc='upper left', prop={'size':6})
fig.tight_layout()
fig.savefig("4e_timeseries_wind_byLocation.png", format='png',dpi=300)

## Sample #2

# hourly timestamp 
by_time = by_timestamp.sample(frac= 0.1)

# Wind, by location
fig, ax1 = plt.subplots()
fig.suptitle('Previous 72 hours, average wind by site')
ax1.set_title('Sample #2 - 10% of 1.6 million records')
sns.set_context('paper') # quality of output
ax1.axhline(15)
ax1 = by_time.groupby('Name')['wind_bin'].plot(legend=True)
plt.legend(loc='upper left', prop={'size':6})
fig.tight_layout()
fig.savefig("4f_timeseries_wind_byLocation.png", format='png',dpi=300)



#%%
''' Incomplete. Unable to correct in time...
    # ValueError: setting an array element with a sequence.
    
# Timeseries Decomposition plot (1 column, 4 rows)
     # 1. line plot, 
     # 2. smoothed trend line
     # 3. Seasonality, by hour, day (i.e. day vs. night)
     # 4. Residual plot
     
from statsmodels.tsa.seasonal import seasonal_decompose
from dateutil.parser import parse


# Example Station
buoy_42036 = wx.groupby("station_id")

# Seasonal (day/night) variation 
result = seasonal_decompose(buoy_42036['wind_spd'], model='multiplicative')

# Plot
plt.rcParams.update({'figure.figsize': (10,10)})
result.plot().suptitle('Time Series of NOAA station:', str(buoy_42036))
plt.show()

'''
 

#%%

#
# Final Plot. Map NOAA & CG sites, 12nm Territorial sea applied in QGIS
#

    # location & range of small boat stations nearby
    # District & sector AORs

    # Data Source: https://coast.noaa.gov/htdata/Shoreline/us_medium_shoreline.zip
    # Altn:https://nauticalcharts.noaa.gov/data/us-maritime-limits-and-boundaries.html#access-digital-data
 
# Basemap layers

    # States polygons
states = geopandas.read_file('cb_2018_us_state_500k.zip')
states.plot()
 
    # 12nm Territorial Sea
territorial_sea = geopandas.read_file('US_Maritime_Limits_Boundaries_Map_Service_Layer.zip')
        # https://hub.arcgis.com/datasets/44f58c599b1e4f7192df9d4d10b7ddcf_1?geometry=-161.895%2C-12.805%2C161.895%2C73.355
territorial_sea.plot()
   
    # NASA/SpaceX Sites
sites = geopandas.read_file('splash_down.gpkg', layer='NASA_sites')
sites = sites.set_index('Name')
sites.plot()


#
#  CG 1hr transit time
# 

# Created GeoDataFrame from .csv
CG_units_raw = pd.read_csv('CG_units.csv')
CG_units = geopandas.GeoDataFrame(CG_units_raw, geometry=geopandas.points_from_xy(CG_units_raw.Longitude,CG_units_raw.Latitude))
CG_units = CG_units.set_crs(epsg=3857, inplace= True)     
CG_units.crs
CG_units = CG_units.set_index("Unit")

# Calculate & Create 1hr CG response range
CG_units['1hr_resp'] = CG_units['Transit_Spd']*.05
CG_buff = CG_units.buffer( CG_units['1hr_resp'] )
 
# Convert to Dataframe, for clipping with state polygons
CG_buff = CG_buff.to_frame()
    # Convert to GeoDataFrame, for overlay module 
CG_buffer = geopandas.GeoDataFrame(CG_buff, crs=3857,geometry= CG_buff[ 0 ] )
    # Remove any buffer over land
CG_buffer = geopandas.overlay(CG_buff, states, how='difference')
CG_buffer.plot()
#%%
## CHECK Start - plot results on a map

fig,ax1 = plt.subplots(dpi=300, figsize=(12,12))
plt.title('NASA/SpaceX Splashdown Sites vs USCG 1-hr range')

    # Zoom into Continential US Area of Interest
xlim = ([CG_buffer.total_bounds[0],  CG_buffer.total_bounds[2]])
ylim = ([CG_buffer.total_bounds[1],  CG_buffer.total_bounds[3]])

ax1.set_xlim(xlim)
ax1.set_ylim(ylim)

    # Stack layers
CG_units.plot(ax=ax1, alpha= 0.9, facecolor='lightskyblue', edgecolors= 'blue', markersize=75)
CG_buffer.plot(ax=ax1, alpha= 0.2, facecolor='lightskyblue', edgecolors= 'none', markersize=50 )

sites.plot(ax=ax1, alpha= 0.9, facecolor='red', edgecolors= 'red', markersize=100)
territorial_sea.plot(ax=ax1, alpha= 0.8)
states.plot(ax=ax1, alpha= 0.2, facecolor='whitesmoke', edgecolors= 'grey', hatch= '///', markersize=50)
        # Color options: https://matplotlib.org/stable/gallery/color/named_colors.html

    # Annotate figure
for x, y, label in zip(sites.geometry.x, sites.geometry.y, sites.index):
    ax1.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")    

for x, y, label in zip(CG_units.geometry.x, CG_units.geometry.y, CG_units.index):
    ax1.annotate(label, xy=(x, y), xytext=(1, 1), textcoords="offset points", size= 5)

# Export 
fig.savefig('4g_SpaceXsites_vs-USCG.png', format='png')
CG_units.to_file('splash_down.gpkg', layer='CG_units', driver='GPKG')
