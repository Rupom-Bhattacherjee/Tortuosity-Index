import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

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