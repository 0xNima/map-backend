import os
import ee
import geemap
import numpy as np
import pandas as pd
import geopandas as gpd
import json


# service_account = 'my-service-account@...gserviceaccount.com'
# credentials = ee.ServiceAccountCredentials(service_account, '.private-key.json')
# ee.Initialize(credentials)
# ee.Authenticate()

INDICATORS_EE_MAP = {
    0: 'NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG',  # NDVI
    1: ''   # BIOMASS
}


def get_statistic(geo_file, indicator, start, end, output):
    gdf = gpd.read_file(geo_file)

    try:
        feature_collection = geemap.geopandas_to_ee(gdf)
    except ValueError:
        for col in gdf.columns:
            for val in gdf[col]:
                if isinstance(val, list):
                    gdf[col] = gdf[col].apply(lambda x: ' '.join(x))
                    break
        feature_collection = geemap.geopandas_to_ee(gdf)

    image = ee.ImageCollection(INDICATORS_EE_MAP[indicator])\
        .filterDate(start, end).select('avg_rad').mean()

    geemap.zonal_statistics(image, feature_collection, output, statistics_type='MEAN', scale=500)
