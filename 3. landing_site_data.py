#
# Purpose: Find sites, create buffers & nearest stations for spatial analysis
#
'''
    # 1. Batch process files from 2 input folders (glob)
    # 2. Merge/Append data & join lat/long on each entry
    # 3. Export result (geopackage, csv & .pkl)
        # Note: merged dataframe is > 1.6 million records.
        # A 10% sample is used in this case study for proof of concept

## User-input:
    # Folder where to save cleaned data
        # data_clean/csv
        # data_clean/spec
    # Files of interest (i.e. .txt, .spec)

## Outputs:
    # CHECK_buoy_all.svg to verify active reporting wx stations on map
    # splash_down.gpkg with layers:
        'sites',                   # All active buoys
        'buoy_selection_rings',    # Buffer rings around NASA sites
        'nearby_wx_stations'       # buoys w/in the buffer rings
        
    # 'cleaned_wx_data.csv'     # 10% sample version
    # 'cleaned_wx_data.pkl.zip' # 10% sample version

## Next .py is 'landing_sites.py'

 To fix:
    - Select weather reporting sites w/in 100nm of splashdown sites 
    - Nice to clean up - join overlapping rings into one buffer
        - Attemped on line 105 but can't set it to a coordinate reference system'
    
'''
    
# Note: contextily & folium are not automatic Anaconda modules
    # To add, (1) Open Anacoda Command Window, (2) enter commands below
    # `conda install contextily -c conda-forge`
    
import geopandas
import fiona                # driver to read .kml format
import matplotlib.pyplot as plt
import contextily as ctx    # basemape for figure plots

#%%
#
# NASA/SpaceX splashdown sites
#

'''
# .kml to GeoDataFrame
geopandas.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
sites = geopandas.read_file('splashdown_sites.kml', driver='KML')
sites = sites.to_crs(epsg=3857)
sites.crs
#  Clean attribute table
sites = sites.set_index('Name')
sites['state'] = 'FL'
sites = sites.drop(columns='Description')


'''

## Input .csv of active buoys with lat/long
sites = pd.read_csv('NASA_sites.csv')

# Convert DataFrame to GeoDataFrame
sites = geopandas.GeoDataFrame(sites, geometry=geopandas.points_from_xy(sites.latitude,sites.longitude))
sites = sites.set_index('Name')
sites = sites.set_crs(epsg=3857, inplace= True) # EPSG:3857 for basemap
    # not having inplace= True killed me for hours! haha.
sites.crs

## CHECK Start - plot results on a map

# Plot results
fig,ax1 = plt.subplots(dpi=300, figsize=(12,12))
print('\nsites.crs: ',sites.crs)
sites.plot(ax=ax1, edgecolors='black')

# Basemap options:
#ctx.providers.keys()
#ctx.providers.Esri.keys()
ctx.add_basemap(ax=ax1, source=ctx.providers.Esri.OceanBasemap, zoom=10)

# Annotate Figure
plt.title('NASA/SpaceX Splashdown Sites')
# Label each lat/long point
for x, y, label in zip(sites.geometry.x, sites.geometry.y, sites.index):
    ax1.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")
    # code reference: https://matplotlib.org/stable/tutorials/text/annotations.html#plotting-guide-annotation

# CHECK End

# Export: 
fig.savefig('CHECK_sites_shapefile.png', format='png')
sites.to_file('splash_down.gpkg', layer='NASA_sites', driver='GPKG')

#%%
#
# Create 150nm site buffer, buoy selection
#

''' fix units'''


# Buffer: 150 nautical miles = 277800 meters (crs)
sites.crs
site_buffers = sites.buffer( 2 ) 
site_buffers.crs
site_buffers = site_buffers.to_crs(epsg=3857)


## CHECK Start - plot results on a map

fig,ax1 = plt.subplots(dpi=300, figsize=(12,12))
print('\n site_buffers.crs: ',site_buffers.crs)

# Plot rings & sites
site_buffers.plot(ax=ax1, color='grey', alpha= 0.6)
sites.plot(ax=ax1, edgecolors='red')
ctx.add_basemap(ax=ax1, source=ctx.providers.Esri.OceanBasemap, zoom=10)

## Annotate Figure
plt.title('NASA/SpaceX Splashdown Sites, 150nm buffer')
for x, y, label in zip(sites.geometry.x, sites.geometry.y, sites.index):
    ax1.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")    
fig.savefig('CHECK_buoy_selection_rings.svg', format='svg')

## CHECK End

# Export: add new layer to geopackage 
site_buffers.to_file('splash_down.gpkg', layer='buoy_selection_rings', driver='GPKG')


#%%

#
# Select NOAA buoys within 150nm of sites
#

# Import buoys from geopackage.
points = geopandas.read_file('splash_down.gpkg', layer='buoys_all')
points.crs
points = points.to_crs(epsg=3857)
    # CHECK 
fig,ax1 = plt.subplots(dpi=300, figsize=(12,12))
print('\n points.crs: ', points.crs)
points.plot(ax=ax1, edgecolors= 'black')

# Confirm buffers crs matches points.
site_buffers = geopandas.read_file('splash_down.gpkg', layer='buoy_selection_rings')
site_buffers.crs
site_buffers = site_buffers.to_crs(epsg=3857)

# CHECK: plot both together
fig,ax1 = plt.subplots(dpi=300, figsize=(12,12))
points.plot(ax=ax1, facecolor='none', edgecolors= 'black', markersize=5)
site_buffers.plot(ax=ax1, alpha= 0.2, facecolor='red', edgecolors= 'none', markersize=50 )
fig.savefig('CHECK_buoys_&_selection_rings.svg', format='svg')

#%%
# Select buoys within buffers

in_buffer = geopandas.overlay(site_buffers, points, how='intersection', keep_geom_type=False)
   # Ref: https://geopandas.org/docs/user_guide/set_operations.html
   
# CHECK: selection & buffers plot both together
fig,ax1 = plt.subplots(dpi=300, figsize=(12,12))
in_buffer.plot(ax=ax1, facecolor='none', edgecolors= 'black', markersize=5)
site_buffers.plot(ax=ax1, alpha= 0.2, facecolor='red', edgecolors= 'none', markersize=50 )
fig.savefig('buoys_inBuffer.svg', format='svg')

# Export: add new layer to geopackage 
site_buffers.to_file('splash_down.gpkg', layer='nearby_wx_stations', driver='GPKG')

