import json
import nptdms
import numpy as np
import pandas as pd
import os
import glob

def init_pulse_iteration(
        amu:float = 40.0, 
        gain:float = 8.0, 
        injected_time:float = 0.0, 
        probe_time:float = 0.0, 
        rtype:str = 'inert', 
        pulse_width:float = 99.0) -> dict:
    """

    This function initializes a dictionary for storing pulse iteration data for a given species.

    Args:
        amu (float): The Atomic Mass Unit for the species.

        gain (float): The mass spectrometer gain setting.

        injected_time (float): The time in which the species was injected.

        probe_time (float): The time the probe molecule was injected (if any).

        rtype (str): The reaction type. Can be either inert, reactant or product.

        pulse_width (float): The pulse width of injection related to the nmol injected.

    Returns:
        out (dict): A dictionary containing pulse iteration meta information.

    """
    out = dict({
        'amu': amu,
        'gain': gain,
        'injected_time': injected_time,
        'probe_time': probe_time,
        'rtype': rtype,
        'pulse_width': pulse_width
        })
    
    return out

def init_metadata(
        catalyst:str = 'Pt', 
        catalyst_amt_mg:float = 1.0,
        catalyst_percent_wt:float = 1,
        catalyst_zone_length_cm:float = 1,
        creator:str = 'John Gleaves',
        date_created:str = '1997-12-25',
        injection_amt_nmol:float = 1.0,
        ID:str = '0001',
        name:str ='Pt/SiO2 conversion experiment',
        paper_DOI:str = 'none',
        preparation_notes:str = 'Washed, baked, etc',
        pulse_iteration:list = [],
        reactor_length_cm:str = 1.0,
        support:str = 'SiO2',
        temperature:float = 25.0,
        time_delta_s:float = 0.001) -> dict:
    """

    This function initializes a dictionary for storing a collection of TAP pulses.

    Args:
        catalyst (str): The catalyst used.

        catalyst_amt_mg (float): The amount of catalyst in milligram.

        catalyst_percent_wt (float): The percent weight of the catalyst.

        catalyst_zone_length_cm (float): The length of the catalyst zone in centimeters.

        creator (float): The name of the person who performed the experiment.

        date_created (str): The date the experiment was performed, YYYY-MM-DD.

        injection_amt_nmol (float): The total number of gas injected in nanomol.

        ID (str): The UNIQUE identifier that connects the meta data to the pulses.

        name (str): The name of the experiment. Typically the file name.

        paper_DOI (str): The DOI associated with the publication that the data was used in.

        preparation_notes (str): Preparation notes of the catalyst.

        pulse_iteration (list): The list pulse iteration meta information (see init_pulse_iteration).

        reactor_length_cm (str): The length of the reactor in centimeters.

        support (str): The support for the catalyst.

        temperature (float): The temperature of the reactor at pulse collection.

        time_delta_s (float): The time interval in which the data was collected.

    Returns:
        out (dict): A dictionary containing meta information for a collection of TAP pulses. 

    """
    out = dict({
        'catalyst': catalyst,
        'catalyst_amt_mg': catalyst_amt_mg,
        'catalyst_percent_wt': catalyst_percent_wt,
        'catalyst_zone_length_cm': catalyst_zone_length_cm,
        'creator': creator,
        'date_created': date_created,
        'injection_amt_nmol': injection_amt_nmol,
        'ID': ID,
        'name': name,
        'paper_DOI': paper_DOI,
        'preparation_notes': preparation_notes,
        'pulse_iteration': pulse_iteration,
        'reactor_length_cm': reactor_length_cm,
        'support': support,
        'temperature': temperature,
        'time_delta_s': time_delta_s
        })
    
    return out


# pulse_iteration, pulse_index, and time_index start at 0, 
# This is especially important when dealing with time.
# Note that the pulse_index, time_index, and pulse_iteration are all integers.
# This is done for faster data queries and compression.
# If the data is not collected evenly within time, please use the time variable.
# Rounding to 4 significant decimal points, based on:
#   "Accurate Mass Measurement: Terminology and Treatment of Data" by Brenton and Godfrey 

def matrix2table(x:pd.DataFrame, sig_pts:int = 4, pulse_iteration:int = 0, time:np.ndarray = None) -> pd.DataFrame:
    """

    This function converts a data frame of column wise pulses to an optimized tabular form.

    Args:
        x (DataFrame): A data frame where each column is a pulse and each row indicates a time index.

        sig_pts (int): The number of significant digits in measurement accuracy of the mass spectrometer.

        pulse_iteration (int): The order in which the gas species were measured by the mass spectrometer (starting at 0).

        time (array): Optional time vector associating the time index to a specific moment. Use only with non-linear time collection.

    Returns:
        out (DataFrame): A data frame that contains each pulse in an optimized tabular form. Columns include: pulse_iteration, pulse_index, time_index, and flux.

    """
    n = x.shape[0]
    p = x.shape[1]
    pulse_index = np.repeat(np.arange(p), n)

    
    time_index = np.tile(np.arange(n), p)
    if time is not None:
        time_index = np.tile(time, p)

    out = pd.DataFrame({'time_index': time_index, 'pulse_index': pulse_index})
    out['pulse_iteration'] = pulse_iteration
    out['flux'] = x.T.to_numpy().flatten().round(sig_pts)

    # Ordering the columns for compression.
    out = out[['pulse_iteration', 'pulse_index', 'time_index', 'flux']]

    # Ensuring integer columns
    out['pulse_iteration'] = out['pulse_iteration'].astype(int)
    out['pulse_index'] = out['pulse_index'].astype(int)
    if time is None:
        out['time_index'] = out['time_index'].astype(int)

    return out


def save_table(meta_data:dict, tabular_data:pd.DataFrame, save_path:str) -> None:
    """

    This function saves the meta data to a json file while saving the tabular data to a parquet file.

    Args:
        meta_data (dict): A dictionary containing meta information for a collection of TAP pulses (see init_metadata). 

        tabular_data (DataFrame): A data frame that contains each pulse in an optimized tabular form. Columns include: pulse_iteration, pulse_index, time_index, and flux (see matrix2table).

        save_path (str): The directory location to save the data.

    Returns:
        out (None): None.

    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    if not os.path.exists(save_path + '/metadata/'):
        os.makedirs(save_path + '/metadata/')

    if not os.path.exists(save_path + '/timeseries/'):
        os.makedirs(save_path + '/timeseries/')

    tmp_path = save_path + '/metadata/' + meta_data['ID'] + '.json'
    with open(tmp_path, 'w') as f:
        json.dump(meta_data, f)

    dat_tabular = pd.concat(tabular_data, ignore_index=True)
    tmp_path = save_path + '/timeseries/' + meta_data['ID'] + '.parquet'
    dat_tabular.to_parquet(tmp_path, index=False)



def csv2table(meta_data:dict, file_path:list, save_path:str) -> None:
    """

    This function saves the meta data to a json file while saving the tabular data to a parquet file.

    Args:
        meta_data (dict): A dictionary containing meta information for a collection of TAP pulses (see init_metadata). 

        file_path (list): A list containing strings of the path to each csv to be included in the tabular data.

        save_path (str): The directory location to save the data.

    Returns:
        out (None): None.

    """
    tabular_data = []
    i = 0
    for single_path in file_path:
        dat = pd.read_csv(single_path)
        tabular_data.append(matrix2table(dat, pulse_iteration=int(i)))
        i += 1

    save_table(meta_data, tabular_data, save_path)


def tdms2table(meta_data:dict, file_path:str, save_path:str) -> None:
    """

    This function saves the meta data to a json file while saving the tabular data to a parquet file.

    Args:
        meta_data (dict): A dictionary containing meta information for a collection of TAP pulses (see init_metadata). 

        file_path (str): A string of the path to the TDMS file to be included in the tabular data.

        save_path (str): The directory location to save the data.

    Returns:
        out (None): None.

    """
    dat = nptdms.TdmsFile(file_path).as_dataframe()
    tmp_keys = dat.keys().to_list()
    key_0 = np.array([i.replace("'", '').split("/")[1] for i in tmp_keys])
    unique_keys = np.unique(key_0)
    unique_keys = unique_keys[unique_keys != 'Secondary Data']
    unique_keys = unique_keys[unique_keys != 'Meta Data']

    pulse_iteration = []
    tabular_data = []
    for single_key in unique_keys:
        key_int = int(single_key) - 1
        sub_df = dat.loc[:, key_0 == single_key]

        # This is the material currently pulled. 
        # May want to inclue temperature per pulse at some point.
        tmp_iter = init_pulse_iteration()
        tmp_iter['amu'] = float(sub_df.iloc[0, 1])
        tmp_iter['gain'] = int(-np.log10(float(sub_df.iloc[1, 1])))
        tmp_iter['injected_time'] = float(sub_df.iloc[4, 1])
        tmp_iter['probe_time'] = float(sub_df.iloc[5, 1])
        tmp_iter['pulse_width'] = float(sub_df.iloc[8, 1])
        pulse_iteration.append(tmp_iter)

        sub_df = sub_df.iloc[1:sub_df.shape[0], 3:sub_df.shape[1]]
        sub_df = sub_df.dropna()
        tabular_data.append(matrix2table(sub_df, pulse_iteration=key_int))
    
    meta_data['pulse_iteration'] = pulse_iteration

    save_table(meta_data, tabular_data, save_path)


def tdms_extract(dir_path, save_path, time_delta = 0.001):
    tdms_files = glob.glob(dir_path + '/**/*.tdms', recursive=True)
    tdms_names = [i.replace('/', '_').replace('.tdms', '').replace(' ', '_') for i in tdms_files]
    meta_data = init_metadata()
    for i, tmp_file in enumerate(tdms_files):
        meta_data['ID'] = '0' * (4 - len(str(i))) + str(i)
        meta_data['name'] = tdms_names[int(i)]
        meta_data['time_delta_s'] = time_delta
        tdms2table(meta_data, tmp_file, save_path)
