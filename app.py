import streamlit as st
import os, sys, time, json, datetime
from datetime import datetime
import requests, urllib.request, json
import pandas as pd, numpy as np, pydeck as pdk

from streamlit_plotly_events import plotly_events
import matplotlib.pyplot as plt, seaborn as sns, plotly.graph_objects as go, plotly.express as px, chart_studio
from plotly.subplots import make_subplots
chart_studio.tools.set_credentials_file(username='a.botti', api_key='aA5cNIJUz4yyMS9TLNhW');

from meteostat import Stations, Hourly
from fn__epw_read import create_df_weather, epwab, strip_string_from_index, strip_string_from_columns
##########




LOCAL_PATH  = r'C:/_OneDrive/OPEN PROJECT SRL/Sostenibilita - Documents/01__Ricerca/10__LCA_Carbon/17__LCA_Coding/01__ITACCA/data/'
FTP_PATH    = r'https://absrd.xyz/streamlit_apps/_weather_data/'
MAIN_PATH = FTP_PATH



# PAGE CONFIG
st.set_page_config(
   page_title="AB.S.RD Climate ToolSet",
   page_icon="📈",
   layout="wide",
   )
padding_top = 0
#
#
#
#
#
st.markdown("""
        <style>
               .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 3rem; padding-right: 3rem;}
        </style>
        """, unsafe_allow_html=True)
#
# TOP CONTAINER
with st.container():
    st.markdown("# AB.S.RD Climate ToolSet")
    st.markdown("### Analisi di Dati Climatici Presenti e Futuri")
    # st.subheader("Analisi di dati climatici di progetto presenti e futuri")
    st.caption('Developed by AB.S.RD - https://absrd.xyz/')
    st.divider()
#
#
#
#
#
# Load Data
url__CTI__stations  = MAIN_PATH + 'CTI__WeatherStations.csv'
url__COB__stations  = MAIN_PATH + 'COB__SelWeatherStations.csv'
url__cti__dbt = MAIN_PATH + 'CTI__AllStations__DBT.csv'
url__cob__dbt = MAIN_PATH + 'COB__SelWeatherStations__DBT.csv'

url__cti_try__dict_regionss      = MAIN_PATH + 'CTI__dict__Regions.json'
url__cti_try__geoson_regions    = MAIN_PATH + 'limits_IT_regions.geojson'
url__cti_try__geoson_provinces  = MAIN_PATH + 'limits_IT_provinces.geojson'
#
#
#
#
#
# Load CTI stations list
@st.cache_resource
def load_data__locations_CTI():
    df = pd.read_csv(url__CTI__stations)
    return df

# Load COB stations list
@st.cache_resource
def load_data__locations_COB():
    df = pd.read_csv(url__COB__stations)
    return df

# Load CTI italian regions - short and long names
@st.cache_resource
def load_data_dict_regionss():
    json_file = json.loads(requests.get(url__cti_try__dict_regionss).text)
    cti_try__dict_regionss = json_file
    return cti_try__dict_regionss

# Load DBT for CTI dataset
@st.cache_resource
def load_data__CTI_DBT():
    df = pd.read_csv(url__cti__dbt,index_col='datetime')
    return df

# Load DBT for CTI dataset
@st.cache_resource
def load_data__COB_DBT():
    df = pd.read_csv(url__cob__dbt)
    return df

# Load TopoJSON
@st.cache_resource
def load_data_regions():
    json_file = json.loads(requests.get(url__cti_try__geoson_regions).text)
    geojson_italy_regions = json_file
    return geojson_italy_regions

@st.cache_resource
def load_data_provinces():
    json_file = json.loads(requests.get(url__cti_try__geoson_provinces).text)
    geojson_italy_provinces = json_file
    return geojson_italy_provinces

# LOAD DATA
df_locations_CTI   = load_data__locations_CTI()
df_locations_COB   = load_data__locations_COB()
df_CTI_DBT = load_data__CTI_DBT()
df_COB_DBT = load_data__COB_DBT()
geojson_italy_regions = load_data_regions()
geojson_italy_provinces = load_data_provinces()
#
#
#
#
#
# DICT REGIONS
cti_try__dict_regionss = {
    "AB":"Abruzzo",         "BC":"Basilicata",          "CM":"Campania",
    "CL":"Calabria",        "ER":"Emilia Romagna",      "FV":"Friuli Venezia Giulia",
    "LZ":"Lazio",           "LG":"Liguria",             "LM":"Lombardia",
    "MH":"Marche",          "ML":"Molise",              "PM":"Piemonte",
    "PU":"Puglia",          "SD":"Sardegna",            "SC":"Sicilia",
    "TC":"Toscana",         "TT":"Trentino Alto Adige", "UM":"Umbria",
    "VD":"Valle dAosta",    "VN":"Veneto"
    }
dict_regions = pd.read_json( url__cti_try__dict_regionss, typ='series')
dict_regions = dict(dict_regions)
regions_list = list(dict_regions.values())
#
#
#
#
#
# DATAFRAME LOCATIONS
df_locations_CTI['region'] = df_locations_CTI['reg'].apply(lambda x: dict_regions.get(x))
sel_cols = ['reg','region','province','city','lat','lon','alt']
df_locations_CTI = df_locations_CTI[sel_cols]

df_locations_COB['wmo_code'] = df_locations_COB['wmo_code'].astype(str) 
df_locations_COB = df_locations_COB[ ['reg', 'location', 'filename', 'wmo_code', 'lat', 'lon','alt'] ]

# st.dataframe(df_locations_CTI)
# st.dataframe(df_locations_COB)


# DATAFRAME PROVINCES
df_province = df_locations_CTI.groupby('province').size()
df_province.rename('station_count', inplace=True)

# DATAFRAME REGION_SHORT
df_reg_short   = df_locations_CTI.groupby('reg').size()
df_reg_short.rename('station_count', inplace=True)
df_reg_short = df_reg_short.reset_index()
df_reg_short['region'] = df_reg_short['reg'].apply(lambda x: dict_regions.get(x))
df_reg_short.set_index('reg',inplace=True)
df_reg_short = df_reg_short[['region', 'station_count']]
#
#
#
#
#
# SAVE ST SESSION STATES
st.session_state['df_locations_CTI'] = df_locations_CTI
st.session_state['df_locations_COB'] = df_locations_COB

st.session_state['df_CTI_DBT'] = df_CTI_DBT
st.session_state['df_COB_DBT'] = df_COB_DBT

st.session_state['df_reg'] = df_reg_short
st.session_state['geojson_italy_regions'] = geojson_italy_regions
st.session_state['geojson_italy_provinces'] = geojson_italy_provinces

st.session_state['dict_regions'] = dict_regions
st.session_state['regions_list'] = regions_list
#
#
#
#
#
# st.dataframe(df_locations_COB)
#
#
#
#
#
##########
current_work_dir = os.getcwd()
# st.caption('Working from path: {}'.format(current_work_dir), unsafe_allow_html=True)

with open('./data/CTI_TRY_description01.txt',encoding='utf8') as f:
    cti_try_descr01 = f.readlines()
with open('./data/CTI_TRY_description02.txt',encoding='utf8') as f:
    cti_try_descr02 = f.readlines()
with open('./data/weather_morphing_description.txt',encoding='utf8') as f:
    weather_morphing_descr01 = f.readlines()
#
#
#
#
#
with open( current_work_dir + '/data/CTI_TRY_description01.txt',encoding='utf8') as f:
    cti_try_descr01 = f.readlines()
with open(current_work_dir + '/data/CTI_TRY_description02.txt',encoding='utf8') as f:
    cti_try_descr02 = f.readlines()
with open(current_work_dir + '/data/weather_morphing_description.txt',encoding='utf8') as f:
    weather_morphing_descr01 = f.readlines()
#
#
#
#
#
p1_col1, spacing, p1_col2, spacing, p1_col3 = st.columns([20,1,20,1,20])    

with p1_col1:
    st.markdown('#### Il passato: Anni Tipo Climatici')
    # st.write('**Elaborazione a cura del Comitato Termotecnico Italiano (CTI)**')
    st.write('Gli anni tipo climatici, o *Test Reference Years (TRY)* o *Typical Meteorological Year (TMY)* vengono forniti dal \
                **Comitato Termotecnico Italiano (CTI)** per 110 località di riferimento distribuite sul territorio nazionale. \
                L\'anno tipo climatico consiste in 12 mesi caratteristici scelti da un database di dati meteorologici di un \
                periodo preferibilmente ampio almeno 10 anni.')
    # st.divider()
    with st.expander('*Per avere più dettagli sui dati disponibili sul sito web del CTI*'):
        st.write('\n'.join(cti_try_descr01))
        st.caption('Fonte: https://try.cti2000.it/')

    with st.expander('*Per avere più dettagli sulla metodologia utilizzata per compilare l\'anno climatico tipo*'):
        st.write('\n'.join(cti_try_descr02))
        st.caption('Fonte: https://try.cti2000.it/')

    st.divider()
    st.markdown('##### Ulteriori informazioni')
    st.markdown("*What is weather data, and how is it collected?*[https://docs.ladybug.tools/ladybug-tools-academy/v/climate-analysis/]",
                unsafe_allow_html=True)

with p1_col2:
    st.markdown('#### Il presente: un clima in cambiamento')
    st.write('Site meteonorm')
    st.divider()

with p1_col3:
    st.markdown('#### Il futuro: proiezioni climatiche e *morphing*')
    st.markdown('#### Il *morphing* dei dati climatici')
    with st.expander('*Dettagli sul morphing di dati climatici per ottenere l\'anno climatico tipo per climi futuri*'):
        st.markdown('\n'.join(weather_morphing_descr01), unsafe_allow_html=True)

    st.markdown('#### Lo strumento *Future Weather Generator*')
# st.dataframe( df_COB_DBT.reindex(sorted(df_COB_DBT.columns), axis=1) )