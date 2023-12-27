# IMPORT LIBRARIES
from imports import *
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
# STREAMLIT SESSION STATE - LOAD DATA
df_locations_CTI = st.session_state['df_locations_CTI']
df_locations_COB = st.session_state['df_locations_COB']
df_locations_COB_capo = st.session_state['df_locations_COB_capo']

dict_regions = st.session_state['dict_regions']
regions_list = st.session_state['regions_list']
df_capoluoghi = st.session_state['df_capoluoghi']

geojson_italy_regions = st.session_state['geojson_italy_regions']
geojson_italy_provinces = st.session_state['geojson_italy_provinces']

df_CTI_DBT = st.session_state['df_CTI_DBT']
df_COB_DBT = st.session_state['df_COB_DBT']
df__COB_capo__DBT = st.session_state['df__COB_capo__DBT']
#
#
#
#
#
color_marker_CTI = st.sidebar.color_picker('Colore per marker CTI', '#71A871')
color_marker_COB = st.sidebar.color_picker('Colore per marker COB', '#E07E34')

col2, col3 = st.columns([8,15])

# n = df_locations_CTI.shape[0]
try:
    df_locations_CTI.set_index('reg', inplace=True)
except:
    ''
try:
    df_locations_COB.drop(['location'], axis=1, inplace=True) 
except:
    ''

with st.sidebar:
    sel_month_COB = st.select_slider(
        'Scelta mesi per la visualizzazione',   options=np.arange(1,13,1),  value=(6,8))
    # st.sidebar.divider()
    lower_threshold = st.slider('Soglia per isolare temperature massime (C)', min_value=20, max_value=40, step=1, value=30)





# TEMPERATURE PLOT
df_CTI_DBT_plot = df_CTI_DBT.copy()
df_COB_DBT_plot = df__COB_capo__DBT.copy()
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

df_CTI_DBT_plot.rename(columns=lambda x: x.split('__',1)[-1], inplace=True)

#
#
#
#
#
# Load the Italian provinces GeoJSON
url = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_provinces.geojson"
provinces = gpd.read_file(url)

# Convert the dataframe with weather stations to a GeoDataFrame
df = df_locations_COB_capo
gdf_stations = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.lon, df.lat),
    crs=provinces.crs,
    )

# Perform a spatial join to determine the province for each weather station
df_mapped = gpd.sjoin(gdf_stations, provinces, how="left", op="within")
df_mapped.drop(['geometry'], axis=1, inplace=True)

# Filter rows in df_mapped based on condition
filtered_df_mapped = df_mapped[df_mapped['prov_acr'].isin(df_capoluoghi['province'])]



# COLOR POOLS
color_pools = create_color_pools(num_colors=400,num_pools=20)
color_pool_CTI = color_pools[4]
color_pool_COB = color_pools[16]



for p in sorted(df_capoluoghi.province):

    filtered_df_COB = filtered_df_mapped[filtered_df_mapped['prov_acr'].str.contains(p)]
    filtered_df_CTI = df_locations_CTI[df_locations_CTI['province'].str.contains(p)]

    col21, spacing, col22 = st.columns([6,1,18])


    col22.markdown('---')
    try:
        prov_name = filtered_df_COB.prov_name.to_list()[0]
    except:
        prov_name = None

#
    map_COB__sel_lat, map_COB__sel_lon, map_COB__sel_location = [42], [15], []
    try:
        map_COB__sel_lat = filtered_df_COB.lat.to_list()
        map_COB__sel_lon = filtered_df_COB.lon.to_list()
        map_COB__sel_location = filtered_df_COB.filename.to_list()
    except:
        ''
        #
    try:
        fig_small_221, fig_small_222 = generate_scatter_map_small(
            latitude_col=map_COB__sel_lat,
            longitude_col=map_COB__sel_lon,
            location_col=map_COB__sel_location,
            chart_height=310,
            marker_size=10,     marker_color=color_marker_COB,
            zoom01=10,          zoom02=12,
            mapbox_access_token = mapbox_access_token,
            )
    except:
        fig_small_221, fig_small_222 = go.Figure(), go.Figure()


    # Filter CTI and COB dataframes for plotting
    filtered__df_CTI_DBT_plot = df_CTI_DBT_plot.loc[:, [col for col in df_CTI_DBT_plot.columns if p in col[:2]]]
    wmo_code_selected = filtered_df_COB.wmo_code.to_list()

    filtered__df_COB_DBT_plot = pd.DataFrame()    
    for wmo in wmo_code_selected:
        df_sel = df_COB_DBT_plot.loc[:, [col for col in df_COB_DBT_plot.columns if wmo in col[:6]]]
        filtered__df_COB_DBT_plot = pd.concat([filtered__df_COB_DBT_plot, df_sel], axis=1)


    # LINE CHART
    fig_line = generate_line_chart(
        color_marker_A = color_marker_CTI,
        color_marker_B = color_marker_COB,
        df_data_A = filtered__df_CTI_DBT_plot,
        df_data_B = filtered__df_COB_DBT_plot,
        color_pool_A = color_pool_CTI,
        color_pool_B = color_pool_COB,
        title_text = 'Temp Bulbo Secco',
        chart_height = 350,
        )


    col21.markdown('---')
    col21.markdown('##### _Provincia: {p1} \({p2}\)_'.format(p2=p, p1=prov_name))
    col21.plotly_chart(fig_small_221, use_container_width=True)    
    #
    col22.plotly_chart(fig_line, use_container_width=True)

