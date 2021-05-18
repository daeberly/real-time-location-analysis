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
    # Landing sites as .csv 
    # Files of interest (i.e. .txt, .spec)

## Outputs:
    # CHECK_buoy_all.svg to verify active reporting wx stations on map
    # splash_down.gpkg with layers:
        'sites',                   # All active buoys
        'buoy_selection_rings',    # Buffer rings around NASA sites
        'nearby_wx_stations'       # buoys w/in the buffer rings
        
## Next .py is 'Evaluation.py'


'''
    
# Note: contextily & folium are not automatic Anaconda modules
    # To add, (1) Open Anacoda Command Window, (2) enter commands below
    # `conda install contextily -c conda-forge`
    
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import fiona

#%%
#
# NASA/SpaceX splashdown sites
#

''' Attempt at converting .kml, CRS
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
print('\nsites.crs: ',sites.crs)

## CHECK Start - plot results on a map

    # Basemap layer - U.S. States
states = geopandas.read_file('cb_2018_us_state_500k.zip')

fig,ax1 = plt.subplots(dpi=300, figsize=(12,12))

    # Zoom into Continential US Area of Interest
xlim = ([sites.total_bounds[0],  sites.total_bounds[2]])
ylim = ([sites.total_bounds[1],  sites.total_bounds[3]])

ax1.set_xlim(xlim)
ax1.set_ylim(ylim)

    # Stack layers
sites.plot(ax=ax1, alpha= 0.9, facecolor='lightcoral', edgecolors= 'none', markersize=100)
states.plot(ax=ax1, alpha= 0.2, facecolor='whitesmoke', edgecolors= 'grey', hatch= '///', markersize=50)

    # Annotate Figure
plt.title('NASA/SpaceX Splashdown Sites')
# Label each lat/long point
for x, y, label in zip(sites.geometry.x, sites.geometry.y, sites.index):
    ax1.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")
    # code reference: https://matplotlib.org/stable/tutorials/text/annotations.html#plotting-guide-annotation

# CHECK End

# Export: 
fig.savefig('3a_CHECK_sites_shapefile.png', format='png')
sites.to_file('splash_down.gpkg', layer='NASA_sites', driver='GPKG')

#%%
#
# Create site buffer, buoy selection
#


# Buffer: 2 degrees = 120 nautical miles (crs)
sites.crs
site_buffers = sites.buffer( 2 ) 
site_buffers.crs
site_buffers = site_buffers.to_crs(epsg=3857)
print('\n site_buffers.crs: ',site_buffers.crs)


## CHECK Start - plot results on a map

fig,ax1 = plt.subplots(dpi=300, figsize=(12,12))

    # Auto zoom into Continential US Area of Interest
        # uses the 'bounds' or extent of the site_buffers' layer
xlim = ([site_buffers.total_bounds[0],  site_buffers.total_bounds[2]])
ylim = ([site_buffers.total_bounds[1],  site_buffers.total_bounds[3]])

ax1.set_xlim(xlim)
ax1.set_ylim(ylim)

    # Stack layers
    # Plot rings & sites
site_buffers.plot(ax=ax1, alpha= 0.2, facecolor='red', edgecolors= 'none', markersize=50 )
sites.plot(ax=ax1, alpha= 0.9, facecolor='red', edgecolors= 'none', markersize=100)
states.plot(ax=ax1, alpha= 0.2, facecolor='whitesmoke', edgecolors= 'grey', hatch= '///', markersize=50)

    # Annotate Figure
plt.title('NASA/SpaceX Splashdown Sites, buffer')
for x, y, label in zip(sites.geometry.x, sites.geometry.y, sites.index):
    ax1.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")    

fig.savefig('3b_CHECK_buoy_selection_rings.png', format='png')

## CHECK End

# Export: add new layer to geopackage 
site_buffers.to_file('splash_down.gpkg', layer='buoy_selection_rings', driver='GPKG')


#%%

#
# Select NOAA buoys within buffers
#


# Import buoys from geopackage.
buoys = geopandas.read_file('splash_down.gpkg', layer='buoys_all')
buoys.crs
buoys = buoys.to_crs(epsg=3857)
print('\n buoys.crs: ', buoys.crs)

## CHECK Start - plot results on a map

fig,ax1 = plt.subplots(dpi=300, figsize=(12,12))
buoys.plot(ax=ax1, edgecolors= 'black')

    # Confirm buffers crs matches points.
site_buffers = geopandas.read_file('splash_down.gpkg', layer='buoy_selection_rings')
site_buffers.crs
site_buffers = site_buffers.to_crs(epsg=3857)

    # CHECK: plot both together
fig,ax1 = plt.subplots(dpi=300, figsize=(12,12))
plt.title('All NOAA Buoys & NASA Site range rings (red)')

    # Zoom into Continential US Area of Interest
xlim = ([site_buffers.total_bounds[0],  site_buffers.total_bounds[2]])
ylim = ([site_buffers.total_bounds[1],  site_buffers.total_bounds[3]])

ax1.set_xlim(xlim)
ax1.set_ylim(ylim)

    # Stack layers
buoys.plot(ax=ax1, facecolor='none', edgecolors= 'black', markersize=5)
sites.plot(ax=ax1, alpha= 0.9, facecolor='red', edgecolors= 'none', markersize=100)
states.plot(ax=ax1, alpha= 0.2, facecolor='whitesmoke', edgecolors= 'grey', hatch= '///', markersize=50)
site_buffers.plot(ax=ax1, alpha= 0.1, facecolor='red', edgecolors= 'none', markersize=50 )

    # Annotate Figure
plt.title('NASA/SpaceX Splashdown Sites, buffer')
for x, y, label in zip(sites.geometry.x, sites.geometry.y, sites.index):
    ax1.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")    
    
fig.savefig('3c_CHECK_buoys_&_selection_rings.png', format='png')

## CHECK End

#%%
#
# Select buoys within buffers
#

in_buffer = geopandas.overlay(site_buffers, buoys, how='intersection', keep_geom_type=False)
   # Ref: https://geopandas.org/docs/user_guide/set_operations.html

print('\nNOAA Stations near Splashdown Sites:\n', in_buffer.count())

# CHECK Start - plot results on a map

fig,ax1 = plt.subplots(dpi=300, figsize=(12,12))
plt.title('NOAA Buoys in NASA Site range rings (red)')

    # Zoom into Continential US Area of Interest
xlim = ([site_buffers.total_bounds[0],  site_buffers.total_bounds[2]])
ylim = ([site_buffers.total_bounds[1],  site_buffers.total_bounds[3]])

ax1.set_xlim(xlim)
ax1.set_ylim(ylim)

    # Stack layers
    # Plot rings & sites
in_buffer.plot(ax=ax1, facecolor='none', edgecolors= 'black', markersize=5)
sites.plot(ax=ax1, alpha= 0.9, facecolor='red', edgecolors= 'none', markersize=100)
states.plot(ax=ax1, alpha= 0.2, facecolor='whitesmoke', edgecolors= 'grey', hatch= '///', markersize=50)
site_buffers.plot(ax=ax1, alpha= 0.1, facecolor='red', edgecolors= 'none', markersize=50 )


fig.savefig('3d_CHECK_buoys_inBuffer.svg', format='svg')

## CHECK End

# Export: add new layer to geopackage 
in_buffer.to_file('splash_down.gpkg', layer='nearby_wx_stations', driver='GPKG')
in_buffer.columns

#%%

# List all layers within a geopackage
for layername in fiona.listlayers('splash_down.gpkg'):
    with fiona.open('splash_down.gpkg', layer=layername) as src:
        print('layer name:', layername, '|| records:', len(src))
        
    # Ref: https://fiona.readthedocs.io/en/latest/README.html#reading-multilayer-data
    
print('\n .py Complete')