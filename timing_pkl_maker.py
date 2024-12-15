print("Importing libraries...")
import uproot
import awkward as ak
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
import pickle as pkl
print("Libraries imported!")
path = "/exp/sbnd/data/users/jbateman/workdir/crt/run/"
run="017985"
file_format = "crt_ana_*"

features = ['run', 'subrun', 'event', 'feb_mac5', 'feb_tagger', 'feb_flags',
       'feb_ts0', 'feb_ts1', 'feb_unixs', 'feb_adc', 'feb_coinc', 'cl_ts0',
       'cl_ts1', 'cl_unixs', 'cl_nhits', 'cl_tagger', 'cl_composition',
       'cl_channel_set', 'cl_adc_set', 'cl_has_sp', 'cl_sp_x', 'cl_sp_ex',
       'cl_sp_y', 'cl_sp_ey', 'cl_sp_z', 'cl_sp_ez', 'cl_sp_pe', 'cl_sp_ts0',
       'cl_sp_ets0', 'cl_sp_ts1', 'cl_sp_ets1', 'cl_sp_complete', 'tr_start_x',
       'tr_start_y', 'tr_start_z', 'tr_end_x', 'tr_end_y', 'tr_end_z',
      'tdc_channel', 'tdc_timestamp', 'tdc_offset',
       'tdc_name']

def list_matching_files(folder_path, pattern):
    search_pattern = os.path.join(folder_path, pattern)
    files = glob.glob(search_pattern)
    return [f for f in files if os.path.isfile(f)]

def flag_map(flag_arr, flag = 11):
    return [1 if x == flag else 0 for x in flag_arr]

def save_flags_as_pkl(trig_time, flag_11, flag_3, path, filename):
    data = {
        't0_etrig': trig_time,
        'flag_11': flag_11,
        'flag_3': flag_3
    }
    with open(os.path.join(path, filename), 'wb') as f:
        pkl.dump(data, f)

# Define a function to apply the boolean mask
def apply_mask(row):
    mask = row['cl_has_sp']
    return row.apply(lambda x: x[mask] if isinstance(x, ak.Array) else x)

def calculate_rel_ts0(ts0, rwm, etrig):
    delta_t = etrig - rwm
    return (ts0 + delta_t)/1e3

def save_sp_as_pkl(relative_ts0, wall_tag, filter_spx, filter_spy, filter_spz, path, filename):
    data = {
        'relative_ts0': relative_ts0,
        'wall_tag': wall_tag,
        'filter_spx': filter_spx,
        'filter_spy': filter_spy,
        'filter_spz': filter_spz
    }
    with open(os.path.join(path, filename), 'wb') as f:
        pkl.dump(data, f)

folder_path = path+run
print("Looking for files in ", folder_path)
matching_files = list_matching_files(folder_path, file_format)
print("Found ", len(matching_files), " files")
# Check how many files there are - memory gets upset if you try load too many
# Splitting the files into batches of 3 for now
batch_size = 5
# Theres probably a better way to loop this, but this is good enough for now!
print("Total batches = ", int(np.ceil(len(matching_files)/batch_size)))


total_batches = int(np.ceil(len(matching_files)/batch_size))

for batch_number in range(total_batches):
    subset_files = matching_files[batch_number*batch_size:(batch_number+1)*batch_size]
    print("Looking at files: ", subset_files)
    print('')
    features = ["feb_ts0", "feb_ts1", "feb_flags", "tdc_timestamp", "tdc_name", "cl_has_sp", "cl_tagger", "cl_sp_ts0", "cl_sp_x","cl_sp_y", "cl_sp_z"]

    # Load the first file to get the columns
    ttree = uproot.open(subset_files[0])
    print("Loading ", subset_files[0], "...")
    recodata = ttree['crtana/tree'].arrays(features, library='pd')
    # Merge all the files into one dataframe
    for file in subset_files[1:]:
        print("Loading ", file, "...")
        ttree = uproot.open(file)
        temp_recodata = ttree['crtana/tree'].arrays(features, library='pd')
        recodata = pd.concat([recodata, temp_recodata])
        ttree.close()

    etrig_index = np.where(recodata['tdc_name'][:1][0] == b'etrig')[0][0]
    rwm_index = np.where(recodata['tdc_name'][:1][0] == b'rwm')[0][0]

    ts0_arr = []
    ts1_arr = []
    flag_arr = []
    tdc_etrig = []
    trig_time = []

    ts0_arr = recodata['feb_ts0']
    ts1 = recodata['feb_ts1']

    flags = recodata['feb_flags'].values
    tdc_time = recodata['tdc_timestamp'].values

    for tdc, flag, ts0 in zip(tdc_time, flags, ts0_arr):
        if len(tdc) > 0:
            
            # tdc_names: ['crtt1' 'bes' 'etrig' 'ftrig' 'rwm']
            tdc_offset = str(tdc[etrig_index]) # Get the TDC etrig
            tdc_offset = np.int64(tdc_offset[-9:]) # Get the last 9 digits for timing until t0 reset
            trig_time.extend(ts0 - tdc_offset)
            flag_arr.extend(flag)

    trig_time = np.array(trig_time)/1e6 # convert from ns to ms

    flag_11 = flag_map(flag_arr, 11)
    flag_3 = flag_map(flag_arr, 3)

    # Saving this as a pkl to merge with the other data!
    path = "/exp/sbnd/data/users/jbateman/workdir/crt/run/"+run+"/"
    filename = f"flag_t0_etrig_{batch_number}.pkl"
    save_flags_as_pkl(trig_time, flag_11, flag_3, path, filename)

    sp_features = ['cl_has_sp', 'cl_tagger', 'cl_sp_ts0', 'cl_sp_x', 'cl_sp_y', 'cl_sp_z'] # defining a reduced set of features to speed up processing

    # Apply the mask to each row
    print("filtering dataframe")
    filtered_df = recodata[sp_features].apply(apply_mask, axis=1)
    print("tagger")

    relative_ts0 = []
    wall_tag = []

    filter_spx = []
    filter_spy = []
    filter_spz = []
    filter_wall_tag = []

    tagger_no_sp = filtered_df['cl_tagger']
    # wall_tag.extend(list(ak.flatten(filtered_df['cl_tagger'])))
    print("sp coords")
    sp_x = filtered_df['cl_sp_x'].values
    sp_y = filtered_df['cl_sp_y'].values
    sp_z = filtered_df['cl_sp_z'].values
    print("tsX")
    sp_ts0 = filtered_df['cl_sp_ts0'].values
    # sp_ts1 = filtered_df['cl_sp_ts1'].values
    print("tdc")
    tdc_time = recodata['tdc_timestamp'].values
    skip_counter = 0
    for tdc, tagger, ts0 , x, y, z in zip(tdc_time, tagger_no_sp, sp_ts0, sp_x, sp_y, sp_z):
        if len(tdc) == 5:
            # ['crtt1' 'bes' 'etrig' 'ftrig' 'rwm']
            tdc_rwm = np.int64(str(tdc[rwm_index])[-12:])       # Get the last 12 digits for timing until RWM, 
            tdc_etrig = np.int64(str(tdc[etrig_index])[-12:])     # otherwise leads to scalar subtract overflow

            delta_t = tdc_etrig - tdc_rwm
            relative_ts0.extend(ts0 + delta_t)
            filter_spx.extend(x)
            filter_spy.extend(y)
            filter_spz.extend(z)
            filter_wall_tag.extend(tagger)
            
            
        else:
            print("skipping event due to missing tdc data")
            skip_counter +=1
    print(f"Skipped {skip_counter} events due to no TDC data")

    filter_spx = np.array(filter_spx)
    filter_spy = np.array(filter_spy)
    filter_spz = np.array(filter_spz)

    relative_ts0 = np.array(relative_ts0)/1e3 # convert from ns to μs
    wall_tag = np.array(filter_wall_tag)

    # Saving this to a pkl to combine with other runs
    path = "/exp/sbnd/data/users/jbateman/workdir/crt/run/"+run+"/"
    filename = f"sp_timing_{batch_number}.pkl"
    save_sp_as_pkl(relative_ts0, wall_tag, filter_spx, filter_spy, filter_spz, path, filename)