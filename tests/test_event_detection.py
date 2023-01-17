import sys
import os
import os.path as op

import pytest
import numpy as np
from scipy.io import loadmat

sys.path.append('/gpfs/home/ddiesbur/SpectralEvents')
import spectralevents as se


def test_event_comparison(method):
    '''Test whether the output from MATLAB and Python event detection scripts align
    
    Parameters
    ----------
    method : float
        The event detection method (1, 2, or 3) used to detect spectral events.

    Notes
    -----
    Currently only supports testing method 1 and 3, with method 2 to be added
    to the Python event detection functions in the future. Python output is 
    tested against the output of MATLAB scripts from Shin et al., 2017. Detection
    of the same number of beta events within each trial is required, and tolerable
    margins of deviation for the other parameters.
    '''
    
    # Define tolerable deviance for spectral event characteristics
    devMaxTime = 5 # +-5ms
    devMaxFreq = 1 # +-1Hz
    devLowFreq = 1 # +-1Hz
    devHighFreq = 1 # +-1Hz
    devOnset = 10 # +-5ms
    devOffset = 10 # +-5ms
    devFOMPow = 0.5 # +-0.5 FOM
    
    # Load MATLAB data
    data_dir = os.getcwd()
    if method == 1:
        matlabFile = loadmat(op.join(data_dir,'tests','beta_events_shin_2017.mat'))
    elif method == 3:
        matlabFile = loadmat(op.join(data_dir,'tests','beta_events_shin_2017_method3.mat'))
    else:
        raise ValueError('Unsupported method! Please use 1 or 3')
    matAllEvs = matlabFile['event_times'][0:200,0] # evs from 1st subject
    
    # Get python events by running find_events on demo data
    # <----------SIMPLIFY BY GETTING PICKLE FILES FOR THIS INSTEAD----------->
    fname = op.join(data_dir,'data','prestim_humandetection_600hzMEG_subject1.mat')
    raw_data = loadmat(fname)
    data = raw_data['prestim_raw_yes_no']    
    
    # set parameters
    samp_freq = 600
    n_times = 600
    freqs = list(range(1, 60 + 1))   # fequency values (Hz) over which to calculate TFR
    times = np.arange(n_times) / samp_freq  # seconds
    event_band = [15, 29]  # beta band (Hz)
    thresh_FOM = 6.0  # factor-of-the-median threshold
    
    # calculate TFR
    tfrs = se.tfr(data, freqs, samp_freq)
    
    # find events
    pyAllEvs = se.find_events(tfr=tfrs, times=times, freqs=freqs, event_band=event_band, 
                           thresholds=None, threshold_FOM=thresh_FOM, find_method=method)
    
    # put from cell array/dict into sets
    pyEvs = np.array([len(trial) for trial in pyAllEvs])
    matEvs = np.array([trial.shape[1] for trial in matAllEvs])
    
    # Overall check that same # of evs detected
    assert np.array_equal(matEvs,pyEvs), "Should be same number of events across all trials"
    
    # Once assured same num of evs, extract event characteristics into np arrays
    # matlab evs
    matTimes = np.array([])
    matMaxFreq = np.array([])
    matLowFreq = np.array([])
    matHighFreq = np.array([])
    matOnsets = np.array([])
    matOffsets = np.array([])
    matPower = np.array([])
    trialIndex = -1
    for trial in matAllEvs:
        trialIndex += 1
        matTimes = [np.append(matTimes,ev) for ev in trial]
        matMaxFreq = [np.append(matMaxFreq,ev) for ev in matlabFile['event_maxfreqs'][trialIndex]]
        matLowFreq = [np.append(matLowFreq,ev) for ev in matlabFile['event_lowfreqs'][trialIndex]]
        matHighFreq = [np.append(matHighFreq,ev) for ev in matlabFile['event_highfreqs'][trialIndex]]
        matOnsets = [np.append(matOnsets,ev) for ev in matlabFile['event_onsets'][trialIndex]]
        matOffsets = [np.append(matOffsets,ev) for ev in matlabFile['event_offsets'][trialIndex]]
        matPower = [np.append(matPower,ev) for ev in matlabFile['event_powers'][trialIndex]]
        
    # python evs    
    pyTimes = np.array([])
    pyOnsets = np.array([])
    pyOffsets = np.array([])
    pyMaxFreq = np.array([])
    pyLowFreq = np.array([])
    pyHighFreq = np.array([])
    pyPower = np.array([])
    for trial in pyAllEvs:
        if len(trial)>0:
            trialTimes = np.array([])
            trialOnsets = np.array([])
            trialOffsets = np.array([])
            trialMaxFreq = np.array([])
            trialLowFreq = np.array([])
            trialHighFreq = np.array([])
            trialPower = np.array([])
            for ev in trial:
                trialTimes = np.append(trialTimes,ev['Peak Time'])
                trialOnsets = np.append(trialOnsets,ev['Event Onset Time'])
                trialOffsets = np.append(trialOffsets,ev['Event Offset Time'])
                trialMaxFreq = np.append(trialMaxFreq,ev['Peak Frequency'])
                trialLowFreq = np.append(trialLowFreq,ev['Lower Frequency Bound'])
                trialHighFreq = np.append(trialHighFreq,ev['Upper Frequency Bound'])
                trialPower = np.append(trialPower,ev['Normalized Peak Power'])
                sorter = np.argsort(trialTimes)
            pyTimes = np.append(pyTimes,trialTimes[sorter])
            pyOnsets = np.append(pyOnsets,trialOnsets[sorter])
            pyOffsets = np.append(pyOffsets,trialOffsets[sorter])
            pyMaxFreq = np.append(pyMaxFreq,trialMaxFreq[sorter])
            pyLowFreq = np.append(pyLowFreq,trialLowFreq[sorter])
            pyHighFreq = np.append(pyHighFreq,trialHighFreq[sorter])
            pyPower = np.append(pyPower,trialPower[sorter])
    
    # Timing - check max timing
    assert ((matTimes - pyTimes)*1000 <= devMaxTime).all(), "Timing of events should be within tolerable limits of deviation"
    
    # Frequency - check max freq
    assert ((matMaxFreq - pyMaxFreq) <= devMaxFreq).all(), "Peak frequency of events should be within tolerable limits of deviation"
    
    # check lower freq bound
    assert ((matLowFreq - pyLowFreq) <= devLowFreq).all(), "Lower frequency of events should be within tolerable limits of deviation"
    
    # check higher freq bound
    assert ((matHighFreq - pyHighFreq) <= devHighFreq).all(), "Higher frequency of events should be within tolerable limits of deviation"
    
    # Duration - check onset
    assert ((matOnsets - pyOnsets)*1000 <= devOnset).all(), "Onset of events should be within tolerable limits of deviation"
    
    # check offset
    assert ((matOffsets - pyOffsets)*1000 <= devOffset).all(), "Offset of events should be within tolerable limits of deviation"
    
    # Power - check maximum power in FOM
    assert ((matPower - pyPower) <= devFOMPow).all(), "Power of events should be within tolerable limits of deviation"
    