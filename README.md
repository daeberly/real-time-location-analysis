# real-time-location-analysis
Identify best NASA/SpaceX Dragon Splashdown Site

## Purpose.
The code pulls real-time and historical data from the web, batch processes it from an input folder, maps it (lat/long), attempts to estimate it's weather, then outputs the results.

## Application.
This case study identifies which NASA/SpaceX Dragon recovery sites meet their wind and wave height requirements. It pulls NOAA buoy .txt files, batch processes the data to create a visual timeseries. The timeseries is used to forecasting sea surface wave heights. Since the NASA/SpaceX recovery sites are not co-located at buoy sites, a buoy data is interpolated to create a raster, then lat/long point estimates are extracted from the raster for site conditions.

QGIS and ArcGIS were not used. All mapping & selections are down with python modules & coding.

### User-defined inputs.
Only two user inputs
1. Site lat/long
1. Radius from site for selecting NOAA reporting stations
1. weather criteria

## Overall Flow.
1. Download data from web [1. get_web_data.py]
1. Combine data into dataframe [2. clean_input_data.py]
1. Find NOAA stations within range of sites [3. landing_site_data.py]
1. Create & plot raster of data [4. interpolate_rasters.py]
1. Extract wind & wave values at recovery sites (specific lat/long) [5. extract lat-long value.py]
1. Timeseries plot of values [TBD]
1. Forecast trend [TBD]
1. Rank best splashdown site options [6. Rank sites.py]

## Background. NASA/SpaceX Site Criteria and Decision Gates.

### Splashdown requirements:

Site:
    wind_speed < 15     # ft/sec
    period_height = wave_period != wave_height
    wave_slope < 7      # degrees
    rain_prob < 0.25    # % of 25 dBZ
    ligthning < 0.25    # % within 10 miles

Helicopter Weather criteria:
    vessel_PitchRoll <= 4    # degrees
    ceiling >= 500           # feet
    visibility_day >= .5     # statute miles 

#### Site Evaluation Decision Gates:

    1-2 days priority
    6 hours before undocking
    2.5 hours before undocking
        - crew undocks is marginal/No-Go
        - splashdown w/in 24 hours after
        - remain in orbit 24-48 hrs for landing attempt
        
    6 hrs before splashdown
    1hr 20 mins before splashdown
    
### Specific Learning Goals.
1. Import & convert real-time data from web (wget)
1. Batch process input folder & export result (Glob)
1. Create raster image from lat/long values
1. Extract values for different lat/long
1. Plot, model & forecast
