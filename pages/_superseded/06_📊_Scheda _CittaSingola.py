# IMPORT LIBRARIES
from imports import *
mapbox_access_token = 'pk.eyJ1IjoiYW5kcmVhYm90dGkiLCJhIjoiY2xuNDdybms2MHBvMjJqbm95aDdlZ2owcyJ9.-fs8J1enU5kC3L4mAJ5ToQ'

from fn__epw_read       import create_df_weather, epwab, strip_string_from_index, strip_string_from_columns
from fn__color_pools    import create_color_pools
from fn__create_charts  import calculate_and_plot_differences, generate_bar_bins_chart, generate_line_chart, generate_scatter_map_small, fetch_daily_data, fetch_hourly_data

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
# Initialize session state for the slider value if not already set
if 'sel_year' not in st.session_state:
    st.session_state['sel_year'] = 2023

# Define a variable to track the active tab
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 'tab1'
#
#
#
#
#
# TOP CONTAINER
TopColA, TopColB = st.columns([6,2])
with TopColA:
    st.markdown("# ITA.C.C.A")
    st.markdown("#### Analisi di dati meteorologici ITAliani per facilitare l'Adattamento ai Cambiamenti Climatici")
    st.caption('Developed by AB.S.RD - https://absrd.xyz/')


with TopColB:
    # Introduce vertical spaces
    st.markdown('<br>', unsafe_allow_html=True)

    with st.container(border=True):
        # Your content here
        st.markdown('###### Scegli colore dei markers')
        TopColB1, TopColB2, TopColB3, TopColB4 = st.columns([1,1,1,1])
        with TopColB1:
            color_marker_CTI = st.color_picker(
                'CTI', '#C4C5C4', help='**CTI = Comitato Termotecnico Italiano** : dati climatici rappresentativi (*anno tipo*) del recente passato',
                )
        with TopColB2:
            color_marker_COB = st.color_picker(
                'COB', '#E2966D', help='**COB = climate.onebuilding.org** : dati climatici rappresentativi (*anno tipo*) del presente',
                )
        with TopColB3:
            color_marker_MSTAT = st.color_picker(
                'MSTAT', '#85A46E', help='**MSTAT = Meteostat** : dati climatici (*anni reali*) del recente passato e presente',
                )
        with TopColB4:
            color_marker_FWG = st.color_picker(
                'FWG', '#6C90AF', help='**FWG = Future Weather Generator** : dati climatici (*anno tipo*) rappresentativi di proiezioni future in linea con gli scenari IPCC',
                )

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
col2, col3 = st.columns([8,15])
try:
    df_locations_CTI.set_index('reg', inplace=True)
except:
    ''
try:
    df_locations_COB.drop(['location'], axis=1, inplace=True) 
except:
    ''
#
#
#
#
#
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
colA, spacing, colB = st.columns([12,1,60])
# colA.markdown('_colA_')
# spacing.markdown('_s_')
# colB.markdown('_colB_')
#
#
#
#
#
# Dropdown for Province Selection
with colA:
    selected_province = st.selectbox("Seleziona una provincia", options=sorted(df_capoluoghi.province), index=4)

p = selected_province
filtered_df_COB = filtered_df_mapped[filtered_df_mapped['prov_acr'].str.contains(p)]
filtered_df_CTI = df_locations_CTI[df_locations_CTI['province'].str.contains(p)]

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
#
#
#
#
try:
    fig_small_221, fig_small_222 = generate_scatter_map_small(
        latitude_col=map_COB__sel_lat,
        longitude_col=map_COB__sel_lon,
        location_col=map_COB__sel_location,
        chart_height=230,
        marker_size=10, marker_color=color_marker_COB,
        zoom01=10, zoom02=12,
        mapbox_access_token = mapbox_access_token,
        )
except:
    fig_small_221, fig_small_222 = go.Figure(), go.Figure()
#
#
#
#
#
# Filter CTI and COB dataframes for plotting
filtered__df_CTI_DBT_plot = df_CTI_DBT_plot.loc[:, [col for col in df_CTI_DBT_plot.columns if p in col[:2]]]
wmo_code_selected = filtered_df_COB.wmo_code.to_list()

filtered__df_COB_DBT_plot = pd.DataFrame()    
for wmo in wmo_code_selected:
    df_sel = df_COB_DBT_plot.loc[:, [col for col in df_COB_DBT_plot.columns if wmo in col[:6]]]
    filtered__df_COB_DBT_plot = pd.concat([filtered__df_COB_DBT_plot, df_sel], axis=1)
#
#
#
#
#
# LINE CHART
fig_line = generate_line_chart(
    color_marker_A = color_marker_CTI,
    color_marker_B = color_marker_COB,
    df_data_A = filtered__df_CTI_DBT_plot,
    df_data_B = filtered__df_COB_DBT_plot,
    color_pool_A = color_pool_CTI,
    color_pool_B = color_pool_COB,
    title_text = 'Temp Bulbo Secco',
    chart_height = 400,
    )
#
#
#
#
#
colA.markdown('###### Provincia: {p1} \({p2}\)'.format(p2=p, p1=prov_name))
colA.plotly_chart(fig_small_221, use_container_width=True) 
#
#
#
#
#
with colA:
    st.markdown('\n')
    st.markdown('##### Filtro dati per la visualizzazione')

    sel_month_COB = st.select_slider('Mese iniziale e mese finale',   options=np.arange(1,13,1),  value=(1,12))
    lower_threshold = st.slider('Soglia temperature max. per calcolo differenze', min_value=20, max_value=40, step=1, value=20)
#
#
#
#
#
# Place the slider in colA and control its interactivity based on the active tab
with colA:
    if st.session_state['active_tab'] == 'tab2':
        # Enable slider in tab2
        sel_year = st.slider(
            "Anno per visualizzare i dati Meteostat", 
            min_value=2010, 
            max_value=datetime.now().year, 
            value=st.session_state['sel_year'],
            help='I dati climatici **CTI** esprimono valori medi...'
        )
        st.session_state['sel_year'] = sel_year
    else:
        # Show slider value but disabled in other tabs
        st.slider(
            "Anno per visualizzare i dati Meteostat", 
            min_value=2010, 
            max_value=datetime.now().year, 
            value=st.session_state['sel_year'],
            disabled=True,
            help='I dati climatici **CTI** esprimono valori medi...'
        )

# ... [Rest of your existing code]


# Adding Tabs in Column 22 for Different Charts
with colB:
    tab1, tab2, tab3 = st.tabs(["📈 CTI vs OneClimate TMY", "📈 CTI vs Meteostat", "🗃 CTI vs Future Data"])

    with tab1:
        st.session_state['active_tab'] = 'tab1'
        # Include content for "CTI vs OneClimate TMY"
        st.plotly_chart(fig_line, use_container_width=True)


    with tab2:
        st.session_state['active_tab'] = 'tab2'
        colB1, spacing, colB2 = st.columns([12,1,30])
        # colB1.markdown('_colB1_')
        # spacing.markdown('_sp_')
        # colB2.markdown('_colB2_')

        with colA:
            sel_year_tab2 = st.slider(
                "Anno per visualizzare i dati Meteostat (enabled)", 
                min_value=2010, 
                max_value=datetime.now().year, 
                value=st.session_state['sel_year'], 
                key="sel_year2",
                help='I dati climatici **CTI** esprimono valori medi - non legati ad un anno preciso. La serie temporale CTI viene *trasportata* (senza variazione di valori) all\'anno scelto per permettere confronto visivo con i dati **Meteostat**'
            )
        st.session_state['sel_year'] = sel_year_tab2
        sel_year = sel_year_tab2
        start_date = datetime(sel_year, 1, 1)
        end_date = datetime(sel_year, 12, 31)

        # Fetch METEOSTAT data
        MSTAT_daily_data = fetch_daily_data(latitude=map_COB__sel_lat, longitude=map_COB__sel_lon, start_date=start_date, end_date=end_date)
        MSTAT_hourly_data = fetch_hourly_data(latitude=map_COB__sel_lat, longitude=map_COB__sel_lon, start_date=start_date, end_date=end_date)

        df__MSTAT_DBT_plot = MSTAT_hourly_data.loc[:,['temp']]
        df__MSTAT_DBT_plot.rename(columns={"temp": 'DBT__{}_MSTAT'.format(p)}, inplace=True, errors="raise")

        # Filter CTI and COB dataframes for plotting
        df_CTI_DBT_plot.index = df_CTI_DBT_plot.index.map(lambda x: x.replace(year=sel_year))
        filtered__df_CTI_DBT_plot = df_CTI_DBT_plot.loc[:, [col for col in df_CTI_DBT_plot.columns if p in col[:2]]]
        wmo_code_selected = filtered_df_COB.wmo_code.to_list()


        try:
            df_CTI_filtered, df_COB_filtered, df_diff, fig_weekly, fig_monthly = calculate_and_plot_differences(
                threshold=lower_threshold,
                df1=filtered__df_CTI_DBT_plot,
                df2=df__MSTAT_DBT_plot,
                color_cooler = color_marker_CTI, color_warmer=color_marker_MSTAT, chart_height=320,
                )
        except:
            fig_weekly, fig_monthly = go.Figure(), go.Figure()

        sel_location_CTI = selected_province
        sel_location_COB = selected_province


        colB1, spacing, colB2 = st.columns([12,1,30])


        with colB1:
            help_text = ':red[ROSSO] indica differenza positive di temperatura, ovvero _{cob} (COB)_ :red[più caldo] di _{cti} (CTI)_. \
                :blue[BLU] indica _{cob} (COB)_ :blue[più fresco] di _{cti} (CTI)_.'.format(
                cti=sel_location_CTI, cob=sel_location_COB, t=lower_threshold)

            st.markdown(
            '##### Differenze di temperatura tra: *{cti}* e *{cob}*'.format(cti=sel_location_CTI, cob=sel_location_COB),
            help=help_text)
            st.caption(
                'Valori calcolati per le temperature superiori a **{t} C**'.format(t=lower_threshold)
            )

        colB1.plotly_chart(fig_monthly,use_container_width=True)



        # LINE CHART
        colB2.markdown('##### Temperature a Bulbo Secco per l\'anno {}'.format(sel_year))
        fig_line_2 = generate_line_chart(
            color_marker_A = color_marker_CTI,
            color_marker_B = color_marker_MSTAT,
            df_data_A = filtered__df_CTI_DBT_plot,
            df_data_B = df__MSTAT_DBT_plot,
            color_pool_A = color_pool_CTI,
            color_pool_B = color_pool_COB,
            title_text = '',
            # title_text = 'Temperature a Bulbo Secco per l\'anno {}'.format(sel_year),
            chart_height = 460,
            )

        colB2.plotly_chart(fig_line_2, use_container_width=True)






    with tab3:
        st.session_state['active_tab'] = 'tab3'

        # Tab 3: Slider disabled (show static value)
        st.text(f"Selected Year (disabled): {st.session_state['sel_year']}")

        colB1, spacing, colB2 = st.columns([12,1,30])

        # Fetch METEOSTAT data
        MSTAT_daily_data = fetch_daily_data(latitude=map_COB__sel_lat, longitude=map_COB__sel_lon, start_date=start_date, end_date=end_date)
        MSTAT_hourly_data = fetch_hourly_data(latitude=map_COB__sel_lat, longitude=map_COB__sel_lon, start_date=start_date, end_date=end_date)

        df__MSTAT_DBT_plot = MSTAT_hourly_data.loc[:,['temp']]
        df__MSTAT_DBT_plot.rename(columns={"temp": 'DBT__{}_MSTAT'.format(p)}, inplace=True, errors="raise")

        # Filter CTI and COB dataframes for plotting
        df_CTI_DBT_plot.index = df_CTI_DBT_plot.index.map(lambda x: x.replace(year=sel_year))
        filtered__df_CTI_DBT_plot = df_CTI_DBT_plot.loc[:, [col for col in df_CTI_DBT_plot.columns if p in col[:2]]]
        wmo_code_selected = filtered_df_COB.wmo_code.to_list()


        try:
            df_CTI_filtered, df_COB_filtered, df_diff, fig_weekly, fig_monthly = calculate_and_plot_differences(
                threshold=lower_threshold,
                df1=filtered__df_CTI_DBT_plot,
                df2=df__MSTAT_DBT_plot,
                color_cooler = color_marker_CTI, color_warmer=color_marker_MSTAT, chart_height=320,
                )
        except:
            fig_weekly, fig_monthly = go.Figure(), go.Figure()

        sel_location_CTI = selected_province
        sel_location_COB = selected_province


        colB1, spacing, colB2 = st.columns([12,1,30])

        with colB1:
            help_text = ':red[ROSSO] indica differenza positive di temperatura, ovvero _{cob} (COB)_ :red[più caldo] di _{cti} (CTI)_. \
                :blue[BLU] indica _{cob} (COB)_ :blue[più fresco] di _{cti} (CTI)_.'.format(
                cti=sel_location_CTI, cob=sel_location_COB, t=lower_threshold)

            st.markdown(
            '##### Differenze di temperatura tra: *{cti}* e *{cob}*'.format(cti=sel_location_CTI, cob=sel_location_COB),
            help=help_text)
            st.caption(
                'Valori calcolati per le temperature superiori a **{t} C**'.format(t=lower_threshold)
            )

        colB1.plotly_chart(fig_monthly,use_container_width=True)



        # LINE CHART
        colB2.markdown('##### Temperature a Bulbo Secco per l\'anno {}'.format(sel_year))
        fig_line_2 = generate_line_chart(
            color_marker_A = color_marker_CTI,
            color_marker_B = color_marker_MSTAT,
            df_data_A = filtered__df_CTI_DBT_plot,
            df_data_B = df__MSTAT_DBT_plot,
            color_pool_A = color_pool_CTI,
            color_pool_B = color_pool_COB,
            title_text = '',
            # title_text = 'Temperature a Bulbo Secco per l\'anno {}'.format(sel_year),
            chart_height = 460,
            )

        colB2.plotly_chart(fig_line_2, use_container_width=True)


