% Run this after example.m in order to write the detected event times to disk

ts_data = [];

num_subj = numel(timeseries);
num_trials = 200;

event_times = cell(num_subj * num_trials, 1);
event_onsets = cell(num_subj * num_trials, 1);
event_offsets = cell(num_subj * num_trials, 1);
event_maxfreqs = cell(num_subj * num_trials, 1);
event_lowfreqs = cell(num_subj * num_trials, 1);
event_highfreqs = cell(num_subj * num_trials, 1);
event_powers = cell(num_subj * num_trials, 1);

for subj_idx = 1:num_subj
    ts_data = [ts_data, timeseries{subj_idx}];
    trial_idxs = specEvents(subj_idx).Events.Events.trialind + ((subj_idx - 1) * num_trials);
    %trial_idxs = specEvents(subj_idx).Events.Events.trialind;



    for trial_idx=1:length(trial_idxs)
        event_time = specEvents(subj_idx).Events.Events.maximatiming(trial_idx);
        event_times{trial_idxs(trial_idx)} = [event_times{trial_idxs(trial_idx)}, event_time];
        event_onset = specEvents(subj_idx).Events.Events.onsettiming(trial_idx);
        event_onsets{trial_idxs(trial_idx)} = [event_onsets{trial_idxs(trial_idx)}, event_onset];
        event_offset = specEvents(subj_idx).Events.Events.offsettiming(trial_idx);
        event_offsets{trial_idxs(trial_idx)} = [event_offsets{trial_idxs(trial_idx)}, event_offset];
        event_maxfreq = specEvents(subj_idx).Events.Events.maximafreq(trial_idx);
        event_maxfreqs{trial_idxs(trial_idx)} = [event_maxfreqs{trial_idxs(trial_idx)}, event_maxfreq];
        event_lowfreq = specEvents(subj_idx).Events.Events.lowerboundFspan(trial_idx);
        event_lowfreqs{trial_idxs(trial_idx)} = [event_lowfreqs{trial_idxs(trial_idx)}, event_lowfreq];
        event_highfreq = specEvents(subj_idx).Events.Events.upperboundFspan(trial_idx);
        event_highfreqs{trial_idxs(trial_idx)} = [event_highfreqs{trial_idxs(trial_idx)}, event_highfreq];
        event_power = specEvents(subj_idx).Events.Events.maximapowerFOM(trial_idx);
        event_powers{trial_idxs(trial_idx)} = [event_powers{trial_idxs(trial_idx)}, event_power];
    end
end

save("beta_events_shin_2017.mat", "ts_data", "event_times", "event_onsets", "event_offsets", "event_maxfreqs",...
    "event_lowfreqs", "event_highfreqs", "event_powers", "Fs")
%save("beta_events_shin_2017_method3.mat", "ts_data", "event_times", "event_onsets", "event_offsets", "event_maxfreqs",...
%    "event_lowfreqs", "event_highfreqs", "event_powers", "Fs")