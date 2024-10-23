#This file has all the functions required to calculate TI. Just save this file and use it as a library. Import any functions from here to get desired result. 
#For example,  if you import TI_muwi into another python file on the same folder and pass the parameters it will calculate TI by MUWI.
#This file is also used in backend to create the app. 

import ipympl
import wellpathpy as wp
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


def find_inflection_new(df):
    threshold=0
    d2_inclination = np.gradient(np.gradient(df['Inclination'], df['TVD']), df['TVD'])
    d2_azimuth = np.gradient(np.gradient(df['Azimuth'], df['TVD']), df['TVD'])

    # Find the indices of local extrema in the second derivative of inclination
    inclination_inflection_indices = argrelextrema(np.abs(d2_inclination), np.greater)[0]
    inclination_inflection_indices = inclination_inflection_indices[np.abs(d2_inclination[inclination_inflection_indices]) >= threshold]

    # Find the indices of local extrema in the second derivative of azimuth
    azimuth_inflection_indices = argrelextrema(np.abs(d2_azimuth), np.greater)[0]
    azimuth_inflection_indices = azimuth_inflection_indices[np.abs(d2_azimuth[azimuth_inflection_indices]) >= threshold]

    return inclination_inflection_indices, azimuth_inflection_indices

def calculate_and_set_tortuosity(st1, st2):
    # Find the indices where the condition is True
    if st2.MD < st1.MD:
        raise ValueError(f"MD of station 2 ({st2.MD}) should be larger than station 1 ({st1.MD}).")

    amplitude = (np.abs((st2.MD - st1.MD) / (np.sqrt((st2.TVD - st1.TVD) ** 2 + (st2.DX - st1.DX) ** 2 + (st2.DY - st1.DY) ** 2)) - 1))
    if amplitude < 0:
        amplitude = 0
    return amplitude

def amplitude(angle_type,df):
    if angle_type=='Inclination':
        Inflection_indices_inc = find_inflection_new(df)[0].tolist()
        df['Amplitude_Inc']=0
        for i in range(1, len(Inflection_indices_inc)): #start from the 2nd inflection point. The first and 2nd point would form a curve. The 2nd and 3rd would another. Similarly the last point and the previous point would form another.
            df['Amplitude_Inc'].iloc[Inflection_indices_inc[i]]=calculate_and_set_tortuosity(df.iloc[Inflection_indices_inc[i-1]], df.iloc[Inflection_indices_inc[i]])
    if angle_type=='Azimuth':
        Inflection_indices_azi = find_inflection_new(df)[1].tolist()
        df['Amplitude_Azi']=0
        for i in range(1, len(Inflection_indices_azi)):
            df['Amplitude_Azi'].iloc[Inflection_indices_azi[i]]=calculate_and_set_tortuosity(df.iloc[Inflection_indices_azi[i-1]], df.iloc[Inflection_indices_azi[i]])

def compute_average_distance(df, min_index: int, max_index: int) -> float:
    mds = []
    for index, row in list(df.iterrows())[min_index+1: max_index + 1]:
        mds.append(row.MD)
    mds = np.array(mds)

    diffs = np.ediff1d(mds)
    # average distance between stations
    distance = np.nanmean(diffs)

    return float(distance)

def compute_scaling_factor(distance: float) -> float:
    if distance < 30:
        return 0.3 / (0.3 + 0.025 * (30 - distance))

    if distance > 30:
        return 0.3 / (0.3 - (0.05 / 30) * (distance - 30))

    return 1

def compute_survey_frequency_scaling_factor(df, min_index: int = 0, max_index: int = None) -> float:
    distance = compute_average_distance(df, min_index, max_index)
    scaling_factor = compute_scaling_factor(distance)
    return scaling_factor

def tortuosity_inc(df):
    amplitude('Inclination',df)
    #run the amplitude function to create columns for amplitude in dataframe
    last_total_ti_inc=0
    df['TI_Inc']=0
    Inflection_indices_inc=find_inflection_new(df)[0].tolist()
    for index, row in df.iterrows():
        if index in Inflection_indices_inc:
            n_inflections_inc=len(Inflection_indices_inc[0:Inflection_indices_inc.index(index)])
            if n_inflections_inc >= 1:
                Lc = df.iloc[index].MD
                sum_tis = sum(df.iloc[0:index + 1]['Amplitude_Inc'])
                if abs(sum_tis) > 0:
                    f_SF = compute_survey_frequency_scaling_factor(df, max_index=index)
                    #last_total_ti_inc =20000* f_SF*(n_inflections_inc) * (1 / Lc) * sum_tis
                    last_total_ti_inc = 1*10**7*((n_inflections_inc - 1) / n_inflections_inc) * (1 / Lc) * sum_tis
                    #last_total_ti_inc = f_SF*Lc**2* ((n_inflections_inc - 1) / n_inflections_inc) * (1 / Lc) * sum_tis
        df['TI_Inc'].iloc[index]=last_total_ti_inc

def tortuosity_azi(df):
    amplitude('Azimuth',df)
    #run the amplitude function to create columns for amplitude in dataframe
    last_total_ti_azi=0
    df['TI_Azi']=0
    Inflection_indices_azi=find_inflection_new(df)[1].tolist()
    for index, row in df.iterrows():
        if index in Inflection_indices_azi:
            n_inflections_azi=len(Inflection_indices_azi[0:Inflection_indices_azi.index(index)])
            if n_inflections_azi >= 1:
                Lc = df.iloc[index].MD
                sum_tis = sum(df.iloc[0:index + 1]['Amplitude_Azi'])
                if abs(sum_tis) > 0:
                    f_SF = compute_survey_frequency_scaling_factor(df, max_index=index)
                    #last_total_ti_azi =20000*f_SF * (n_inflections_azi) * (1 / Lc) * sum_tis
                    last_total_ti_azi = 1*10**7* ((n_inflections_azi - 1) / n_inflections_azi) * (1 / Lc) * sum_tis
                    #last_total_ti_azi = f_SF * Lc ** 2 * ((n_inflections_azi - 1) / n_inflections_azi) * (1 / Lc) * sum_tis
        df['TI_Azi'].iloc[index]=last_total_ti_azi

def tortuosity_3D(df):
    df['TI_3D']=0
    tortuosity_inc(df)
    tortuosity_azi(df)
    df['TI_3D']=np.sqrt(df['TI_Inc']**2+df['TI_Azi']**2)
    df['TI_3D_scaled']=scaler.fit_transform(df['TI_3D'].values.reshape(-1,1))
    df['TI_Local']= abs(df['TI_3D'].diff().fillna(0))
    return df