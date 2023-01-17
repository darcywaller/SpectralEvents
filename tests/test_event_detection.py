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
    margins of deviation for the other parameters are as follows:
    .........
    '''
    
    # Define tolerable deviance for spectral event characteristics
    devMaxTime = 10 # +-10ms
    devMaxFreq = 1 # +-1Hz
    devLowFreq = 1 # +-1Hz
    devHighFreq = 1 # +-1Hz
    devOnset = 10 # +-10ms
    devOffset = 10 # +-10ms
    devFOMPow = 0.5 # +-0.5 FOM
    
    # Load MATLAB data
    data_dir = os.getcwd()
    if method == 1:
        matlabFile = loadmat(op.join(data_dir,'beta_events_shin_2017.mat'))
    elif method == 3:
        matlabFile = loadmat(op.join(data_dir,'beta_events_shin_2017_method3.mat'))
    else:
        raise ValueError('Unsupported method! Please use 1 or 3')
    matAllEvs = matlabFile['event_times'][0:200,0] # evs from 1st subject
    
    # Get python events by running find_events on demo data
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
    
    
    # Trial loop - checking first subject only for now
    
    # Check # evs per trial
    #assert len(trialPyEvs)-len(trialMatEvs) == 0, "Should be same number of events within trials"
    
    # Timing - check max timing
    #assert trialPyEvs[evIndex]-trialMatEvs[evIndex] <= devMaxTime, "Timing of events should be within tolerable limits of deviation"
    
    # Frequency - check max freq
    # check lower freq bound
    # check higher freq bound
    
    # Duration - check onset
    # check offset
    
    # Power - check maximum power, raw + FOM
    