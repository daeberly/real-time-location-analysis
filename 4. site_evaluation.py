#
# Sites Evaluation
# 





import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import seaborn as sns


#%%%

#
# Number of weather stations per site
#

nearby = geopandas.read_file('splash_down.gpkg', layer='nearby_wx_stations')
nearby.crs

per_site = nearby.value_counts('Name')

# Plot Bar Chart

fig, ax1 = plt.subplots(dpi=300)
plt.figure(dpi=300)
ax = per_site.plot.barh()
ax.set_ylabel('Splashdown Site')
ax.set_xlabel('NOAA Stations within 120nm')
ax.set_title('Nearby Active NOAA Weather Stations')

fig.savefig('WxStations_per_site.png', format='png')



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
ax1.axhline(15)
fig.suptitle('Previous 72 hours, wind')
ax1.set_ylabel('ft/sec')
ax1.set_xlabel('Splashdown Site Area')
ax1.tick_params(axis='x', rotation= 20)
fig.tight_layout()
fig.savefig("wind_byLocation_violinplot.png", format='png',dpi=300)

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
ax1.set_xlabel('Splashdown Site Area')
ax1.tick_params(axis='x', rotation= 20)
fig.tight_layout()
fig.savefig("wave_byLocation_boxplot.png", format='png',dpi=300)


#%%

#
# Timeseries plot of 72 hours
#


# hourly timestamp 
by_time = by_timestamp.sample(frac= 0.02)

# Wind, by location
fig, ax1 = plt.subplots()
sns.set_context('paper') # quality of output
ax1.axhline(15)
ax1 = by_time.groupby('Name')['wind_bin'].plot(legend=True)
fig.suptitle('Previous 72 hours, average wind by site')
fig.tight_layout()
fig.savefig("wave_byLocation_boxplot.png", format='png',dpi=300)



#%%










