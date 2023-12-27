# IMPORT LIBRARIES
from imports import *
mapbox_access_token = 'pk.eyJ1IjoiYW5kcmVhYm90dGkiLCJhIjoiY2xuNDdybms2MHBvMjJqbm95aDdlZ2owcyJ9.-fs8J1enU5kC3L4mAJ5ToQ'

from fn__epw_read       import create_df_weather, epwab, strip_string_from_index, strip_string_from_columns
from fn__color_pools    import create_color_pools
from fn__create_charts  import calculate_and_plot_differences, generate_bar_bins_chart, generate_line_chart, generate_scatter_map_small, \
fetch_daily_data, fetch_hourly_data, bin_and_calculate_percentages, create_plotly_go_chart, create_plotly_express_chart, generate_temperature_bins_chart

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
TopColA, TopColB = st.columns([6,2])
with TopColA:
    st.markdown("# ITA.C.C.A")
    st.markdown("#### Analisi di dati meteorologici ITAliani per facilitare l'Adattamento ai Cambiamenti Climatici")
    st.caption('Developed by AB.S.RD - https://absrd.xyz/')
#
with TopColB:
    # Introduce vertical spaces
    st.markdown('<br><br>', unsafe_allow_html=True)

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
colA, spacing, colB = st.columns([14,1,60])
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
    st.markdown('###### Filtro dati per la visualizzazione')

    sel_month_COB = st.select_slider('Mese iniziale e mese finale',   options=np.arange(1,13,1),  value=(1,12))
    lower_threshold = st.slider('Temperatura min. per confronto dati', min_value=20, max_value=40, step=1, value=20)
#
#
#
#
#
# Adding Tabs in Column 22 for Different Charts
with colB:
    tab1, tab2, tab3, tab4 = st.tabs(["📈 CTI vs OneClimate TMY", "📈 CTI vs Meteostat", "🗃 CTI vs Future Data", 'All Data'])

    with tab1:
        st.session_state['active_tab'] = 'tab1'
        colB1, spacing, colB2 = st.columns([12,1,30])
        # colB1.markdown('_colB1_')
        # spacing.markdown('_sp_')
        # colB2.markdown('_colB2_')

        # Filter CTI and COB dataframes for plotting
        filtered__df_CTI_DBT_plot = df_CTI_DBT_plot.loc[:, [col for col in df_CTI_DBT_plot.columns if p in col[:2]]]
        wmo_code_selected = filtered_df_COB.wmo_code.to_list()


        try:
            df_CTI_filtered, df_COB_filtered, df_diff, fig_weekly, fig_monthly = calculate_and_plot_differences(
                threshold=lower_threshold,
                df1=filtered__df_CTI_DBT_plot,
                df2=filtered__df_COB_DBT_plot,
                color_cooler = color_marker_CTI, color_warmer=color_marker_COB, chart_height=320,
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
            '###### Differenze di temperatura tra: CTI e COB',
            help=help_text)
            st.caption('Valori calcolati per le temperature superiori a **{t} C**'.format(t=lower_threshold))

        colB1.plotly_chart(fig_monthly,use_container_width=True)


        # LINE CHART
        colB2.markdown('###### Temperature a Bulbo Secco per l\'anno tipo')
        fig_line_CTI_COB = generate_line_chart(
            color_marker_A = color_marker_CTI,
            color_marker_B = color_marker_COB,
            df_data_A = filtered__df_CTI_DBT_plot,
            df_data_B = filtered__df_COB_DBT_plot,
            color_pool_A = color_pool_CTI,
            color_pool_B = color_pool_COB,
            title_text = '',
            # title_text = 'Temperature a Bulbo Secco per l\'anno {}'.format(sel_year),
            chart_height = 380,
            )

        colB2.plotly_chart(fig_line_CTI_COB, use_container_width=True)




    with tab2:
        st.session_state['active_tab'] = 'tab2'
        colB1, spacing, colB2 = st.columns([12,1,30])
        # colB1.markdown('_colB1_')
        # spacing.markdown('_sp_')
        # colB2.markdown('_colB2_')

        with colA:
            sel_year_tab2 = st.slider(
                "Anno per visualizzare i dati Meteostat", 
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
            '###### Differenze di temperatura tra: CTI e MSTAT', help=help_text)
            st.caption('Valori calcolati per le temperature superiori a **{t} C**'.format(t=lower_threshold))

        colB1.plotly_chart(fig_monthly,use_container_width=True)



        # LINE CHART
        colB2.markdown('###### Temperature a Bulbo Secco per l\'anno {}'.format(sel_year))
        fig_line_CTI_MSTAT = generate_line_chart(
            color_marker_A = color_marker_CTI,
            color_marker_B = color_marker_MSTAT,
            df_data_A = filtered__df_CTI_DBT_plot,
            df_data_B = df__MSTAT_DBT_plot,
            color_pool_A = color_pool_CTI,
            color_pool_B = color_pool_COB,
            title_text = '',
            # title_text = 'Temperature a Bulbo Secco per l\'anno {}'.format(sel_year),
            chart_height = 380,
            )

        colB2.plotly_chart(fig_line_CTI_MSTAT, use_container_width=True)








    with tab3:
        st.session_state['active_tab'] = 'tab3'

        # Tab 3: Slider disabled (show static value)
        # st.text(f"Selected Year (disabled): {st.session_state['sel_year']}")

        colB1, spacing, colB2 = st.columns([12,1,30])

        # Fetch METEOSTAT data
    
    

        try:
            df_CTI_filtered, df_COB_filtered, df_diff, fig_weekly, fig_monthly = calculate_and_plot_differences(
                threshold=lower_threshold,
                df1=filtered__df_CTI_DBT_plot,
                df2=df__MSTAT_DBT_plot,
                color_cooler = color_marker_CTI, color_warmer=color_marker_FWG, chart_height=320,
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
            '###### Differenze di temperatura tra: CTI e FWG', help=help_text)
            st.caption('Valori calcolati per le temperature superiori a **{t} C**'.format(t=lower_threshold))

        colB1.plotly_chart(fig_monthly,use_container_width=True)


        # LINE CHART
        colB2.markdown('###### Temperature a Bulbo Secco per l\'anno tipo futuro')
        fig_line_CTI_FWG = generate_line_chart(
            color_marker_A = color_marker_CTI,
            color_marker_B = color_marker_FWG,
            df_data_A = filtered__df_CTI_DBT_plot,
            df_data_B = df__MSTAT_DBT_plot,
            color_pool_A = color_pool_CTI,
            color_pool_B = color_pool_COB,
            title_text = '',
            # title_text = 'Temperature a Bulbo Secco per l\'anno {}'.format(sel_year),
            chart_height = 380,
            )

        colB2.plotly_chart(fig_line_CTI_FWG, use_container_width=True)



#
#
#
#
#
# BINNING TEMPERATURE DATA

temperature_bins = list(range(0, 42, 5))


def display_color(hex_color):
    # Display a color box and its hex code
    st.markdown(f"""
        <div style='width: 100px; height: 20px; background: {hex_color};'></div>
        <p>{hex_color}</p>
        """, unsafe_allow_html=True)

# default_colors = ['blue', 'green', 'yellow', 'red']  # Example default colors
color_palette = [ '#b8c3d1', '#c0e0c7', '#DCE775', '#FFD54F', '#FFB74D', '#FF8A65', '#EF5350', '#D21714', '#8C0F0D']
hex_colors = color_palette

with st.sidebar:
    with st.expander(label='Schema colori'):
        st.caption('Palette lenght: {p} - bins lenght: {b}'.format(p=len(color_palette), b=len(temperature_bins)))

        # Display each color
        for color in hex_colors:
            display_color(color)




# Define temperature intervals and periods
df__FreqBars = df__MSTAT_DBT_plot
col_name = df__FreqBars.columns[0]
df__FreqBars['date'] = df__FreqBars.index

# Bin data and calculate percentages
binned_data_monthly = bin_and_calculate_percentages(temperature_data=df__FreqBars,  temperature_col= col_name,  intervals=temperature_bins, period='M')
binned_data_weekly = bin_and_calculate_percentages(temperature_data=df__FreqBars,  temperature_col= col_name,  intervals=temperature_bins, period='W')

fig__temp_bins_freq_monthly = create_plotly_express_chart(data=binned_data_monthly,   bins=temperature_bins, colors=color_palette, bar_gap=0.30, chart_height=150)
fig__temp_bins_freq_weekly  = create_plotly_express_chart(data=binned_data_weekly,    bins=temperature_bins, colors=color_palette, bar_gap=0.00, chart_height=150)


# with colB:
#     st.markdown('<br>',unsafe_allow_html=True)
#     st.markdown('###### Frequenza di temperature mensili e settimanali')

#     colB_monthly, colB_weekly = st.columns([3,7])
#     colB_monthly.plotly_chart(fig__temp_bins_freq_monthly, use_container_width=True)
#     colB_weekly.plotly_chart(fig__temp_bins_freq_weekly, use_container_width=True)

# 


def filter_rows_by_threshold(df, column_name, threshold):
    # Function to extract numbers from a string and check if they meet the condition
    def numbers_meet_threshold(s):
        numbers = [int(num) for num in re.findall(r'\d+', s)]
        return all(num >= threshold for num in numbers)

    # Apply the function to the specified column and filter the DataFrame
    return df[df[column_name].apply(numbers_meet_threshold)]





frames = {'CTI' : filtered__df_CTI_DBT_plot,    'COB' : filtered__df_COB_DBT_plot,    'MSTAT' : df__MSTAT_DBT_plot,}
# for key, value in frames.items():
#     print("key: ", key)
#     print(frames[key], "\n")


with tab4:

    AllData__grouped_by_month = pd.DataFrame()

    tab4A, tab4B = st.tabs(["CHARTS", "TABLE"])

    for key, value in frames.items():

        df__FreqBars = frames[key]

        # Define temperature intervals and periods
        col_name = df__FreqBars.columns[0]

        df__FreqBars['date'] = df__FreqBars.index

        # Bin data and calculate percentages
        binned_data_monthly = bin_and_calculate_percentages(temperature_data=df__FreqBars,  temperature_col= col_name,  intervals=temperature_bins, period='M')
        binned_data_weekly = bin_and_calculate_percentages(temperature_data=df__FreqBars,  temperature_col= col_name,  intervals=temperature_bins, period='W')

        fig__temp_bins_freq_monthly = create_plotly_express_chart(data=binned_data_monthly,   bins=temperature_bins, colors=color_palette, bar_gap=0.20, chart_height=180)
        fig__temp_bins_freq_weekly  = create_plotly_express_chart(data=binned_data_weekly,    bins=temperature_bins, colors=color_palette, bar_gap=0.00, chart_height=180)



        # Filter rows where 'col_to_check' is greater than SOGLIA
        df = df__FreqBars
        filtered_df = df[df[col_name] > lower_threshold]

        grouped_by_month = filtered_df.groupby(pd.Grouper(freq='M')).count()    # or use another aggregation function
        grouped_by_month.index = grouped_by_month.index.strftime('%B')          # Convert the index to month names
        grouped_by_month = grouped_by_month[[col_name]]
        # grouped_by_month.rename(columns={grouped_by_month.columns[0]:'Hours > {}'.format(lower_threshold)}, inplace=True)

        AllData__grouped_by_month = pd.concat([AllData__grouped_by_month,grouped_by_month], axis=1)
                                              
        # Convert DataFrame to a string while maintaining the table structure
        df_string = grouped_by_month.to_string(index=True, header=True, justify='right')


        with tab4A:
            colB_title, colB_stats, colB_monthly, colB_weekly = st.columns([10,1,25,40])
            colB_title.markdown('###### {}'.format(key))
            colB_title.caption('{}'.format(col_name))
            # colB_stats.table(grouped_by_month)

            colB_monthly.plotly_chart(fig__temp_bins_freq_monthly, use_container_width=True)
            colB_weekly.plotly_chart(fig__temp_bins_freq_weekly, use_container_width=True)

    with tab4B:
        st.markdown('###### Numero di ore in cui le Temperature eccedono il valore di {} C'.format(lower_threshold))
        st.dataframe(AllData__grouped_by_month)