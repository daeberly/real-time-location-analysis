! [] (https://github.com/daeberly/real-time-location-analysis/blob/main/end_product.jpg)

# Location Analysis: Using Real-Time NOAA data

### Purpose.
The purpose of this project is to create a hands-off repeated, auditable, and accurate framework. In this case, it helps determine NASA/SpaceX splashdown site viability with continuous weather updates that occur every 10 minutes. As well, it can be used to help aid U.S. Coast Guard command centers identify the best unit to respond, as the USCG is charged with protecting the public, NASA's astronauts and its high-valued capsule.

SpaceX, contracted with NASA, used seven 'splashdown' sites in Southeast U.S. to recover the manned Dragon capsules. Each site is re-evaluated multiple times prior to landing, with the last decision gate at 1 hour and 20 minutes.

The U.S. Coast Guard is charged with protecting capsule upon arrival, establishing a security boundary and providing search and rescue. With each site around 12nm from shore this poses a capacity and capabilities challenge.

The code pulls real-time and historical data from the NOAA, batch processes it from an input folder and maps splashdown sites, NOAA reporting stations within 120nm then plots the results against the wind criteria. As well, CG units are mapped with their one-hour transit range and the 12nm territorial sea boundary. Both are combined in QGIS to overlay the results.

 QGIS and ArcGIS were not used. All mapping & selections were completed with python modules & coding requiring no outside software knowledge or usage.

## Findings
1. Coding is fun and rewarding, but challenging at times. With over 1.6 million weather observations from NOAA, 5 of 7 locations were under the 15 ft/sec (10.2 mph) wind limitation. Running the program two days later, all stations were under the wind limitation except Tampa, FL previous within limits. This shows time-sensitive decisions, if available, require time enabled (near-real time) data to support decision makers.

2. This coding framework and it's subparts are applicable in all disciplines. For example, in time of COVID-19, it could access all vaccine or test location appointments, consolidate them and display the closest. 

## Data Sources.
- NASA/SpaceX Splashdown Sites & Weather Criteria. https://www.nasa.gov/sites/default/files/atoms/files/ccp_splashdown.pdf
- U.S. Coast Guard station & asset info. Compiled by me & included in the public GitHub "Inputs" folder.
- U.S. States geodatabase. Census at https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
- Territorial Sea shapefile. Esri at https://hub.arcgis.com/datasets/44f58c599b1e4f7192df9d4d10b7ddcf_1?geometry=-161.895%2C-12.805%2C161.895%2C73.355

## Original Goal.
### Project feel short of the raster rendering and point extraction.
This case study identifies which NASA/SpaceX Dragon recovery sites meet their wind and wave height requirements. It pulls NOAA buoy .txt files, batch processes the data to create a visual timeseries. The timeseries is used to forecasting sea surface wave heights. Since the NASA/SpaceX recovery sites are not co-located at buoy sites, a buoy data is interpolated to create a raster, then lat/long point estimates are extracted from the raster for site conditions.

### User-defined inputs.
1. SpaceX splashdown site with latitude & longitude.
1. URL for NOAA weather reports
1. Desired radius (120nm) from each site for selecting NOAA reporting stations
1. Weather criteria
1. U.S. Coast Guard units with latitude, longitude and asset transit speed.

## Overall Flow.
1. Download data from web [1. get_web_data.py]
1. Combine data into dataframe [2. clean_input_data.py]
1. Find NOAA stations within range of sites [3. landing_site_data.py]
1. Plot data & map USCG force laydown relative to sites [4. site_evaluation.py]

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
1. Plot results based on decision criteria
1. Create raster image from lat/long values (*attempted*)
1. Extract values for different lat/long (*attempted*)
1. Plot, model & forecast (*partially completed*)
