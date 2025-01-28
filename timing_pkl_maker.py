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
import sys

print("Libraries imported!")
if len(sys.argv) != 2:
    print("Usage: python timing_pkl_maker.py <run>")
    sys.exit(1)

run = sys.argv[1]
file_format = "crt_ana_*"
print("Looking at run ", run)

# Use either the persistent or data path. Currently using the persistent path because data is full
# path = "/exp/sbnd/data/users/jbateman/workdir/crt/run/"
path = "/pnfs/sbnd/persistent/users/jbateman/crt/run/"


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
def apply_mask(data, mask):
    return data[mask]

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
    recodata = ttree['crtana/tree'].arrays(features, library='ak')
    # Merge all the files into one dataframe
    for file in subset_files[1:]:
        print("Loading ", file, "...")
        ttree = uproot.open(file)
        temp_recodata = ttree['crtana/tree'].arrays(features, library='ak')
        recodata = ak.concatenate([recodata, temp_recodata])
        ttree.close()
    print("Data loaded!")

    ts0_arr = recodata['feb_ts0']
    ts1_arr = recodata['feb_ts1']

    flags = recodata.feb_flags
    tdc_time = recodata.tdc_timestamp
    tdc_names = recodata.tdc_name

    # Find the indices of 'etrig' in tdc_names
    etrig_indices = ak.argmax(tdc_names == b'etrig', axis=1)

    # Initialize an empty list to store the TDC etrig values
    tdc_etrig = []

    # Loop through each subarray in tdc_time and etrig_indices
    for tdc_subarray, etrig_index in zip(tdc_time, etrig_indices):
        if etrig_index is not None:
            tdc_etrig.append(tdc_subarray[etrig_index])
        else:
            tdc_etrig.append(np.nan)  # Handle cases where etrig_index is None

    # Convert the list to a numpy array
    tdc_etrig = np.array(tdc_etrig)

    # Get the last 9 digits for timing until t0 reset
    tdc_offset = tdc_etrig % 1e9

    # Calculate trig_time
    trig_time = (ts0_arr - tdc_offset[:, None]) / 1e6  # convert from ns to ms

    # Flatten the arrays and filter by flag
    trig_time = ak.flatten(trig_time)
    flag_arr = ak.flatten(flags)

    trig_time = np.array(trig_time)
    flag_arr = np.array(flag_arr)
    flag_11 = flag_map(flag_arr, 11)
    flag_3 = flag_map(flag_arr, 3)
    print("Finished creating flag arrays!")
    # Saving this as a pkl to merge with the other data!
    path = "/exp/sbnd/data/users/jbateman/workdir/crt/run/"+run+"/"
    print("Saving flags to ", path)
    filename = f"flag_t0_etrig_{batch_number}.pkl"
    save_flags_as_pkl(trig_time, flag_11, flag_3, path, filename)

    sp_features = ['cl_has_sp', 'cl_tagger', 'cl_sp_ts0', 'cl_sp_x', 'cl_sp_y', 'cl_sp_z'] # defining a reduced set of features to speed up processing

    # Apply the mask to each row
    print("Filtering dataframe for spacepoints...")
    mask = recodata['cl_has_sp']
    filtered_df = {feature: apply_mask(recodata[feature], mask) for feature in sp_features}

    relative_ts0 = []
    relative_ts1 = []

    filter_spx = []
    filter_spy = []
    filter_spz = []
    filter_wall_tag = []

    tagger_no_sp = filtered_df['cl_tagger']
    sp_x = filtered_df['cl_sp_x']
    sp_y = filtered_df['cl_sp_y']
    sp_z = filtered_df['cl_sp_z']
    sp_ts0 = filtered_df['cl_sp_ts0']
    sp_ts1 = filtered_df['cl_sp_ts1']
    tdc_time = recodata['tdc_timestamp']
    tdc_names = recodata['tdc_name']

    # Find the indices of 'crtt1', 'rwm', and 'etrig' in tdc_names
    crtt1_indices = ak.argmax(tdc_names == b'crtt1', axis=1)
    rwm_indices = ak.argmax(tdc_names == b'rwm', axis=1)
    etrig_indices = ak.argmax(tdc_names == b'etrig', axis=1)

    # # Filter out events with missing TDC data
    valid_events = (crtt1_indices != -1) & (rwm_indices != -1) & (etrig_indices != -1)
    # Apply the mask to filter valid events
    tdc_names = tdc_names[valid_events]
    tdc_time = tdc_time[valid_events]

    # Extract the TDC values
    tdc_crt = tdc_time[tdc_names == b'crtt1']
    tdc_rwm = tdc_time[tdc_names == b'rwm']
    tdc_etrig = tdc_time[tdc_names == b'etrig']

    # Check that none of the entries in each array have length zero
    filter = []
    for crt, rwm, etrig in zip(tdc_crt, tdc_rwm, tdc_etrig):
        try:
            if len(crt) == 0 or len(rwm) == 0 or len(etrig) == 0:
                filter.extend([False])
            else:
                filter.extend([True])
        except:
            filter.extend([False])

    sp_ts0 = sp_ts0[filter]
    sp_ts1 = sp_ts1[filter]
    sp_x = sp_x[filter]
    sp_y = sp_y[filter]
    sp_z = sp_z[filter]
    tagger_no_sp = tagger_no_sp[filter]

    tdc_etrig_flat = ak.flatten(tdc_etrig[filter]) % 1e12
    tdc_rwm_flat = ak.flatten(tdc_rwm[filter]) % 1e12

    # Calculate delta_t
    delta_t = tdc_etrig_flat - tdc_rwm_flat


    # Calculate relative timestamps
    relative_ts0 = sp_ts0 + delta_t
    relative_ts1 = sp_ts1 + delta_t

    # Flatten the arrays
    relative_ts0 = ak.flatten(relative_ts0) / 1e3  # convert from ns to μs
    relative_ts1 = ak.flatten(relative_ts1) / 1e3  # convert from ns to μs
    filter_spx = ak.flatten(sp_x)
    filter_spy = ak.flatten(sp_y)
    filter_spz = ak.flatten(sp_z)
    filter_wall_tag = ak.flatten(tagger_no_sp)

    # Convert to numpy arrays
    relative_ts0 = np.array(relative_ts0)
    relative_ts1 = np.array(relative_ts1)
    filter_spx = np.array(filter_spx)
    filter_spy = np.array(filter_spy)
    filter_spz = np.array(filter_spz)
    wall_tag = np.array(filter_wall_tag)


    print("Number of spacepoints: ", len(relative_ts0))
    print(f"Skipped {len(recodata) - len(delta_t)} events due to missing TDC data")
    
    filter_spx = np.array(filter_spx)
    filter_spy = np.array(filter_spy)
    filter_spz = np.array(filter_spz)

    relative_ts0 = np.array(relative_ts0)/1e3 # convert from ns to μs
    wall_tag = np.array(filter_wall_tag)

    # Saving this to a pkl to combine with other runs
    path = "/exp/sbnd/data/users/jbateman/workdir/crt/run/"+run+"/"
    print("Saving spacepoints to ", path)
    filename = f"sp_timing_{batch_number}.pkl"
    save_sp_as_pkl(relative_ts0, wall_tag, filter_spx, filter_spy, filter_spz, path, filename)