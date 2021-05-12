# Location Analysis: Using Real-Time NOAA data
### Case Study. Identify the most suitable NASA/SpaceX Dragon Splashdown Sites
![](https://github.com/daeberly/real-time-location-analysis/blob/main/end_product.jpg)

## Purpose.
This project provides a hands-off repeated, auditable, and accurate framework to pull large volumes of web data, batch process and manipulate it before analysis. No external programs (QGIS or ArcGIS) are used for analysis or plotting; only python coding, associated modules and embedded methods. Only three user inputs are required, after that it can rerun the analysis repeated with no interaction by the user.

### Use Case.
Here, we determine NASA/SpaceX splashdown site viability with 10 minute weather updates that include the previous 72 hours. NASA re-evaluates all landing sites multiple times before splashdown, the latest 1 hour and 20 minutes before arrival. This tool helps NASA as well as U.S. Coast Guard command centers whom must identify the best unit to respond, as the USCG is charged with protecting the public, NASA's astronauts and its high-valued capsule.

#### Site Evaluation Decision Gates:

    1-2 days priority
    6 hours before undocking
    2.5 hours before undocking
        - crew undocks is marginal/No-Go
        - splashdown w/in 24 hours after
        - remain in orbit 24-48 hrs for landing attempt

    6 hrs before splashdown
    1hr 20 mins before splashdown

#### Splashdown requirements:

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

#### User-defined inputs.
1. SpaceX splashdown site with latitude & longitude.
1. URL for NOAA weather reports
1. Desired radius (120nm) from each site for selecting NOAA reporting stations
1. Weather criteria
1. U.S. Coast Guard units with latitude, longitude and asset transit speed.

### Overall Flow.
1. Download data from web [1. get_web_data.py]
1. Combine data into dataframe [2. clean_input_data.py]
1. Find NOAA stations within range of sites [3. landing_site_data.py]
1. Plot data & map USCG force laydown relative to sites [4. site_evaluation.py]

## Processing and Location Analysis
The code pulls real-time and historical data from the active NOAA weather stations world-wide(total 801), batch processes two data files (.txt and .spec) per station (1.6 million records) from an input folder and plot splashdown sites. Here, we apply a 120nm buffer around splashdown sites to select nearby NOAA reporting stations (Figure 1.).
![](https://github.com/daeberly/real-time-location-analysis/blob/main/Outputs/3c_CHECK_buoys_%26_selection_rings.svg)
*Figure 1. NOAA weather reporting stations near Space X Splashdown Sites.*

Once NOAA stations are identified, they are georeferenced, and plotted the results against the weather criteria. As a proof of concept, we only look at current wind speed and wave height as well as changes over time per station (Figure 2.)
![](https://github.com/daeberly/real-time-location-analysis/blob/main/Outputs/4b_wind_byLocation_violinplot.png)
*Figure 2. Wind speed distributions within 120nm of each site.*

The U.S. Coast Guard is charged with protecting the capsule upon arrival, establishing a security boundary and providing search and rescue. With each site around 12nm from shore this poses a capacity and capabilities challenge. For the U.S.Coast Guard, nearby small boat station one-hour transit ranges are plotted against splashdown sites and the U.S. 12nm territorial sea boundary (Figure 3). Only within the territorial seas is the U.S., by regulation the U.S.Coast Guard, authorize to establish and maintain a security boundary. Outside of 12nm, U.S. sovereignty ends and under the United Nations Commission on the Law of the Sea (UNCLOS) with respect to security zones.

It is important to note, all splashdown sites are within a one-hour transit of USCG small boat stations and outside the 12nm territorial sea boundary.

![](https://github.com/daeberly/real-time-location-analysis/blob/main/Outputs/4g_SpaceXsites_vs-USCG.svg)
*Figure 3. Space X Splashdown Sites within 1-hour range of USCG small boat stations.*

### Findings
1. Coding is fun and rewarding, but challenging at times. With over 1.6 million weather observations from NOAA, 5 of 7 locations were under the 15 ft/sec (10.2 mph) wind limitation. Running the program two days later, all stations were under the wind limitation except Tampa, FL previous within limits. This shows time-sensitive decisions, if available, require time enabled (near-real time) data to support decision makers.

2. This coding framework and it's subparts are applicable in all disciplines. For example, in time of COVID-19, it could access all vaccine or test location appointments, consolidate them and display the closest.

### Data Sources.
- NASA/SpaceX Splashdown Sites & Weather Criteria. https://www.nasa.gov/sites/default/files/atoms/files/ccp_splashdown.pdf
- U.S. Coast Guard station & asset info. Compiled by me & included in the public GitHub "Inputs" folder.
- U.S. States geodatabase. Census at https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
- Territorial Sea shapefile. Esri at https://hub.arcgis.com/datasets/44f58c599b1e4f7192df9d4d10b7ddcf_1?geometry=-161.895%2C-12.805%2C161.895%2C73.355

### Original Goal.
#### Project feel short of the raster rendering and point extraction.
This case study identifies which NASA/SpaceX Dragon recovery sites meet their wind and wave height requirements. It pulls NOAA buoy .txt files, batch processes the data to create a visual timeseries. The timeseries is used to forecasting sea surface wave heights. Since the NASA/SpaceX recovery sites are not co-located at buoy sites, a buoy data is interpolated to create a raster, then lat/long point estimates are extracted from the raster for site conditions.

### Specific Learning Goals.
1. Import & convert real-time data from web (wget)
1. Batch process input folder & export result (Glob)
1. Plot results based on decision criteria
1. Create raster image from lat/long values (*attempted*)
1. Extract values for different lat/long (*attempted*)
1. Plot, model & forecast (*partially completed*)
