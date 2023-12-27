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
# LOCAL_PATH  = r'C:/_OneDrive/OPEN PROJECT SRL/Sostenibilita - Documents/01__Ricerca/10__LCA_Carbon/17__LCA_Coding/01__ITACCA/data/'
LOCAL_PATH  = r'C:/_GitHub/andreabotti/itacca/data/'
FTP_PATH    = r'https://absrd.xyz/streamlit_apps/_weather_data/'
MAIN_PATH = FTP_PATH
#
#
#
#
#
# Load Data
url__cti__dbt = MAIN_PATH + 'CTI__AllStations__DBT.csv'
url__cob__dbt = MAIN_PATH + 'COB__SelWeatherStations__DBT.csv'

url__cti__df_capoluoghi = MAIN_PATH + 'CTI__capoluoghi.csv'
url__cti__dbt__capoluoghi = MAIN_PATH + 'COB__SelWeatherStations__Capoluoghi__DBT.csv'

url__cti__dict_regions      = MAIN_PATH + 'CTI__dict__Regions.json'
url__cti__geoson_regions    = MAIN_PATH + 'limits_IT_regions.geojson'
url__cti__geoson_provinces  = MAIN_PATH + 'limits_IT_provinces.geojson'

url__CTI__stations  = MAIN_PATH + 'CTI__WeatherStations.csv'
url__COB__stations  = MAIN_PATH + 'COB__SelWeatherStations.csv'
url__COB_capo__stations  = MAIN_PATH + 'COB__CapoWeatherStations.csv'
#
#
#
#
#
@st.cache_resource
def LoadData__locations_CTI_COB():
    df_CTI = pd.read_csv(url__CTI__stations)
    df_COB = pd.read_csv(url__COB__stations)
    df_COB_capo = pd.read_csv(url__COB_capo__stations)
    return df_CTI, df_COB, df_COB_capo

df_locations_CTI,df_locations_COB, df_locations_COB_capo = LoadData__locations_CTI_COB()

# Load Capoluoghi dataframe
@st.cache_resource
def LoadData__capoluoghi():
    df = pd.read_csv(url__cti__df_capoluoghi, index_col=False, keep_default_na=False)
    return df
df_capoluoghi = LoadData__capoluoghi()


# Load DBT for CTI and COB datasets
@st.cache_resource
def LoadData__DBT__CTI_COB__all():
    df_CTI = pd.read_csv(url__cti__dbt,index_col='datetime')
    df_COB = pd.read_csv(url__cob__dbt)
    return df_CTI, df_COB

df_CTI_DBT, df_COB_DBT = LoadData__DBT__CTI_COB__all()


# Load DBT for Capoluoghi selected COB datasets
@st.cache_resource
def LoadData__DBT__COB__capoluoghi():
    df = pd.read_csv(url__cti__dbt__capoluoghi)
    return df

df__COB_capo__DBT = LoadData__DBT__COB__capoluoghi()



# Load TopoJSON
@st.cache_resource
def LoadData_regions_provinces():
    json_file = json.loads(requests.get(url__cti__geoson_regions).text)
    geojson_italy_regions = json_file

    json_file = json.loads(requests.get(url__cti__geoson_provinces).text)
    geojson_italy_provinces = json_file
    return geojson_italy_regions, geojson_italy_provinces

geojson_italy_regions, geojson_italy_provinces = LoadData_regions_provinces()
#
#
#
#
#


#
#
# DICT REGIONS
cti__dict_regions = {
    "AB":"Abruzzo",         "BC":"Basilicata",          "CM":"Campania",
    "CL":"Calabria",        "ER":"Emilia Romagna",      "FV":"Friuli Venezia Giulia",
    "LZ":"Lazio",           "LG":"Liguria",             "LM":"Lombardia",
    "MH":"Marche",          "ML":"Molise",              "PM":"Piemonte",
    "PU":"Puglia",          "SD":"Sardegna",            "SC":"Sicilia",
    "TC":"Toscana",         "TT":"Trentino Alto Adige", "UM":"Umbria",
    "VD":"Valle dAosta",    "VN":"Veneto"
    }
dict_regions = pd.read_json( url__cti__dict_regions, typ='series')
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
df_locations_COB_capo['wmo_code'] = df_locations_COB_capo['wmo_code'].astype(str) 
df_locations_COB_capo = df_locations_COB_capo[ ['reg', 'location', 'filename', 'wmo_code', 'lat', 'lon','alt'] ]


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
st.session_state['df_locations_COB_capo'] = df_locations_COB_capo

st.session_state['df_CTI_DBT'] = df_CTI_DBT
st.session_state['df_COB_DBT'] = df_COB_DBT
st.session_state['df__COB_capo__DBT'] = df__COB_capo__DBT

st.session_state['df_reg'] = df_reg_short
st.session_state['geojson_italy_regions'] = geojson_italy_regions
st.session_state['geojson_italy_provinces'] = geojson_italy_provinces

st.session_state['dict_regions'] = dict_regions
st.session_state['regions_list'] = regions_list

st.session_state['df_capoluoghi'] = df_capoluoghi
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
current_work_dir = os.getcwd()
# st.caption('Working from path: {}'.format(current_work_dir), unsafe_allow_html=True)

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
col1, spacing, col2 = st.columns([9,1,12])

with col1:
    # st.markdown('#### Scopo di questa app')
    st.write('Lo scopo di questa app ITA.C.C.A è quello di colmare alcune **lacune** esistenti rispetto alla disponibilità, all\'interno di standards tecnici e normativi italiani \
              di **dati climatici** capaci di descrivere accuratamente gli **impatti presenti e futuri del cambiamento climatico** nelle varie zone del territorio Italiano.')
    st.write('Questo risulta di importanza capitale per informare la progettazione edile ed impiantistica degli edifici di varie destinazioni d\'uso, \
             e per valutarne il comportamento termico **con particolare riguardo al periodo estivo**.')

    st.divider()
    st.markdown('##### Come utilizzare l\'app:')
    st.markdown('1 Scegliere la regione italiana per visualizzare stazioni meteo disponibili rispetto alle banche dati CTI (*Comitato Termotecnico Italiano*) e COB (*climate.onebuilding.org*)')
    st.code('📂 Scelta Regione')
    st.markdown('2 Scegliere, esplorare e confrontare i dati di temperatura secondo i files normativi italiani (CTI) e quelli piu\' recenti, forniti dal dataset COB. \
                Laddove i dati climatici dei due *datasets* per le stesse località indicano discrepanze significative, la progettazione impiantistica e la modellazione energetica \
                elaborate secondo i dati CTI rischiano di non essere adeguate')
    st.code('📂 Confronto Dati Province')




with col2:
    tab1, tab2, tab3 = st.tabs([":file_cabinet: Il Passato Recente", ":world_map: Il Presente", ":thermometer: Il Futuro"])

with tab1:
    st.markdown('##### Il passato: Anni Tipo Climatici del Comitato Termotecnico Italiano \(CTI\)')
    st.write('Gli anni tipo climatici - *Test Reference Years (TRY)* o *Typical Meteorological Year (TMY)* - vengono forniti dal \
             **Comitato Termotecnico Italiano (CTI)** per 110 località di riferimento distribuite sul territorio nazionale e rappresentano i dati standard \
             ai fini del soddisfacimento della normativa energetica \
             L\'anno tipo climatico consiste in 12 mesi caratteristici scelti da un database di dati meteorologici di un periodo preferibilmente ampio almeno 10 anni.')

    # st.divider()
    with st.expander('*Per avere più dettagli sugli anni tipo climatici - banca dati CTI*'):
        st.write('\n'.join(cti_try_descr01))
        st.write('\n'.join(cti_try_descr02))
        st.caption('Fonte: https://try.cti2000.it/')

    st.divider()
    st.markdown('##### Ulteriori informazioni')
    st.markdown("*What is weather data, and how is it collected?*[https://docs.ladybug.tools/ladybug-tools-academy/v/climate-analysis/]",
                unsafe_allow_html=True)



with tab2:
    st.markdown('##### Il presente: anni tipici recenti dalla banca dati di *climate.onebuilding.org* \(COB\)')
    st.write('The weather data - *Typical Meteorological Years TMYx* - provided at https://climate.onebuilding.org/ are derived from a number of public sources, and produced by translating the source data into the EPW format. \
        TMYx files are typical meterological files derived from ISD \(US NOAA\'s Integrated Surface Database\) with hourly data through 2021 using the TMY/ISO 15927-4:2005 methodologies. \
        ISD individual year files are created using the general principles from the IWEC (International Weather for Energy Calculations) Typical Meteorological Years that was published in 2001. \
        The ERA5 data, courtesy of Oikolab, provides a comprehensive, worldwide gridded solar radiation data set based on satellite data.')
    st.write('For each location, the TMYx file structure \'EGY_AN_Aswan.Intl.AP.624140_TMYx.2007-2021\' indicate data collected for the most recent 15 years \(2007-2021\). Not all locations have recent data.')




with tab3:
    st.markdown('#### Il futuro: proiezioni climatiche e *morphing*')
    st.markdown('#### Il *morphing* dei dati climatici')
    with st.expander('*Dettagli sul morphing di dati climatici per ottenere l\'anno climatico tipo per climi futuri*'):
        st.markdown('\n'.join(weather_morphing_descr01), unsafe_allow_html=True)

    st.markdown('#### Lo strumento *Future Weather Generator*')
# st.dataframe( df_COB_DBT.reindex(sorted(df_COB_DBT.columns), axis=1) )