import pandas as pd
import utils
import math
import numpy as np


def distance (lat1, lon1, lat2, lon2):
    """Calculates distance between given points"""


    # Convert degrees to radians
    lat1 = lat1 * math.pi / 180.0
    lon1 = lon1 * math.pi / 180.0

    lat2 = lat2 * math.pi / 180.0
    lon2 = lon2 * math.pi / 180.0

    # Radius of earth in metres
    r = 6378100

    # P
    rho1 = r * math.cos(lat1)
    z1 = r * math.sin(lat1)
    x1 = rho1 * math.cos(lon1)
    y1 = rho1 * math.sin(lon1)

    # Q
    rho2 = r * math.cos(lat2)
    z2 = r * math.sin(lat2)
    x2 = rho2 * math.cos(lon2)
    y2 = rho2 * math.sin(lon2)

    # Dot product
    dot = (x1 * x2 + y1 * y2 + z1 * z2)
    cos_theta = dot / (r * r)

    # Acos(Cos) does not have value for over 1
    if cos_theta > 1:
        cos_theta = 1
    theta = math.acos(cos_theta)

    # Distance in Metres
    return r * theta



def speed (lat1, lon1, lat2, lon2, timeStamp1, timeStamp2):
    """Calculates speed from given points and time stamps"""

    # Calling the distance function to get the distance between 2 points
    dist = distance(lat1, lon1, lat2, lon2)
    # Getting the time difference between 2 time stamps
    time_s = abs((timeStamp2 - timeStamp1))

    # If time is zero then there is no speed
    if time_s.total_seconds() == 0:
        return 0

    speed_mps = dist/time_s.total_seconds()

    # Converting mps to kph
    speed_kph = (speed_mps * 3600.0) / 1000.0

    return speed_kph


def speed_list (data_frame):
    """Creates a list of tupples of Distance and Speed from each points"""

    lst = []
    # Trigger variable to skip executing statements for the first iteration
    flag = False
    for row in data_frame.itertuples():
        if flag:
            # Getting distance by calling the distance function between current points and previous points
            dist = float(distance (row.latitude, row.longitude, prev_row.latitude, prev_row.longitude))
            # Getting speed by calling the speed function between current points and previous points
            spd = float(speed(row.latitude, row.longitude, prev_row.latitude, prev_row.longitude, row.Index, prev_row.Index))
            lst.append((dist, spd))
        # Updating previous row as a current row before going to the next iteration
        prev_row = row
        # Trigger variable is true so it does not skip executing statements from future iteration
        flag = True
    return lst



def distance_list (data_frame):
    """Creates a list of distances from the starting point to the end poing"""

    lst = []
    # Trigger variable to skip executing statements for the first iteration
    flag = False
    ignore = False
    for row in data_frame.itertuples():
        if flag:
            # Getting distance between two points
            temp = float((distance(row.latitude, row.longitude, prev_row.latitude, prev_row.longitude)))
            # If the distance is not zero or point is not stationary
            if temp != 0:
                ignore = True
            # Add the distance to the list
            if ignore == True:
                lst.append(temp)

        if ignore == False:
            # Updating previous row as a current row before going to the next iteration
            prev_row = row
        # Trigger variable is true so it does not skip executing statements from future iteration
        flag = True
    return lst



def elevation_list (data_frame):
    """Creates a list of elevation differences between two elevations"""

    lst = []
    # Trigger variable to skip executing statements for the first iteration
    flag = False
    for row in data_frame.itertuples():
        if flag:
            temp = float(row.elevation-prev_row.elevation)
            lst.append(temp)
        # Updating previous row as a current row before going to the next iteration
        prev_row = row
        # Trigger variable is true so it does not skip executing statements from future iteration
        flag = True
    return lst



def distance_per_unit_list (data_frame):
    """Creates a list of distances between two points"""

    lst = []
    # Trigger variable to skip executing statements for the first iteration
    flag = False
    for row in data_frame.itertuples():
        if flag:
            lst.append(float((distance (row.latitude, row.longitude, prev_row.latitude, prev_row.longitude))))
        # Updating previous row as a current row before going to the next iteration
        prev_row = row
        # Trigger variable is true so it does not skip executing statements from future iteration
        flag = True
    return lst



def gradient_list (df_main):
    """Creates a list of gradients from two points"""

    # DataFrame with distance difference and elevation between two points
    data_frame = pd.DataFrame({'distance':distance_per_unit_list(df_main), 'elevation':elevation_list(df_main)})
    data_frame.elevation = data_frame.elevation.astype(str).astype('float64')
    data_frame.distance = data_frame.distance.astype(str).astype('float64')

    lst = []
    for row in data_frame.itertuples():
        # If not stationary then add
        if row.distance !=0:
            # Formula to get gradient = elevation over distance
            temp = float((row.elevation/row.distance))
        else:
            temp = 0
        lst.append(temp)
    return lst



def lap_detector (df_main):
    """Calcualtes lap count"""

    # Making a DataFrame with only with distance differences between the start point and end points
    data_frame = pd.DataFrame({'distance':distance_list(df_main)})
    size = data_frame.size
    # if not enough points to calculate laps
    if size < 3:
        return -1
    lap_count = 0
    # Distance difference tolerance when counting the lap
    n = data_frame[data_frame.index==0].distance.values[0] + 10
    # Distance difference of previous point from the starting point
    prev_note = data_frame[data_frame.index==0].distance.values[0]
    # Distance difference of current point from the starting point
    main_note = data_frame[data_frame.index==1].distance.values[0]
    # Distance difference of next point from the starting point
    current_note = data_frame[data_frame.index==2].distance.values[0]

    for i in range(2, size):
        # If current point is decreased from previous point and the next point
        # is increased from current point and current point falls under tolerance
        # level then it is a lap.
        if ((main_note<prev_note and current_note>main_note) and main_note<n):
            lap_count += 1
        # Updating points with new indexs before next iteration
        prev_note = data_frame[data_frame.index==i-2].distance.values[0]
        main_note = data_frame[data_frame.index==i-1].distance.values[0]
        current_note = data_frame[data_frame.index==i].distance.values[0]
    return lap_count




def speedDate(fileList):
    """Creates a list of tuples of average speeds and their dates"""

    lst = []
    for x in fileList:
        # Getting the average speed of a perticular file by calling the speed_list function
        speed = (pd.DataFrame({'avg_speed':[b for a, b in speed_list(x)]})).mean().values[0]
        # Adding respective date
        date = x.index[0].date()
        lst.append([speed, date])
    return lst



def distance_list_with_time (dataframe):
    """Creates a list of distance differences between points and their times"""

    # Custom DataFrame with reseted index, so index can be accessed with numarical values
    data_frame = dataframe.reset_index()
    # DataFrame columns according to the columns before reseting
    data_frame.columns = ['time', 'elevation', 'latitude', 'longitude']
    lst = []
    # Trigger variable to skip executing statements for the first iteration
    flag = False
    ignore = False
    for row in data_frame.itertuples():
        if flag:
            # Getting distance between two points
            dist = float((distance(row.latitude, row.longitude, prev_row.latitude, prev_row.longitude)))
            # Getting times
            time = row.time
            # If the distance is not zero or point is not stationary
            if dist != 0:
                ignore = True
            # Add the time and distance to the list
            if ignore == True:
                lst.append((time, dist))

        if ignore == False:
            # Updating previous row as a current row before going to the next iteration
            prev_row = row
        # Trigger variable is true so it does not skip executing statements from future iteration
        flag = True
    return lst




def distWithTimeDFs(df_list):
    """Creates a list of DataFrame files of distance differences between points and their times"""

    lst = []
    for x in df_list:
        dlwt = distance_list_with_time(x)
        lst.append(pd.DataFrame({'time':[time for time, dist in dlwt],
                                'distance':[dist for time, dist in dlwt]}))
    return lst





def lap_detector_with_lapTime (data_frame):
    """Calculates lap time"""

    size = data_frame.shape[0]
    # if not enough points to calculate laps
    if size < 3:
        return -1
    lap_count = 0
    lst = []
    # Distance difference tolerance when counting the lap
    n = data_frame[data_frame.index==0].distance.values[0] + 10

    # Distance difference of previous point from the starting point
    prev_note = data_frame[data_frame.index==0].distance.values[0]
    # Distance difference of current point from the starting point
    main_note = data_frame[data_frame.index==1].distance.values[0]
    # Distance difference of next point from the starting point
    current_note = data_frame[data_frame.index==2].distance.values[0]

    # Time at starting point
    lap_start = pd.Timestamp(data_frame[data_frame.index==0].time.values[0])
    # Time at end point
    lap_end = pd.Timestamp(data_frame[data_frame.index==1].time.values[0])

    for i in range(2, size):
        # If current point is decreased from previous point and the next point
        # is increased from current point and current point falls under tolerance
        # level then it is a lap.
        if ((main_note<prev_note and current_note>main_note) and main_note<n):
            lap_count += 1
            # Time difference between start and end point
            lap = lap_end-lap_start
            # Updateing new time at starting point
            lap_start = data_frame[data_frame.index==i].time.values[0]
            lst.append((lap_count, lap))

        # Updating points with new indexs before next iteration
        prev_note = data_frame[data_frame.index==i-2].distance.values[0]
        main_note = data_frame[data_frame.index==i-1].distance.values[0]
        current_note = data_frame[data_frame.index==i].distance.values[0]

        # Updateing new time at ending point
        lap_end = pd.Timestamp(data_frame[data_frame.index==i-1].time.values[0])

    return lst




def lapWithTimeDFs(file_list):
    """Creates a list of DataFrames of lap times from different races"""

    lst = []
    for x in file_list:
        ldwlt = lap_detector_with_lapTime(x)
        lst.append(pd.DataFrame({'lap':[lap for lap, time in ldwlt],
                                 'time':[time for lap, time in ldwlt]}))
    return lst




def fastestAndSlowestLap(dataFrame_laps):
    """Returns fastest and slowest lap time of a given DataFrame"""

    # Using -8 index to trim out the year month part, just taking the time part
    fastest = str(dataFrame_laps.min().values[1])[-8:]
    slowest = str(dataFrame_laps.max().values[1])[-8:]

    return ((fastest, slowest))
