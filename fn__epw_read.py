# -*- coding: utf-8 -*-
import os, sys
import pandas as pd
import csv
import epw



def create_df_weather(filepath):
    #read_ewp_as_link(Link_weather)
    epw = EPW()
    epw.read(filepath)
    year, month, day, hour = [], [], [], []
    dry_bulb_temperature = []
    dew_point_temperature = []
    relative_humidity = []
    atmospheric_station_pressure = []
    global_horizontal_radiation = []
    direct_normal_radiation = []
    diffuse_horizontal_radiation = []
    wind_direction = []
    wind_speed = []
    total_sky_cover = []
    opaque_sky_cover = []
    precipitable_water = []

    for wd in epw.weatherdata:
        year.append(wd.year)
        month.append(wd.month)
        day.append(wd.day)
        hour.append(wd.hour)
        dry_bulb_temperature.append(wd.dry_bulb_temperature)
        dew_point_temperature.append(wd.dew_point_temperature)
        relative_humidity.append(wd.relative_humidity)
        atmospheric_station_pressure.append(wd.atmospheric_station_pressure)
        global_horizontal_radiation.append(wd.global_horizontal_radiation)
        direct_normal_radiation.append(wd.direct_normal_radiation)
        diffuse_horizontal_radiation.append(wd.global_horizontal_radiation)
        wind_direction.append(wd.wind_direction)
        wind_speed.append(wd.wind_speed)
        total_sky_cover.append(wd.total_sky_cover)
        opaque_sky_cover.append(wd.opaque_sky_cover)
        precipitable_water.append(wd.precipitable_water)


    df = pd.DataFrame(
        [year, month, day, hour, dry_bulb_temperature, dew_point_temperature, relative_humidity,
         atmospheric_station_pressure, global_horizontal_radiation, direct_normal_radiation, diffuse_horizontal_radiation,
         wind_direction,
         wind_speed, total_sky_cover, opaque_sky_cover, precipitable_water])

    df = df.transpose()
    df.columns = ['year', 'month', 'day', 'hour', 'dry_bulb_temperature', 'dew_point_temperature',
                            'relative_humidity',
                            'atmospheric_station_pressure', 'global_horizontal_radiation', 'direct_normal_radiation',
                            'diffuse_horizontal_radiation',
                            'wind_direction', 'wind_speed', 'total_sky_cover', 'opaque_sky_cover', 'precipitable_water']
    df.columns = ['year', 'month', 'day', 'hour', 'dbt', 'dpt', 'rh', 'a_st_pre', 'gl_hor_rad', 'dir_norm_rad', 'dif_hor_rad',
                            'wind_dir', 'wind_speed', 'tot_sky_cover', 'opa_sky_cover', 'prec_water']

    exclusions = ['dbt', 'dpt','wind_speed']
    for col in df.columns:
      if col not in exclusions:
        df[col] = df[col].astype(int)

    # df.loc[-1] = df.loc[0]  # adding a row
    # df.index = df.index + 1  # shifting index
    # df.sort_index(inplace=True)
    # df.loc[0,'hour'] = 0    # replace value of first hour
    # df = df.iloc[:-1]    # removing last n rows

    dt_str_col = df.year.map(str) + "-" + df.month.map(str) + "-" + df.day.map(str) + "-" + df.hour.map(str)
    df['dt'] = dt_str_col
    dt_col = pd.date_range('2022-01-01', periods=8760, freq='H').shift(periods=1)

    years = df.year.unique()
    df['datetime'] = dt_col
    # df.shift(periods=1, fill_value=0, inplace=True)
    print('data years: ', years)
    return df

##########


class epwab():
    """A class which represents an EnergyPlus weather (epw) file"""
    def __init__(self):
        self.headers={}
        self.dataframe=pd.DataFrame()

    def read(self,fp):
        """Reads an epw file
        Arguments:
            - fp (str): the file path of the epw file
        """
        self.headers=self._read_headers(fp)
        self.dataframe=self._read_data(fp)

    def _read_headers(self,fp):
        """Reads the headers of an epw file
        Arguments:
            - fp (str): the file path of the epw file
        Return value:
            - d (dict): a dictionary containing the header rows
        """
        d={}
        with open(fp, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                if row[0].isdigit():
                    break
                else:
                    d[row[0]]=row[1:]
        return d

    def _read_data(self,fp):
        """Reads the climate data of an epw file
        Arguments:
            - fp (str): the file path of the epw file
        Return value:
            - df (pd.DataFrame): a DataFrame comtaining the climate data
        """
        names=['Year','Month','Day','Hour','Minute',
               'Data Source and Uncertainty Flags',
               'Dry Bulb Temperature',
               'Dew Point Temperature',
               'Relative Humidity',
               'Atmospheric Station Pressure',
               'Extraterrestrial Horizontal Radiation',
               'Extraterrestrial Direct Normal Radiation',
               'Horizontal Infrared Radiation Intensity',
               'Global Horizontal Radiation',
               'Direct Normal Radiation',
               'Diffuse Horizontal Radiation',
               'Global Horizontal Illuminance',
               'Direct Normal Illuminance',
               'Diffuse Horizontal Illuminance',
               'Zenith Luminance',
               'Wind Direction',
               'Wind Speed',
               'Total Sky Cover',
               'Opaque Sky Cover (used if Horizontal IR Intensity missing)',
               'Visibility',
               'Ceiling Height',
               'Present Weather Observation',
               'Present Weather Codes',
               'Precipitable Water',
               'Aerosol Optical Depth',
               'Snow Depth',
               'Days Since Last Snowfall',
               'Albedo',
               'Liquid Precipitation Depth',
               'Liquid Precipitation Quantity']

        first_row=self._first_row_with_climate_data(fp)
        df=pd.read_csv(fp,
                       skiprows=first_row,
                       header=None,
                       names=names)
        return df


    def _first_row_with_climate_data(self,fp):
        """Finds the first row with the climate data of an epw file
        Arguments:
            - fp (str): the file path of the epw file
        Return value:
            - i (int): the row number
        """

        with open(fp, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for i,row in enumerate(csvreader):
                if row[0].isdigit():
                    break
        return i


    def write(self,fp):
        """Writes an epw file
        Arguments:
            - fp (str): the file path of the new epw file
        """
        with open(fp, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for k,v in self.headers.items():
                csvwriter.writerow([k]+v)
            for row in self.dataframe.itertuples(index= False):
                csvwriter.writerow(i for i in row)



def filter_files(path_to_search, strings_to_exclude, strings_to_include, string_ext):
    file_path_list = []
    dict_of_files = {}

    for foldername, subfolders, filenames in os.walk(path_to_search):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            file_name, file_extension = os.path.splitext(filename)

            # Check if any exclusion strings are present in the file name
            exclude_file = any(exclude_str in file_name for exclude_str in strings_to_exclude)

            # Check if inclusion strings are present in the file name
            include_file = any(include_str in file_name for include_str in strings_to_include)

            # Check if the file extension matches the desired extension
            valid_extension = file_extension.lower() == string_ext.lower()

            # Add the file to the filtered list if it meets all criteria
            if not exclude_file and include_file and valid_extension:
                file_path_list.append(file_path)
                dict_of_files[filename] = file_path

    return file_path_list, dict_of_files



def strip_string_from_index(df, string_to_strip):
    # Convert the index to strings and then use the string method 'strip' to remove the specified string
    try:
        df.index = df.index.astype(str).str.strip(string_to_strip)
        df.index = df.index.astype(str).str.replace(string_to_strip,'')
    except:
        'Do nothing'
    return df


def strip_string_from_columns(df, string_to_strip):
    # Use the string method 'strip' to remove the specified string from all column names
    try:
        df.columns = df.columns.str.strip(string_to_strip)
        df.columns = df.columns.str.replace(string_to_strip,'')
    except:
        'Do nothing'
    return df