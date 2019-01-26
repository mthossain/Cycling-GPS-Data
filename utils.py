import pandas as pd
import xml.etree.ElementTree as ET


def parse_gpx(filename):
    """Parse data from a GPX file and return a Pandas Dataframe
    with columns for latitude, longitude and elevation and
    with timestamps as the row index"""
    
    tree = ET.parse(filename)
    root = tree.getroot()

    # define a namespace dictionary to make element names simpler
    # this mirrors the namespace definintions in the XML files
    ns = {'gpx':'http://www.topografix.com/GPX/1/1',
          'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'}

    # when we look for elements, we need to use the namespace prefix
    trk = root.find('gpx:trk', ns)
    trkseg = trk.find('gpx:trkseg', ns)

    data = []
    times = []
    
    # iterate over the first ten trkpt elements - the children of trkseg
    for trkpt in trkseg:
        # get some properties from the attributes
        lon = trkpt.attrib['lon']
        lat = trkpt.attrib['lat']
        # get values from the child elements
        ele = trkpt.find('gpx:ele', ns).text
        time = trkpt.find('gpx:time', ns).text

        row = {
               'latitude': float(lat),
               'longitude': float(lon),
               'elevation': float(ele),
              }
        data.append(row)
        times.append(time)

    times = pd.to_datetime(times)
    return pd.DataFrame(data, index=times)

