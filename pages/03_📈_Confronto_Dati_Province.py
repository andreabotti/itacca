# IMPORT LIBRARIES
import streamlit as st, pandas as pd, numpy as np
import re, os, sys, time,  datetime, json, requests, urllib.request
from datetime import datetime
from meteostat import Stations, Hourly
from streamlit_plotly_events import plotly_events

import pydeck # import pydeck instead of pdk
import matplotlib.pyplot as plt, seaborn as sns, plotly.graph_objects as go, plotly.express as px, chart_studio
from plotly.subplots import make_subplots
chart_studio.tools.set_credentials_file(username='a.botti', api_key='aA5cNIJUz4yyMS9TLNhW');
import leafmap.foliumap as leafmap
mapbox_access_token = 'pk.eyJ1IjoiYW5kcmVhYm90dGkiLCJhIjoiY2xuNDdybms2MHBvMjJqbm95aDdlZ2owcyJ9.-fs8J1enU5kC3L4mAJ5ToQ'

from fn__epw_read       import create_df_weather, epwab, strip_string_from_index, strip_string_from_columns
from fn__color_pools    import create_color_pools
from fn__create_charts  import calculate_and_plot_differences, generate_bar_bins_chart, generate_line_chart, generate_scatter_map_small
#
#
#
#
#
# PAGE CONFIG
st.set_page_config(page_title="ITACCA Streamlit App",   page_icon="🌡️", layout="wide")

st.markdown(
    """<style>.block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 3rem; padding-right: 3rem;}</style>""",
    unsafe_allow_html=True)
#
# TOP CONTAINER
top_col1, top_col2 = st.columns([6,1])
with top_col1:
    st.markdown("# ITA.C.C.A")
    st.markdown("#### Analisi di dati meteorologici ITAliani per facilitare l'Adattamento ai Cambiamenti Climatici")
    st.caption('Developed by AB.S.RD - https://absrd.xyz/')
#
#
#
#
#
#
# STREAMLIT SESSION STATE - LOAD DATA
df_SelectedLocations_CTI = st.session_state['df_SelectedLocations_CTI'] 
df_SelectedLocations_COB = st.session_state['df_SelectedLocations_COB']
selected_reg = st.session_state['selected_reg'] 
selected_region = st.session_state['selected_region']

df_CTI_DBT = st.session_state['df_CTI_DBT']
df_COB_DBT = st.session_state['df_COB_DBT']

color_marker_CTI = st.session_state['color_marker_CTI']
color_marker_COB = st.session_state['color_marker_COB']
#
#
#
#
#

with top_col2:
    try:
        image_path = './img/{r}.svg'.format(r=selected_reg)
        st.markdown('\n')
        st.image(image_path, width=170)
    except:
        ''

st.divider()
#
#
#
#
#
# SIDEBAR
with st.sidebar:
    st.markdown("""
        <style>
            div[data-testid="stSidebar"] .block-container {padding-top: 0rem;padding-bottom: 0rem;padding-left: 0rem;padding-right: 0rem;}
        </style>
        """, unsafe_allow_html=True)

    sel_month_COB = st.select_slider(
        'Scelta mesi per la visualizzazione',   options=np.arange(1,13,1),  value=(6,8))
    # st.sidebar.divider()
    lower_threshold = st.slider('Soglia per temperature massime (C)', min_value=20, max_value=40, step=1, value=25)
#
#
#
#
#
# TEMPERATURE PLOT
df_CTI_DBT_plot = df_CTI_DBT.copy()
df_COB_DBT_plot = df_COB_DBT.copy()
df_CTI_DBT_plot.columns = df_CTI_DBT_plot.columns.str.replace('DBT\|','')
df_CTI_DBT_plot = df_CTI_DBT_plot.convert_dtypes(convert_floating=True)
df_COB_DBT_plot = df_COB_DBT_plot.convert_dtypes(convert_floating=True)
#
#  Set datetime index
df_CTI_DBT_plot['datetime']=pd.to_datetime(df_CTI_DBT_plot.index)
df_CTI_DBT_plot.set_index(['datetime'], inplace=True, drop=True)
#
df_COB_DBT_plot['datetime']=pd.to_datetime(df_CTI_DBT_plot.index)
df_COB_DBT_plot.set_index(['datetime'], inplace=True, drop=True)
#
#
#
#
#
# Slicing Dataframes based on month chosen in the above sliders
year_plot = pd.DatetimeIndex(df_CTI_DBT_plot.index).year
year_plot = year_plot[0]
start_slice = '{y}-{m:02}-01'.format(y=year_plot, m=sel_month_COB[0])
end_slice   = '{y}-{m:02}-30'.format(y=year_plot, m=sel_month_COB[1])

df_CTI_DBT_plot = df_CTI_DBT_plot[start_slice:end_slice]
df_COB_DBT_plot = df_COB_DBT_plot[start_slice:end_slice]
#
#
#
#
#
sel_cols_CTI = []
for p in df_SelectedLocations_CTI.province:
    for c in df_CTI_DBT_plot.columns:
        DBT_province = c.split('__')[1]
        if DBT_province == p:
            sel_cols_CTI.append(c)
df_CTI_DBT_plot = df_CTI_DBT_plot[sel_cols_CTI]


sel_cols_COB = []
for f in df_SelectedLocations_COB.filename:
    num = re.search(r'\d+', f).group()
    f = f.rsplit('.epw')[0]
    f = f.rsplit(num)[-1]
    stringa = 'DBT__{}{}'.format(num,f)

    for c in df_COB_DBT.columns:
        if c == stringa:
            sel_cols_COB.append(c)

df_COB_DBT_plot = df_COB_DBT_plot.filter(sel_cols_COB)
#
#
#
#
#

#
#
#
#
#
# SIDEBAR
tab1, tab2, tab3 = st.tabs(["📈 CTI vs OneClimate TMY", "📈 CTI vs Meteostat", "🗃 CTI vs Future Data"])

with tab1:

    col1, spacing, col2 = st.columns([12,1,20])
    with col1:
        col11, col12 = st.columns([7,2])
        
        with col11:
            with st.container():
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
                df = df_SelectedLocations_CTI
                
                sel_province_CTI = st.radio('Seleziona Provincia', df.province, index=None)
                # sel_location_CTI = pills('Seleziona Provincia', df.province.to_list())

                df_sel = df[df['province'].isin([sel_province_CTI])]
                df_stations_CTI_line = df_sel
        with col12:
            st.markdown('.')
            try:
                sel_location_CTI = df_sel.city[0]
            except:
                sel_location_CTI = 'nessuna selezionata'
            original_title = '<p style="color:Green; font-size: 14px;">{}</p>'.format(sel_location_CTI)
            st.markdown(original_title, unsafe_allow_html=True)


    with col1:

        # BINS
        bins = list(range(0, 41, 5))
        color_palette = ['#A8E6CF', '#DCE775', '#FFD54F', '#FFB74D', '#FF8A65', '#EF5350', '#d21714', '#8c0f0d']

        def find_higher(x, y):
            min_val, max_val = min(x, y), max(x, y)
            return max_val
        bar_chart_CTI_height = find_higher(125, 25* df_SelectedLocations_CTI.shape[0] )
        bar_chart_COB_height = find_higher(125, 25* df_SelectedLocations_COB.shape[0] )

        fig_bar_bins_CTI = generate_bar_bins_chart(
            bins = bins,
            df=df_CTI_DBT_plot,
            color_palette=color_palette,
            chart_height=bar_chart_CTI_height,
            )
        st.plotly_chart(fig_bar_bins_CTI, use_container_width=True)


        df = df_SelectedLocations_COB
        sel_location_COB = st.radio('Seleziona stazione meteo - dati Climate OneBuilding', [f.split(selected_reg+'_')[-1] for f in df.filename], index=None)
        df_sel = df[df['filename'].isin(['ITA_{r}_{s}'.format(r=selected_reg,s=sel_location_COB)])]
        df_stations_COB_line = df_sel

        fig_bar_bins_COB = generate_bar_bins_chart(
            bins = bins,
            df=df_COB_DBT_plot,
            color_palette=color_palette,
            chart_height=bar_chart_COB_height,
            )
        st.plotly_chart(fig_bar_bins_COB, use_container_width=True)
        # st.write(df_stations_COB.values.flatten().tolist())
#
#
#
#
#
# COLOR POOLS
color_pools = create_color_pools(num_colors=400,num_pools=20)
color_pool_CTI = color_pools[4]
color_pool_COB = color_pools[16]
#
#
#
#
#
sel_cols_CTI_line = []
for p in df_stations_CTI_line.province:
    for c in df_CTI_DBT_plot.columns:
        DBT_province = c.split('__')[1]
        if DBT_province == p:
            sel_cols_CTI_line.append(c)
df_CTI_DBT_plot = df_CTI_DBT_plot[sel_cols_CTI_line]


sel_cols_COB_line = []
for f in df_stations_COB_line.filename:
    num = re.search(r'\d+', f).group()
    f = f.rsplit('.epw')[0]
    f = f.rsplit(num)[-1]
    stringa = 'DBT__{}{}'.format(num,f)

    for c in df_COB_DBT.columns:
        if c == stringa:
            sel_cols_COB_line.append(c)

df_COB_DBT_plot = df_COB_DBT_plot.filter(sel_cols_COB_line)



# LINE CHART
fig_line = generate_line_chart(
    color_marker_A = color_marker_CTI,
    color_marker_B = color_marker_COB,
    df_data_A = df_CTI_DBT_plot,
    df_data_B = df_COB_DBT_plot,
    color_pool_A = color_pool_CTI,
    color_pool_B = color_pool_COB,
    title_text='Temperature a Bulbo Secco - Stazioni in {r}'.format(r=selected_region),
    chart_height = 520,
    )
with tab1:
    with col2:
        st.plotly_chart(fig_line, use_container_width=True)
        # st.divider()#
#
#
#
#
#
#
#
#
#
try:
    df_CTI_filtered, df_COB_filtered, df_diff, fig_weekly, fig_monthly = calculate_and_plot_differences(
        threshold=lower_threshold, df_CTI=df_CTI_DBT_plot, df_COB=df_COB_DBT_plot,
        chart_height=250,
        )
except:
    fig_weekly, fig_monthly = go.Figure(), go.Figure()

with col1:
    col111, spacing, col112 = st.columns([18,1,12])

with tab1:

    with col2:
        st.divider()
        help_text = ':red[ROSSO] indica differenza positive di temperatura, ovvero _{cob} (COB)_ :red[più caldo] di _{cti} (CTI)_. \
            :blue[BLU] indica _{cob} (COB)_ :blue[più fresco] di _{cti} (CTI)_.'.format(
            cti=sel_location_CTI, cob=sel_location_COB, t=lower_threshold)
        st.markdown('##### Differenze di temperatura tra *{cti}* e *{cob}*'.format(cti=sel_location_CTI, cob=sel_location_COB),
                    help=help_text)
        st.caption('I valori riportati sono calcolati per le temperature massime, ovvero quelle superiori a **{t} C** come definito dall\'utente nella sidebar.'.format(t=lower_threshold)
        )
        # st.info('This is a purely informational message', icon="ℹ️")
        col21, spacing, col22 = st.columns([18,1,12])
        with col21:        
            st.plotly_chart(fig_weekly,use_container_width=True)
        with col22:
            st.plotly_chart(fig_monthly,use_container_width=True)



try:
    with col1:    
        map_COB__sel_lat = df_stations_COB_line.lat.to_list()
        map_COB__sel_lon = df_stations_COB_line.lon.to_list()
        map_COB__sel_location = df_stations_COB_line.filename.to_list()
        fig_small_01, fig_small_02 = generate_scatter_map_small(
            latitude_col=map_COB__sel_lat,
            longitude_col=map_COB__sel_lon,
            location_col=map_COB__sel_location,
            chart_height=250,
            marker_size=12,
            marker_color=color_marker_COB,
            zoom01=10,
            zoom02=14,
            mapbox_access_token = mapbox_access_token,
            )
        st.markdown('**Vista su mappa: {l}**'.format(l=map_COB__sel_location[0]))
        col_s1, col_s2 = st.columns([1,1])
        with col_s1:
            st.plotly_chart(fig_small_01, use_container_width=True)
        with col_s2:
            st.plotly_chart(fig_small_02, use_container_width=True)
except:
    ''






# Define CSS styles
radio_style = """
    <style>
        .spring-css-radio-widget .radio-inner {
            font-size: 10px !important;
        }
    </style>
"""

# tabs_font_css = """
# <style>
# div[class*="stTextArea"] label {
#   font-size: 26px;
#   color: red;
# }

# div[class*="stTextInput"] label {
#   font-size: 26px;
#   color: blue;
# }

# div[class*="stNumberInput"] label {
#   font-size: 26px;
#   color: green;
# }
# </style>
# """
