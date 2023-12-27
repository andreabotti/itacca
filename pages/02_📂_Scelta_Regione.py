# IMPORT LIBRARIES
from imports import *
mapbox_access_token = 'pk.eyJ1IjoiYW5kcmVhYm90dGkiLCJhIjoiY2xuNDdybms2MHBvMjJqbm95aDdlZ2owcyJ9.-fs8J1enU5kC3L4mAJ5ToQ'
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
dict_regions = st.session_state['dict_regions']
regions_list = st.session_state['regions_list']

geojson_italy_regions = st.session_state['geojson_italy_regions']
geojson_italy_provinces = st.session_state['geojson_italy_provinces']

df_CTI_DBT = st.session_state['df_CTI_DBT']
df_COB_DBT = st.session_state['df_COB_DBT']
#
#
#
#
#
# Region Selection
selected_region = st.sidebar.selectbox("Selezionare la regione:", regions_list)
color_marker_CTI = st.sidebar.color_picker('Colore per marker CTI', '#71A871')
color_marker_COB = st.sidebar.color_picker('Colore per marker COB', '#E07E34')
#
# Filter CTI and COB stations based on selected region
selected_reg = [i for i in dict_regions if dict_regions[i]==selected_region][0]
df_SelectedLocations_COB = df_locations_COB[df_locations_COB.reg == selected_reg]
df_SelectedLocations_CTI = df_locations_CTI[df_locations_CTI.region == selected_region]
#
df_TablePlot_CTI = df_SelectedLocations_CTI
df_TablePlot_COB = df_SelectedLocations_COB
try:
    df_TablePlot_COB.drop(['location'], axis=1, inplace=True)
except:
    ''
df_TablePlot_CTI = df_TablePlot_CTI[['province', 'city', 'lat', 'lon', 'alt']]
df_TablePlot_COB.drop(['reg'], axis=1, inplace=True)
n = df_TablePlot_CTI.shape[0]
#
#
#
#
#
image_path = './img/{r}.svg'.format(r=selected_reg)
with top_col2:
    st.markdown('\n')
    st.image(image_path, width=170)

st.sidebar.markdown('\n')
st.sidebar.image(image_path, width=220)

st.divider()
#
#
#
#
#
# COLUMNS AND LAYOUT
col1, space1, col2, space2, col3 = st.columns([18,1,15,1,25])

with col1:
    # Calculate the centroid of the provided data points
    center_latitude = sum(df_SelectedLocations_CTI.lat) / len(df_SelectedLocations_CTI.lat)
    center_longitude = sum(df_SelectedLocations_CTI.lon) / len(df_SelectedLocations_CTI.lon)

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

    st.markdown('##### Mappa delle stazioni meteo in {r}'.format(r=selected_region))
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

st.session_state['color_marker_CTI'] = color_marker_CTI
st.session_state['color_marker_COB'] = color_marker_COB
