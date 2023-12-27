import streamlit as st

import pandas as pd, numpy as np, re
import colorsys, random, math
from datetime import datetime
from meteostat import Point, Daily, Hourly

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import altair as alt




def round_to_decade(custom_series):
    # Extract max and min values from the column
    max_value = custom_series.max()
    min_value = custom_series.min()
    
    # Round values to nearest decade
    rounded_max = math.ceil(max_value/10.0) * 10
    rounded_min = math.ceil(min_value/10.0) * 10
    # print(f"Original Max: {max_value}, Rounded Max: {rounded_max}")
    # print(f"Original Min: {min_value}, Rounded Min: {rounded_min}")
    
    return rounded_max
#
#
#
#
#
def generate_bar_bins_chart(bins, df, color_palette, chart_height):

    data = []
    for col in df.columns:
        binned_counts = [0 for _ in range(len(bins)-1)]
        
        for temp in df[col]:
            try:
                temp = float(temp)
            except:
                'do nothing'
            for i in range(len(bins)-1):
                if bins[i] <= temp < bins[i+1]:
                    binned_counts[i] += 1
        
        total_values = len(df[col])
        binned_percentages = [(count / total_values) * 100 for count in binned_counts]
        
        # Create a bar for each bin
        for i, (percentage, count) in enumerate(zip(binned_percentages, binned_counts)):
            bin_label = f"{bins[i]}-{bins[i+1]}"

            data.append(
                go.Bar(
                    name=bin_label, y=[col], x=[percentage], text=[count], 
                    textposition='auto', hoverinfo="name+y+text", orientation='h',
                    marker_color=color_palette[i],
                    showlegend=True,
                    )
                )
    
    # Update layout for stacking
    layout = go.Layout(
        barmode='stack',
        xaxis=dict(range=[0,101],dtick=20, showticklabels=True, ticksuffix='%'),
        yaxis=dict(tickfont=dict(family="Swis721 BT", size=10)),
        height=chart_height,
        #
        # font_family="Swis721 BT", font_size=10,
        font=dict(family="Swis721 BT", size=12),
        #
        margin=dict(l=0,r=0,t=20,b=0),
        showlegend=True,
        legend=dict(
            # orientation = "h", x=0.5, y=-0.5, xanchor='center',
            font=dict(family="Swis721 BT", size=10),
            ),
        title=dict(text='Temperature - intervalli %', font=dict(size=13), x=0.5, y=1, xanchor='center', yanchor='top',),
    )

    fig = go.Figure(data=data, layout=layout)
    
    return fig
#
#
#
#
#
def calculate_and_plot_differences(threshold, df1, df2, color_cooler, color_warmer, chart_height):
    # Slice both dataframes to their first column
    try:
        df1_sliced = df1.iloc[:, 0]
        df2_sliced = df2.iloc[:, 0]
    except:
        df1_sliced = df1
        df2_sliced = df2

    # Apply the lower threshold to the sliced dataframes
    df1_filtered = df1_sliced[df1_sliced >= threshold]
    df2_filtered = df2_sliced[df2_sliced >= threshold]

    # Apply the lower threshold to the sliced dataframes and replace null values with 0
    df1_filtered = df1_sliced.where(df1_filtered >= threshold, 0)
    df2_filtered = df2_sliced.where(df2_sliced >= threshold, 0)


    # Calculate differences
    df_diff = df2_filtered - df1_filtered
    df_diff = df_diff[df_diff >= -10]
    df_diff = df_diff[df_diff <= 10]


    # Group df_diff by week and month, and calculate the sum
    df_diff_weekly = df_diff.resample('W-Mon').sum()
    df_diff_monthly = df_diff.resample('M').sum()

    rounded_max_weekly = round_to_decade(df_diff_weekly)
    rounded_max_monthly = round_to_decade(df_diff_monthly)
    rounded_max = rounded_max_monthly+1


    # Create a function to determine bar color based on positive or negative values
    def get_bar_color(value):
        return 'lightblue' if value < 0 else 'lightcoral'

    # Create a function - similar to that above - that instead applies Color2 (for df2) for positive values and Color1 (for df1) for negative values.
    # This assumes that df2 almost always represents warmer data (COB, MSTAT) than df1 (CTI)
    def get_bar_color(value):
        return color_cooler if value < 0 else color_warmer

    # Create subplots for weekly differences
    fig_weekly = make_subplots(rows=1, cols=1, subplot_titles=["Differenze Settimanali"])

    trace_weekly = go.Bar(
        x=df_diff_weekly.index,
        y=df_diff_weekly,
        marker=dict(color=[get_bar_color(val) for val in df_diff_weekly]),
    )
    fig_weekly.add_trace(trace_weekly)

    # Update subplot layout for weekly differences
    fig_weekly.update_layout(
        showlegend=False,
        # title_text="Weekly Differences",
        xaxis_title="SETTIMANE",
        yaxis_title="Piu fresco | Piu caldo",
        yaxis_range=[-rounded_max,rounded_max],
        yaxis=dict(ticksuffix=' DH'),
        height=chart_height,
        margin=dict(l=0,r=0,t=40,b=0),
    )

    # Create subplots for monthly differences
    fig_monthly = make_subplots(rows=1, cols=1, subplot_titles=["Differenze Mensili"])

    trace_monthly = go.Bar(
        x=df_diff_monthly.index,
        y=df_diff_monthly,
        marker=dict(color=[get_bar_color(val) for val in df_diff_monthly]),
    )
    fig_monthly.add_trace(trace_monthly)

    # Update subplot layout for monthly differences
    fig_monthly.update_layout(
        showlegend=False,
        xaxis_title="MESI",
        yaxis_title="Piu fresco | Piu caldo",
        yaxis_range=[-rounded_max*1.10,rounded_max*1.10],
        yaxis=dict(ticksuffix=' DH'),
        height=chart_height,
        margin=dict(l=0,r=0,t=40,b=0),
    )

    # Return the weekly and monthly plots
    return df1_filtered, df2_filtered, df_diff, fig_weekly, fig_monthly
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
def generate_line_chart(
        df_data_A, df_data_B, color_marker_A, color_marker_B, color_pool_A, color_pool_B,
        chart_height, title_text,
        ):

    fig_line = go.Figure()

    i=0
    for c in df_data_A.columns:
        i=i+1
        line_color = ['rgb'+str(tuple(col)) for col in color_pool_A][i]
        line_color = color_marker_A
        fig_line.add_trace(
            go.Scatter(
                x=df_data_A.index,
                y=df_data_A[c],
                name = c.split("__")[1],
                marker=dict(color=line_color),
                )
            )

    i=0
    for c in df_data_B.columns:
        i=i+1
        line_color = ['rgb'+str(tuple(col)) for col in color_pool_B][i]
        line_color = color_marker_B
        fig_line.add_trace(
            go.Scatter(
                x=df_data_B.index,
                y=df_data_B[c],
                name = c,
                marker=dict(color=line_color),
                )
            )

    fig_line.update_layout(
        xaxis=dict(zeroline=True, showline=True, showticklabels=True),
        yaxis=dict(
            range=[0,40.2],dtick=5,zeroline=True, showline=True, showticklabels=True, ticksuffix=' C'
            ),
        # 
        showlegend=True,
        legend=dict(x=0.79, y=1.16),
        # 
        height=chart_height,
        # width=1500,
        margin=dict(l=0,r=0,t=40,b=0),
        # 
        template="plotly_white",
        font=dict(family="Swis721 BT", size=14),
        title=dict(
            text=title_text,
            font=dict(size=20), x=0.5, y=1, xanchor='center', yanchor='top'),
        )


    fig_line.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=3,label="3d",step="day",stepmode="backward"),
                    dict(count=7,label="7d",step="day",stepmode="backward"),
                    dict(count=14,label="14d",step="day",stepmode="backward"),
                    dict(count=1,label="1m",step="month",stepmode="backward"),
                    dict(count=3,label="3m",step="month",stepmode="backward"),
                    dict(step="all"),
                ])
            ),
        rangeslider=dict(visible=True),
        type="date"
        )
    )

    # Return the plot
    return fig_line
#
#
#
#
#
def generate_scatter_map_small(
        latitude_col, longitude_col, location_col, chart_height, marker_size, marker_color, zoom01, zoom02,mapbox_access_token):
    fig_small_01 = go.Figure()
    fig_small_01.add_traces(
        go.Scattermapbox(
            lat=latitude_col,
            lon=longitude_col,
            text=location_col,
            mode='markers',
            marker=go.scattermapbox.Marker(size=marker_size, color=marker_color),
            )
    )
    fig_small_01.update_layout(
        showlegend=False,
        height=chart_height,
        hovermode='closest',
        mapbox_style="light",
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox=dict(
            accesstoken=mapbox_access_token,
            center=dict(lat=latitude_col[0],lon=longitude_col[0]),
            zoom=zoom01,
        )
    )
    fig_small_02 = go.Figure(fig_small_01)
    fig_small_02.update_layout(
        mapbox=dict(zoom=zoom02)
    )

    return fig_small_01, fig_small_02
#
#
#
#
#

def fetch_daily_data(latitude, longitude, start_date, end_date):
    # Create a Point for the location
    location = Point(latitude, longitude)

    # Fetch daily data
    data = Daily(location, start_date, end_date)
    daily_data = data.fetch()

    return daily_data
#
def fetch_hourly_data(latitude, longitude, start_date, end_date):
    # Create a Point for the location
    location = Point(latitude, longitude)

    # Fetch hourly data
    data = Hourly(location, start_date, end_date)
    hourly_data = data.fetch()

    return hourly_data




# Function to bin temperature data and calculate percentages
def bin_and_calculate_percentages(temperature_data, temperature_col, intervals, period):
    """
    Bin temperature data into specified intervals and calculate the percentages.
    :param temperature_data: DataFrame with 'date' and 'temperature'.
    :param intervals: List of temperature intervals for binning.
    :param period: Period for aggregation ('M' for monthly, 'W' for weekly).
    :return: DataFrame with percentage data.
    """
    # Bin the temperature data
    temperature_data['temp_bin'] = pd.cut(temperature_data[temperature_col], bins=intervals, include_lowest=True, right=True)
    # Group by period and bin, then count occurrences
    binned_data = temperature_data.groupby([pd.Grouper(key='date', freq=period), 'temp_bin']).size().reset_index(name='count')

    # Calculate total counts per period for normalization
    total_counts = binned_data.groupby('date')['count'].transform('sum')

    # Calculate percentage
    binned_data['percentage'] = (binned_data['count'] / total_counts) * 100
    binned_data['temp_bin'] = binned_data['temp_bin'].astype(str)  # Convert bin to string for plotting

    return binned_data







def create_plotly_go_chart(data, bins, colors):

    # Map bins to colors
    color_mapping = {bin_label: color for bin_label, color in zip(bins, colors)}
    data['color'] = data['temp_bin'].map(color_mapping)

    fig = go.Figure(data=[
        go.Bar(
            x=data['date'],
            y=data['percentage'],
            marker=dict(color=data['temp_bin'])  # Customize bar colors
        )
    ])
    
    # Customize the layout
    fig.update_layout(
        title='Temperature Distribution',
        title_font_size=20,
        title_x=0.5,  # Center title
        xaxis_title='Date',
        yaxis_title='% of Time',
        barmode='group',
        font=dict(family="Arial, sans-serif", size=12, color="RebeccaPurple"),
        margin=dict(l=40, r=40, t=40, b=40),  # Margins (left, right, top, bottom)
        plot_bgcolor='ivory',  # Background color for the plot
        paper_bgcolor='mintcream',  # Background color for the paper
    )

    # Customize axes
    fig.update_xaxes(title_font=dict(size=18, family='Courier', color='crimson'),
                     tickfont=dict(size=14, family='Helvetica', color='blue'),
                     tickangle=45)
    fig.update_yaxes(title_font=dict(size=18, family='Courier', color='crimson'),
                     tickfont=dict(size=14, family='Helvetica', color='blue'))

    # Customize legend
    fig.update_layout(legend=dict(
        x=0,
        y=1,
        traceorder="normal",
        font=dict(family="sans-serif", size=12, color="black"),
        bgcolor="LightSteelBlue",
        bordercolor="Black",
        borderwidth=2
    ))

    return fig




# Function to extract, round numbers, and keep original brackets
def format_range(s):
    # Extract brackets and numbers
    brackets = re.findall(r'[()\[\]]', s)
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", s)
    
    # Round the numbers and reassemble the string with original brackets
    rounded_numbers = [round(float(num)) for num in numbers]
    return f"{brackets[0]}{rounded_numbers[0]}, {rounded_numbers[1]}{brackets[1]}" if len(rounded_numbers) == 2 else None




def create_plotly_express_chart(data, bins, colors, bar_gap,chart_height):

    # Get unique bin intervals from the DataFrame
    unique_bins = data['temp_bin'].unique()

    # Map unique bin intervals to colors
    color_mapping = {bin_label: color for bin_label, color in zip(unique_bins, colors)}
    
    # Apply color mapping to the DataFrame
    data['color'] = data['temp_bin'].map(color_mapping)
    color_dict = {color: color for color in colors}

    # Apply the function to create a new column
    data['temp_bin'] = data['temp_bin'].apply(format_range)


    # Create the figure with Plotly Express
    fig = px.bar(
        data,
        x='date',
        y='percentage',
        color='color',
        color_discrete_map=color_dict,
        hover_data={'color': False, 'percentage': ':.1%', 'temp_bin': True},  # Custom hover data
        title=' ',
    )
    # Update hover template to include bin string and formatted percentage
    fig.update_traces(
        hovertemplate="<br>".join([
            "%{x}",
            "%{y:.1f}%",
            "%{customdata[1]}"
        ])
    )

    # Update layout
    fig.update_layout(
        title_font_size=12,
        title_x=0.5,  # Center title
        # xaxis_title='Date',
        # yaxis_title='% of Time',
        # font=dict(family="Roboto, sans-serif", size=11),
        margin=dict(l=20, r=20, t=20, b=0),
        showlegend=False,
    )

    # Update layout to reduce gap between bars
    fig.update_layout(bargap=bar_gap)  # Adjust this value as needed
    
    # Hide the axis titles
    fig.update_xaxes(title='')
    fig.update_yaxes(title='')

    fig.update_layout(
        showlegend=False,
        yaxis=dict(ticksuffix=' %'),
        height=chart_height,
        margin=dict(l=0,r=0,t=10,b=0),
    )

    # Customize legend
    # fig.update_layout(
    #     legend=dict(
    #         x=0,
    #         y=1,
    #         traceorder="normal",
    #         font=dict(family="sans-serif", size=12, color="black"),
    #         bgcolor="LightSteelBlue",
    #         bordercolor="Black",
    #         borderwidth=2,
    #     )
    # )

    return fig












def generate_temperature_bins_chart(bins, df, color_palette, chart_height, freq):
    """
    Generate a bar bins chart for a temperature timeseries, with separate sets of binned data for each period.

    Args:
    bins (list): A list of numeric values defining the edges of bins.
    df (pd.DataFrame): A pandas DataFrame containing the timeseries data.
    color_palette (list): A list of colors for the bars in the chart.
    chart_height (int): The height of the chart.
    freq (str): Frequency for grouping data ('W' for weekly, 'M' for monthly, etc.).
    """

    # Ensure the DataFrame has a datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a datetime index.")

    # Grouping the data by the specified frequency
    grouped_df = df.groupby(pd.Grouper(freq=freq))

    
    data = []
    for name, group in grouped_df:
        if group.empty:  # Skip empty groups
            continue

        for col in group.columns:
            binned_counts = [0 for _ in range(len(bins)-1)]
            
            for temp in group[col]:
                try:
                    temp = float(temp)
                except:
                    continue  # Skip non-numeric values
                for i in range(len(bins)-1):
                    if bins[i] <= temp < bins[i+1]:
                        binned_counts[i] += 1

            total_values = len(group[col])
            if total_values == 0:  # Avoid division by zero
                continue
            binned_percentages = [(count / total_values) * 100 for count in binned_counts]

            for i, (percentage, count) in enumerate(zip(binned_percentages, binned_counts)):
                bin_label = f"{bins[i]}-{bins[i+1]} ({name.strftime('%b %Y')})"
                data.append(
                    go.Bar(
                        name=bin_label, x=[col], y=[percentage], text=[count], 
                        textposition='auto', hoverinfo="name+x+text", orientation='h',
                        marker_color=color_palette[i % len(color_palette)],
                        showlegend=True,
                    )
                )

    layout = go.Layout(
        barmode='stack',
        yaxis=dict(range=[0, 101], dtick=20, showticklabels=True, ticksuffix='%'),
        xaxis=dict(tickfont=dict(family="Swis721 BT", size=10)),
        height=chart_height,
        font=dict(family="Swis721 BT", size=12),
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=True,
        legend=dict(font=dict(family="Swis721 BT", size=10)),
        title=dict(text='Temperature - intervalli %', font=dict(size=13), x=0.5, y=1, xanchor='center', yanchor='top'),
    )

    fig = go.Figure(data=data, layout=layout)
    
    return fig
