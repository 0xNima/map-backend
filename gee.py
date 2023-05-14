import ee
import geemap
import geopandas as gpd

from webservice.local import SERVICE_ACCOUNT_EMAIL, SERVICE_ACCOUNT_PATH

credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT_EMAIL, SERVICE_ACCOUNT_PATH)
ee.Initialize(credentials)


INDICATORS_EE_MAP = {
    0: 'MODIS/MOD09GA_006_NDVI',
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

    image = ee.ImageCollection(INDICATORS_EE_MAP[indicator]) \
        .filterDate(start, end).select('NDVI').mean()

    geemap.zonal_statistics(image, feature_collection, output, statistics_type='MEAN', scale=500, crs=str(gdf.crs))
