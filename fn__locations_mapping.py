# IMPORT LIBRARIES
from imports import *
#
#
#
#
#
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # haversine formula 
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


def find_closest(df1, df2, lat_col='lat', lon_col='lon'):
    closest_locations = []

    for index1, row1 in df1.iterrows():
        min_distance = float('inf')
        closest_location = None

        for index2, row2 in df2.iterrows():
            distance = haversine(row1[lat_col], row1[lon_col], row2[lat_col], row2[lon_col])
            
            if distance < min_distance:
                min_distance = distance
                closest_location = row2

        closest_locations.append(closest_location)

    return pd.DataFrame(closest_locations)


