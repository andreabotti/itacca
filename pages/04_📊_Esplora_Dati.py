# IMPORT LIBRARIES
import streamlit as st
import re, os, sys, time, json, datetime
from datetime import datetime
import requests, urllib.request, json
import pandas as pd, numpy as np
import pydeck # import pydeck instead of pdk

from streamlit_plotly_events import plotly_events
import matplotlib.pyplot as plt, seaborn as sns, plotly.graph_objects as go, plotly.express as px, chart_studio
from plotly.subplots import make_subplots
chart_studio.tools.set_credentials_file(username='a.botti', api_key='aA5cNIJUz4yyMS9TLNhW');
# px.set_mapbox_access_token('pk.eyJ1IjoiYW5kcmVhYm90dGkiLCJhIjoiY2xuNDdybms2MHBvMjJqbm95aDdlZ2owcyJ9.-fs8J1enU5kC3L4mAJ5ToQ')
import leafmap.foliumap as leafmap

from meteostat import Stations, Hourly
from fn__epw_read import create_df_weather, epwab, strip_string_from_index, strip_string_from_columns
from fn__color_pools import create_color_pools
from fn__create_charts import calculate_and_plot_differences


##########

mapbox_access_token = 'pk.eyJ1IjoiYW5kcmVhYm90dGkiLCJhIjoiY2xuNDdybms2MHBvMjJqbm95aDdlZ2owcyJ9.-fs8J1enU5kC3L4mAJ5ToQ'





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
# STREAMLIT SESSION STATE - LOAD DATA
df_locations_CTI = st.session_state['df_locations_CTI']
df_locations_COB = st.session_state['df_locations_COB']

df_CTI_DBT = st.session_state['df_CTI_DBT']
df_COB_DBT = st.session_state['df_COB_DBT']

geojson_italy_regions = st.session_state['geojson_italy_regions']
geojson_italy_provinces = st.session_state['geojson_italy_provinces']

dict_regions = st.session_state['dict_regions']
regions_list = st.session_state['regions_list']
#
#
#
#
#



##########
col1, col2, col3 = st.columns([1,10,15])

with col1:

    col11, col12 = st.columns([1,1])
    with col11:
        color_marker_CTI = st.sidebar.color_picker('Colore per marker CTI', '#71A871')
    with col12:
        color_marker_COB = st.sidebar.color_picker('Colore per marker COB', '#E07E34')


with col2:

    n = df_locations_CTI.shape[0]
    try:
        df_locations_CTI.set_index('reg', inplace=True)
    except:
        ""

    # OPTION 2 : go.Scattermapbox
    # Calculate the centroid of the provided data points
    center_latitude = sum(df_locations_CTI.lat) / len(df_locations_CTI.lat)  - 0.8
    center_longitude = sum(df_locations_CTI.lon) / len(df_locations_CTI.lon) + 0.5

    # print(df_locations_COB)

    fig2 = go.Figure()
    fig2.add_traces(
        go.Scattermapbox(
            lat=df_locations_CTI.lat,
            lon=df_locations_CTI.lon,
            text=df_locations_CTI.province,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=8,
                color=color_marker_CTI,
                # symbol='marker',
                ),
            )
    )
    fig2.add_traces(
        go.Scattermapbox(
            lat=df_locations_COB.lat,
            lon=df_locations_COB.lon,
            text=df_locations_COB.filename,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=8,
                color=color_marker_COB,
                # symbol='diamond',
                ),
            )
    )
    fig2.update_layout(
        showlegend=False,
        height=680,
        hovermode='closest',
        mapbox_style="light",
        # mapbox_style = 'mapbox://styles/andreabotti/cln47wjba036a01qubmem1lox',
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox=dict(
            accesstoken=mapbox_access_token,
            center=dict(lat=center_latitude,lon=center_longitude),
            zoom=5,
            # style='mapbox://styles/andreabotti/cln47wjba036a01qubmem1lox',
        )
    )

    # st.markdown('##### Vista mappa')
    st.plotly_chart(fig2, use_container_width=True)
##########


try:
    df_locations_COB.drop(['location'], axis=1, inplace=True) 
except:
    'do nothing'


with st.sidebar:
    sel_month_COB = st.select_slider(
        'Scelta mesi per la visualizzazione',   options=np.arange(1,13,1),  value=(6,8))
    # st.sidebar.divider()
    lower_threshold = st.slider('Soglia per isolare temperature massime (C)', min_value=20, max_value=40, step=1, value=30)




with col3:
    # st.write('Stazioni Meteo - Banca dati CTI')
    filter_str_CTI = st.text_input(
        "Banca dati CTI - Digitare per filtrare la tabella secondo la colonna \"city\" ",
        "",
        key="filter_str_CTI",
    ).lower()

    df_locations_CTI = df_locations_CTI[df_locations_CTI['city'].str.contains(filter_str_CTI, na=False, case=False)]

    st.dataframe(df_locations_CTI, use_container_width=True)

    # st.write('Stazioni Meteo - Dataset TMYx')
    filter_str_COB = st.text_input(
        "Dataset TMYx - Digitare per filtrare secondo la colonna \"filename\" ",
        "2007",
        key="filter_str_COB",
    )
    df_locations_COB = df_locations_COB[df_locations_COB['filename'].str.contains(filter_str_COB, na=False, case=False)]
    df_locations_COB.set_index('reg', inplace=True)

    sel_stations_COB_list = [s.rsplit('.epw')[0] for s in df_locations_COB['filename'].to_list()]
    number_pos = [ re.search(r'\d+', s).span()[0] for s in sel_stations_COB_list]


    sel_stations_COB_list_filtered = []
    for s in sel_stations_COB_list:
        number_pos = re.search(r'\d+', s).span()[0]
        sel_stations_COB_list_filtered.append( s[int(number_pos):] )


    cols_COB = df_COB_DBT.columns.to_list()
    sel_cols_COB = []
    for c in cols_COB:
        c = c.split('DBT__')[-1]
        # print(c)
        for s in sel_stations_COB_list_filtered:
            if c == s:
                sel_cols_COB.append(c)


    st.dataframe(df_locations_COB, use_container_width=True)

##########




##########
# TEMPERATURE PLOT
df_CTI_DBT_plot = df_CTI_DBT.copy()
df_CTI_DBT_plot.columns = df_CTI_DBT_plot.columns.str.replace('DBT\|','')


# Select columns for filtering
sel_cols_CTI = []
for p in df_locations_CTI.province:
    for c in df_CTI_DBT_plot.columns:
        DBT_province = c.split('__')[1]
        if DBT_province == p:
            sel_cols_CTI.append(c)

sel_cols_COB = []
for f in df_locations_COB.filename:
    num = re.search(r'\d+', f).group()
    f = f.rsplit('.epw')[0]
    f = f.rsplit(num)[-1]
    stringa = 'DBT__{}{}'.format(num,f)
    # print(stringa)

    for c in df_COB_DBT.columns:
        if c == stringa:
            sel_cols_COB.append(c)

# Filter columns
df_CTI_DBT_plot = df_CTI_DBT_plot[sel_cols_CTI]
df_COB_DBT_plot = df_COB_DBT.filter(sel_cols_COB)
df_COB_DBT_plot.set_index(df_CTI_DBT_plot.index, inplace=True)

# Set datetime index
df_COB_DBT_plot['datetime']=pd.to_datetime(df_COB_DBT_plot.index)
df_COB_DBT_plot.set_index(['datetime'], inplace=True, drop=True)

df_CTI_DBT_plot['datetime']=pd.to_datetime(df_CTI_DBT_plot.index)
df_CTI_DBT_plot.set_index(['datetime'], inplace=True, drop=True)








