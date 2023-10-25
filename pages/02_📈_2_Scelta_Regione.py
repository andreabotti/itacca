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
# from color_pools_fn import create_color_pools
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
top_col1, top_col2 = st.columns([3,1])

with top_col1: 
    with st.container():
        st.markdown("# AB.S.RD Climate ToolSet")
        st.markdown("### Analisi di Dati Climatici Presenti e Futuri")
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
# Region Selection
col1, space1, col2, space2, col3 = st.columns([18,1,15,1,25])

with top_col2:
    selected_region = st.sidebar.selectbox("Selezionare la regione:", regions_list)

    color_marker_CTI = st.sidebar.color_picker('Colore per marker CTI', '#71A871')
    color_marker_COB = st.sidebar.color_picker('Colore per marker COB', '#E07E34')

# Filter CTI and COB stations based on selected region
selected_reg = [i for i in dict_regions if dict_regions[i]==selected_region][0]

df_SelectedLocations_COB = df_locations_COB[df_locations_COB.reg == selected_reg]
df_SelectedLocations_CTI = df_locations_CTI[df_locations_CTI.region == selected_region]

df_TablePlot_CTI = df_SelectedLocations_CTI
df_TablePlot_COB = df_SelectedLocations_COB
try:
    df_TablePlot_COB.drop(['location'], axis=1, inplace=True)
except:
    ''
df_TablePlot_CTI = df_TablePlot_CTI[['province', 'city', 'lat', 'lon', 'alt']]
df_TablePlot_COB.drop(['reg'], axis=1, inplace=True)
n = df_TablePlot_CTI.shape[0]

##########




with col1:
    # OPTION 2 : go.Scattermapbox

    # Calculate the centroid of the provided data points
    center_latitude = sum(df_SelectedLocations_CTI.lat) / len(df_SelectedLocations_CTI.lat)
    center_longitude = sum(df_SelectedLocations_CTI.lon) / len(df_SelectedLocations_CTI.lon)

    # print(df_SelectedLocations_COB)

    fig2 = go.Figure()
    fig2.add_traces(
        go.Scattermapbox(
            lat=df_SelectedLocations_CTI.lat,
            lon=df_SelectedLocations_CTI.lon,
            text=df_SelectedLocations_CTI.province,
            mode='markers',
            marker=go.scattermapbox.Marker(size=10, color=color_marker_CTI),
            )
    )
    fig2.add_traces(
        go.Scattermapbox(
            lat=df_SelectedLocations_COB.lat,
            lon=df_SelectedLocations_COB.lon,
            text=df_SelectedLocations_COB.filename,
            mode='markers',
            marker=go.scattermapbox.Marker(size=10, color=color_marker_COB),
            )
    )
    fig2.update_layout(
        showlegend=False,
        height=400,
        hovermode='closest',
        mapbox_style="light",
        # mapbox_style = 'mapbox://styles/andreabotti/cln47wjba036a01qubmem1lox',
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox=dict(
            accesstoken=mapbox_access_token,
            center=dict(lat=center_latitude,lon=center_longitude),
            zoom=6,
            # style='mapbox://styles/andreabotti/cln47wjba036a01qubmem1lox',
        )
    )

    st.markdown('##### Vista mappa')
    st.plotly_chart(fig2, use_container_width=True)
##########




##########
with col2:
    st.markdown('**{s}** Stazioni meteo in **{r}** | Banca dati [**CTI**](https://try.cti2000.it/)'.format(
        s=len(df_TablePlot_CTI), r=selected_region)
    )
    st.table(df_TablePlot_CTI.style.format(
        { "alt": "{:.0f}", "lat": "{:.2f}", "lon": "{:.2f}", }
        ))

with col3:
    # st.divider()
    st.markdown(
        '**{s}** Stazioni meteo in **{r}**  |  Banca dati [Climate OneBuilding (COB)](https://climate.onebuilding.org)'.format(
        s=len(df_TablePlot_COB), r=selected_region)
    )
    st.table(df_TablePlot_COB.style.format(
        { "alt": "{:.0f}", "lat": "{:.2f}", "lon": "{:.2f}", }
        ))

##########



st.session_state['df_SelectedLocations_CTI'] = df_SelectedLocations_CTI
st.session_state['df_SelectedLocations_COB'] = df_SelectedLocations_COB

st.session_state['selected_reg'] = selected_reg
st.session_state['selected_region'] = selected_region

