#This file has the functions to get the directional drilling survey data by different means (e.g., by wellID, wellname, pad name, etc.)
#The GUI tool calls these functions backend to get the data, calculate TI, and make plots.
#Some functions are deliberately kept filtered to prevent unwanted access to company database.

import ipympl
import wellpathpy as wp
import pyodbc
import openpyxl
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import sklearn
from scipy.signal import argrelextrema
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))
from mpl_toolkits.mplot3d import Axes3D
import mplcursors
import matplotlib.ticker as ticker
#import matplotlib.cm as cm
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
matplotlib.use('TkAgg')
pd.set_option('mode.chained_assignment', None)
from tortuosity_functions import tortuosity_3D, plot_ti_wellname, plot_ti_pad,TI_wellname_line_plot

def custom_formatter(x, pos):
        return str(x)[-7:]

def get_data_by_muwi(muwi):
    #muwi is the unique wellID for us.
    # Establish a connection to the database using SQLAlchemy
    connection_string = "<Enter your connection string>"
    engine = create_engine(connection_string)

    # Define the SQL query with the muwi_number as a parameter
    sql_query = f"""
    /****** Script for SelectTopNRows command from SSMS  ******/
    SELECT [BU],[Field],[Route],[Pad],[WellName],[MUWI],[PointID],[OffsetX],[OffsetY],[DX],[DY],[MD],[TVD],[Inclination],[Azimuth]
  FROM <Your specific database table>
  WHERE MUWI = '{muwi}'
    """

    # Execute the query and load the result into a pandas DataFrame
    df = pd.read_sql_query(sql_query, engine)

    # Return the resulting DataFrame
    return df.sort_values('PointID').reset_index(drop=True)


def TI_muwi(muwi, section, angle):
    """
    This is a function that calculates TI based on muwi number of a specific well.

    Parameters:
    - muwi: pass the muwi number here as a string.
    - angle: pass the angle here as numeric where you think the lateral section starts from or vertical section finishes at.
    -section: lateral or vertical as string

    Returns:
    - Dataframe with TI values calculated.
    """
    group=get_data_by_muwi(muwi)
    if section=='lateral':
        index=group[group['Inclination']>=angle].index[0]
        group=group.loc[index:].reset_index(drop=True)
        return(tortuosity_3D(group))
    if section=='vertical':
        index=group[group['Inclination']<=angle].index[-1]
        group=group.loc[:index].reset_index(drop=True)
        return(tortuosity_3D(group))
    
def TI_muwi_table(muwi, section, angle):
    """
    This is a function that calculates TI based on muwi number of a specific well.

    Parameters:
    - muwi: pass the muwi number here as a string.
    - angle: pass the angle here as numeric where you think the lateral section starts from or vertical section finishes at.
    -section: lateral or vertical as string

    Returns:
    - Dataframe with TI values calculated.
    """
    group=get_data_by_muwi(muwi)
    if section=='lateral':
        index=group[group['Inclination']>=angle].index[0]
        group=group.loc[index:].reset_index(drop=True)
        result=tortuosity_3D(group)
        print (result)
    if section=='vertical':
        index=group[group['Inclination']<=angle].index[-1]
        group=group.loc[:index].reset_index(drop=True)
        result=tortuosity_3D(group)
        print(result)

def TI_muwi_line_plot(muwi,section,angle):
    plt.figure(figsize=(10, 6))
    group=get_data_by_muwi(muwi)
    if section=='lateral':
        index=group[group['Inclination']>=angle].index[0]
        group=group.loc[index:].reset_index(drop=True)
        result=tortuosity_3D(group)
    if section=='vertical':
        index=group[group['Inclination']<=angle].index[-1]
        group=group.loc[:index].reset_index(drop=True)
        result=tortuosity_3D(group)
    plt.plot(result['MD'], result['TI_3D'], label='3D Tortuosity', color='red')
    plt.plot(result['MD'], result['TI_Inc'], label='Inclination Tortuosity', color='blue')
    plt.plot(result['MD'], result['TI_Azi'], label='3D Tortuosity', color='green')
    plt.xlabel('Measured Depth (MD)')
    plt.ylabel('TI Values')
    plt.title(f'Tortuosity along {section} section')
    plt.legend()
    plt.show()
    
def TI_muwi_depth(muwi,section,MD):
    """
    This is a function that calculates TI based on muwi number of a specific well.

    Parameters:
    - muwi: pass the muwi number here as a string.
    - angle: pass the angle here as numeric where you think the lateral section starts from or vertical section finishes at.
    -section: lateral or vertical as string

    Returns:
    - Dataframe with TI values calculated.
    """
    group=get_data_by_muwi(muwi)
    if section=='lateral':
        index=group[group['MD']>=MD].index[0]
        group=group.loc[index:].reset_index(drop=True)
        return(tortuosity_3D(group))
    if section=='vertical':
        index=group[group['MD']<=MD].index[-1]
        group=group.loc[:index].reset_index(drop=True)
        return(tortuosity_3D(group))

#plotting any metrics 
def plot_ti_muwi(Metric,muwi,section,angle):
    """
    This is a function that performs plotting TI with well trajectory

    Parameters:
    - parameter1: Metric is the first parameter and represents type of TI. The value could be either 'Inc', 'Azi', '3D', '3D_scaled'.
    - muwi: This is the muwi of the well
    - section: vertical or lateral
    - angle: pass the angle here where you think the lateral section starts from.

    Returns:
    - The result is the plot.
    """
    import matplotlib.colors as colors
    df=TI_muwi(muwi,section,angle).sort_values(by=['PointID']) #df with TI calculated

    x = df['OffsetX']
    y = df['OffsetY']
    z = df['TVD']
    import matplotlib.colors as mcolors
    point_ids = df['PointID']
    mds=df['MD']
    tortuosity=df[f'TI_{Metric}']

    fig = plt.figure(figsize=(15, 12))
    ax = fig.add_subplot(1,1,1, projection='3d',)

    # Plotting the scatter points with color based on tortuosity
    cmap = matplotlib.colormaps.get_cmap('viridis')
    cmap_reversed = cmap.reversed()

    lower_limit = np.percentile(tortuosity, 5)
    upper_limit = np.percentile(tortuosity, 99.9999)

    sc = ax.scatter(x, y, z, c=tortuosity, cmap=cmap_reversed, vmin=lower_limit, vmax=upper_limit, linewidth=2)

    x_min=min(df['OffsetX'])
    x_max=max(df['OffsetX'])
    y_min=min(df['OffsetY'])
    y_max=max(df['OffsetY'])
    z_min=min(df['TVD']-100)
    z_max=max(df['TVD']+100)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)

    ax.set_xlabel('West (-) / East (+)', labelpad=10)
    ax.set_ylabel('South (-) / North (+)', labelpad=10)
    ax.set_zlabel('TVD', labelpad=10)
    ax.set_title(f' Tortuosity along the {section} section')

    ax.xaxis.label.set_position([0.5, -0.1])
    ax.yaxis.label.set_position([-0.1, 0.5])
    ax.zaxis.label.set_position([0, 0.5])

    #Adjust the spacing between x-axis tick marks
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
    
    #Adjust the spacing between y-axis tick marks
    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
    
    #Adjust the spacing between z-axis tick marks
    ax.zaxis.set_major_locator(ticker.MaxNLocator(nbins=5))

    # Customize the x-axis tick formatter
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1e'))

    
    # Add a colorbar
    cbar = plt.colorbar(sc, orientation='vertical', label='Tortuosity', shrink=0.8)
    cbar.set_label(f'{Metric} Tortuosity')

    # Create the mplcursors cursor
    cursor = mplcursors.cursor(sc, hover=True)

    # Format the tooltip display
    @cursor.connect("add")
    def on_add(sel):
        index = sel.index
        tortuosity_value = tortuosity[index]
        tooltip_text = f'PointID: {point_ids[index]},\n OffsetX: {x[index]:.2f},\n OffsetY: {y[index]:.2f},\n MD: {mds[index]:.2f},\n TVD: {z[index]:.2f},\n{Metric}  Tortuosity: {tortuosity_value:.2f}'
        sel.annotation.set_text(tooltip_text)

    ax.invert_zaxis()
    plt.show()

def get_data_by_wellname(wellname): 
    # Establish a connection to the database using SQLAlchemy
    connection_string = "<Your connection string>"
    engine = create_engine(connection_string)

    # Define the SQL query with the muwi_number as a parameter
    sql_query = f"""
    /****** Script for SelectTopNRows command from SSMS  ******/
    SELECT [BU],[Field],[Route],[Pad],[WellName],[MUWI],[PointID],[OffsetX],[OffsetY],[DX],[DY],[MD],[TVD],[Inclination],[Azimuth]
  FROM <Your table>
  WHERE WellName = '{wellname}'
    """
    # Execute the query and load the result into a pandas DataFrame
    df = pd.read_sql_query(sql_query, engine)

    # Return the resulting DataFrame
    return df.sort_values('PointID').reset_index(drop=True)

def TI_wellname(wellname,section, angle):
    """
    This is a function that calculates TI based on wellname and number.

    Parameters:
    - wellname: pass the name of the well here as a string. Wellname should be in sentence case. For example: 'Briggs 11H'
    - section: vertical or lateral
    - angle: pass the angle here where you think the lateral section starts from.

    Returns:
    - Dataframe with TI values calculated.
    """
    group=get_data_by_wellname(wellname)
    if section=='lateral':
        index=group[group['Inclination']>=angle].index[0]
        group=group.loc[index:].reset_index(drop=True)
        return(tortuosity_3D(group))
    if section=='vertical':
        index=group[group['Inclination']<=angle].index[-1]
        group=group.loc[:index].reset_index(drop=True)
        return(tortuosity_3D(group))
    
def TI_wellname_line_plot(wellname, section,angle):
    plt.figure(figsize=(10, 6))
    group=get_data_by_wellname(wellname)
    if section=='lateral':
        index=group[group['Inclination']>=angle].index[0]
        group=group.loc[index:].reset_index(drop=True)
        result=tortuosity_3D(group)
    if section=='vertical':
        index=group[group['Inclination']<=angle].index[-1]
        group=group.loc[:index].reset_index(drop=True)
        result=tortuosity_3D(group)
        
    plt.plot(result['MD'], result['TI_3D'], label='3D Tortuosity', color='red')
    plt.plot(result['MD'], result['TI_Inc'], label='Inclination Tortuosity', color='blue')
    plt.plot(result['MD'], result['TI_Azi'], label='Azimuth Tortuosity', color='green')
    plt.xlabel('Measured Depth (MD)')
    plt.ylabel('TI Values')
    plt.title(f'Tortuosity Index against MD')
    plt.legend()
    plt.show()

def plot_ti_wellname(Metric, wellname, section, angle):
    """
    This is a function that performs plotting TI from wellname and number with well trajectory

    Parameters:
    - Metric: Metric is the first parameter and represents type of TI. The value could be either 'Inc', 'Azi', '3D_scaled'.
    - wellname: pass the name of the well here as a string. Wellname should be in sentence case. For example: 'Briggs 11H'
    - section: vertical or lateral
    - angle: pass the angle as numeric

    Returns:
    - The result is the plot.
    """
    df = TI_wellname(wellname, section, angle)
    x = df['OffsetX']
    y = df['OffsetY']
    z = df['TVD']
    tortuosity = df[f'TI_{Metric}']
    point_ids = df['PointID']
    mds=df['MD']

    fig = plt.figure(figsize=(15, 12))
    ax = fig.add_subplot(111, projection='3d')

    # Plotting the scatter points with color based on tortuosity
    cmap = matplotlib.colormaps.get_cmap('viridis')
    cmap_reversed = cmap.reversed()

    lower_limit = np.percentile(tortuosity, 5)
    upper_limit = np.percentile(tortuosity, 95)

    sc = ax.scatter(x, y, z, c=tortuosity, cmap=cmap_reversed, vmin=lower_limit, vmax=upper_limit, linewidth=2)

    x_min=min(df['OffsetX'])
    x_max=max(df['OffsetX'])
    y_min=min(df['OffsetY'])
    y_max=max(df['OffsetY'])
    z_min=min(df['TVD']-100)
    z_max=max(df['TVD']+100)


    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max) 

    ax.set_xlabel('Offset West (-) / East (+)', labelpad=10)
    ax.set_ylabel('Offset South (-) / North (+)', labelpad=10)
    ax.set_zlabel('TVD', labelpad=10)
    ax.set_title(f'3D Trajectory of {wellname} with Colorized Points based on {Metric} Tortuosity')

    ax.xaxis.label.set_position([0.5, -0.1])
    ax.yaxis.label.set_position([-0.1, 0.5])
    ax.zaxis.label.set_position([0, 0.5])

    # Add a colorbar
    cbar = plt.colorbar(sc, orientation='vertical', label='Tortuosity', shrink=0.8)
    cbar.set_label(f'{Metric} Tortuosity')

    # Customize the x-axis tick formatter
    #ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1e'))
    #ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1e'))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(custom_formatter))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(custom_formatter))

    # Create the mplcursors cursor
    cursor = mplcursors.cursor(sc, hover=True)
    # Format the tooltip display
    @cursor.connect("add")
    def on_add(sel):
        index = sel.index
        tortuosity_value = tortuosity[index]
        tooltip_text = f'PointID: {point_ids[index]},\n OffsetX: {x[index]:.2f},\n OffsetY: {y[index]:.2f},\n MD: {mds[index]:.2f},\n TVD: {z[index]:.2f},\n{Metric} Tortuosity: {tortuosity_value:.2f}'
        sel.annotation.set_text(tooltip_text)

    ax.invert_zaxis()
    plt.tight_layout()
    plt.show()


def get_data_by_wellpad(wellpad): 
    # Establish a connection to the database using SQLAlchemy
    connection_string = "<your connection string>"
    engine = create_engine(connection_string)

    # Define the SQL query with the muwi_number as a parameter
    sql_query = f"""
    /****** Script for SelectTopNRows command from SSMS  ******/
      SELECT [BU],[Field],[Route],[Pad],[WellName],[MUWI],[PointID],[OffsetX],[OffsetY],[DX],[DY],[MD],[TVD],[Inclination],[Azimuth]
  FROM <your table>
  WHERE Pad = '{wellpad}'
    """

    # Execute the query and load the result into a pandas DataFrame
    df = pd.read_sql_query(sql_query, engine) #we can't sort it by pointID or anything because it contains group from different well. We will sort it later when we group them by well.

    # Return the resulting DataFrame
    return df.reset_index(drop=True)

def TI_wellpad(wellpad,section,angle):
    """
    This is a function that performs TI estimation of the wells across the wellpad.

    Parameters:
    - wellpad: pad name.
    - section: vertical or lateral
    - angle: Inclination angle 

    Returns:
    - The result is the TI values for all the wells of a wellpad.
    """
    df_new=get_data_by_wellpad(wellpad)

    # # Iterate over each DataFrame
    grouped_data = df_new.groupby('WellName')
    result_df = []
    
    for _, group in grouped_data:
        group=group.sort_values(by=['PointID']).reset_index(drop=True)
        if section=='lateral':
            index=group[group['Inclination']>=angle].index[0]
            group=group.loc[index:].reset_index(drop=True)
            result_df.append(tortuosity_3D(group))
        if section=='vertical':
            index=group[group['Inclination']<=angle].index[-1]
            group=group.loc[:index].reset_index(drop=True)
            result_df.append(tortuosity_3D(group))

    combined_df = pd.concat(result_df, ignore_index=True)
    return combined_df

def plot_ti_pad(metric, wellpad, section, angle):
    """
    This is a function that performs plotting TI with well trajectory across the wellpad.

    Parameters:
    - metric: metric represents the type of TI you want to plot. The value could be either 'Inc', 'Azi', '3D_scaled'.
    - wellpad: wellpad name. 
    - section: vertical or lateral
    - angle: angle where the lateral section starts

    Returns:
    - The result is the interactive TI plot with trajectories for all the wells of a wellpad.
    """

    df_new = get_data_by_wellpad(wellpad)
    grouped_data = df_new.groupby('WellName')
    fig = plt.figure(figsize=(15, 12))
    ax = fig.add_subplot(111, projection='3d')
    scatters = []  # Store the scatter plot objects
    tortuosity_values = []  # Store all the tortuosity values
    
    for wellname, group in grouped_data:
        group = group.sort_values(by=['PointID']).reset_index(drop=True)
        if section=='lateral':
            index = group[group['Inclination'] >= angle].index[0]
            group = group.loc[index:].reset_index(drop=True)
            result_df = tortuosity_3D(group)
        if section=='vertical':
            index = group[group['Inclination'] <= angle].index[-1]
            group = group.loc[:index].reset_index(drop=True)
            result_df = tortuosity_3D(group)
        cmap = matplotlib.colormaps.get_cmap('viridis')
        cmap_reversed = cmap.reversed()

        sc = ax.scatter(
            result_df['OffsetX'],
            result_df['OffsetY'],
            result_df['TVD'],
            c=result_df[f'TI_{metric}'],
            cmap=cmap_reversed,
            linewidth=2,
            picker=True,
            label=wellname,  # Set the wellname as the label for each well group
        )
        scatters.append(sc)
        tortuosity_values.extend(result_df[f'TI_{metric}'])

    lower_limit = np.percentile(tortuosity_values, 5)
    upper_limit = np.percentile(tortuosity_values, 99.999)

    sc.set_clim(lower_limit, upper_limit)

    cbar = fig.colorbar(sc, orientation='vertical', label='Tortuosity', shrink=0.8)
    cbar.set_label(f'{metric} Tortuosity')

    x_min=min(result_df['OffsetX'])
    x_max=max(result_df['OffsetX'])
    y_min=min(result_df['OffsetY'])
    y_max=max(result_df['OffsetY'])
    z_min=min(result_df['TVD']-100)
    z_max=max(result_df['TVD']+100)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)  # Set the z-axis limit to include TVD=0

    ax.set_xlabel('Offset West (-) / East (+)', labelpad=10)
    ax.set_ylabel('Offset South (-) / North (+)', labelpad=10)
    ax.set_zlabel('TVD', labelpad=10)
    ax.set_title(f' {section} section of Wells from pad {wellpad} with {metric} Tortuosity Index')

    ax.xaxis.label.set_position([0.5, -0.1])
    ax.yaxis.label.set_position([-0.1, 0.5])
    ax.zaxis.label.set_position([0, 0.5])

    # Customize the x-axis tick formatter
    #ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1e'))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(custom_formatter))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(custom_formatter))
    
    # Add cursor to show well name and tooltip information when hovering over a plot
    cursor = mplcursors.cursor(scatters, hover=True)

    #Format the tooltip display
    @cursor.connect("add")
    def on_add(sel):
        wellname = sel.artist.get_label()
        index = sel.index
        point_id = result_df['PointID'].iloc[index]
        offset_x = result_df['OffsetX'].iloc[index]
        offset_y = result_df['OffsetY'].iloc[index]
        tvd = result_df['TVD'].iloc[index]
        md= result_df['MD'].iloc[index]
        tortuosity = result_df[f'TI_{metric}'].iloc[index]
        
        tooltip_text = f'Well: {wellname}'
        sel.annotation.set_text(tooltip_text)

    @cursor.connect("remove")
    def on_remove(sel):
        sel.annotation.set_text("") 

    ax.invert_zaxis()
    plt.show()
