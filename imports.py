# This file - imports.py - allows to modularise the streamlit app code, and import all necessary python libraries at once

# Data handling and general libraries
import pandas as pd, numpy as np
import re,os, sys, time, json, datetime
from datetime import datetime
import requests, urllib.request, json
from meteostat import Stations, Hourly
import geopandas as gpd

# Streamlit
import streamlit as st

# Plotting
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go, plotly.express as px
from plotly.subplots import make_subplots
from streamlit_plotly_events import plotly_events
import altair as alt
import leafmap.foliumap as leafmap
import chart_studio
chart_studio.tools.set_credentials_file(username='a.botti', api_key='aA5cNIJUz4yyMS9TLNhW');


# Custom libraries
from fn__epw_read import create_df_weather, epwab, strip_string_from_index, strip_string_from_columns
from fn__color_pools import create_color_pools
from fn__create_charts import calculate_and_plot_differences
from fn__locations_mapping import *
#