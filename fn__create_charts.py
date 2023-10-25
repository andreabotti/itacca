import colorsys, random
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st



def round_to_decade(custom_series):
    # Extract max and min values from the column
    max_value = custom_series.max()
    min_value = custom_series.min()
    
    # Round values to nearest decade
    rounded_max = math.ceil(max_value/10.0) * 10
    rounded_min = math.ceil(min_value/10.0) * 10

    
    print(f"Original Max: {max_value}, Rounded Max: {rounded_max}")
    print(f"Original Min: {min_value}, Rounded Min: {rounded_min}")
    
    return rounded_max






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




def calculate_and_plot_differences(threshold, df_CTI, df_COB, chart_height):
    # Slice both dataframes to their first column
    try:
        df_CTI_sliced = df_CTI.iloc[:, 0]
        df_COB_sliced = df_COB.iloc[:, 0]
    except:
        df_CTI_sliced = df_CTI
        df_COB_sliced = df_COB

    # Apply the lower threshold to the sliced dataframes
    df_CTI_filtered = df_CTI_sliced[df_CTI_sliced >= threshold]
    df_COB_filtered = df_COB_sliced[df_COB_sliced >= threshold]

    # Apply the lower threshold to the sliced dataframes and replace null values with 0
    df_CTI_filtered = df_CTI_sliced.where(df_CTI_filtered >= threshold, 0)
    df_COB_filtered = df_COB_sliced.where(df_COB_sliced >= threshold, 0)


    # Calculate differences
    df_diff = df_COB_filtered - df_CTI_filtered
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
        yaxis=dict(ticksuffix=' C'),
        height=chart_height,
        margin=dict(l=0,r=0,t=20,b=0),
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
        yaxis_range=[-rounded_max,rounded_max],
        yaxis=dict(ticksuffix=' C'),
        height=chart_height,
        margin=dict(l=0,r=0,t=20,b=0),
    )

    # Return the weekly and monthly plots
    return df_CTI_filtered, df_COB_filtered, df_diff, fig_weekly, fig_monthly
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
def generate_line_chart(df_data_A, df_data_B, color_marker_A, color_marker_B, color_pool_A, color_pool_B, region, chart_height):

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
        margin=dict(l=0,r=0,t=70,b=0),
        # 
        template="plotly_white",
        font=dict(family="Swis721 BT", size=14),
        title=dict(
            text='Temperature a Bulbo Secco - Stazioni in {r}'.format(r=region),
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


