# %%
# imports

import os
import re
import numpy as np
import matplotlib.pyplot as plt

# %%
# class to load data and perform analyses 

class SpikeAnalysis:

    def __init__(self):

        self.data = None
        self.events = None
        self.neuron_events = None

    def load_events(self, events_file):

        events = [] 
        neuron_events = []  

        with open(events_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(',')
                if len(parts) != 2:
                    continue
                name, timestamp = parts
                name = name.strip()
                try:
                    timestamp = float(timestamp.strip())
                except ValueError:
                    print(f"Invalid timestamp: {timestamp} in line: {line}")
                    continue
                if name.startswith('_ch'):
                    neuron_events.append((name, timestamp))
                elif not name.startswith('_'):
                    events.append((name, timestamp))

        self.events = events
        self.neuron_events = neuron_events

        # change units from s to ms
        self.events = [(name, timestamp * 1000) for name, timestamp in self.events]
        self.neuron_events = [(name, timestamp * 1000) for name, timestamp in self.neuron_events]


        print(f"Loaded {len(events)} experiment events.")
        print(f"Loaded {len(neuron_events)} neurons events.")
 
    def trialize_data(self, pre_event_duration=-1000, post_event_duration=5000):

        self.pre_event_duration = pre_event_duration
        self.post_event_duration = post_event_duration

        trials = []
        for event, timestamp in self.events:
            trial_start = timestamp + self.pre_event_duration
            trial_end = timestamp + self.post_event_duration
            trial_spikes_aligned = [(t - timestamp) for n, t in self.neuron_events if t >= trial_start and t <= trial_end]
            trials.append((event, trial_spikes_aligned))
        
        self.trials = trials

        MAX_PIXELS = 700
        if int((self.post_event_duration - self.pre_event_duration)) > MAX_PIXELS:
            bin_scale = int(np.ceil((self.post_event_duration - self.pre_event_duration) / MAX_PIXELS))
            print(f"Time window too big to show all single spikes. Grouping spikes into {bin_scale}ms bins for raster plot.")
        else:
            bin_scale = 1

        trials_matrix = np.zeros((len(trials), int((self.post_event_duration - self.pre_event_duration)/bin_scale)))
        for i, (event, trial_spikes_aligned) in enumerate(trials):
            for spike_time in trial_spikes_aligned:
                spike_bin = int((spike_time - self.pre_event_duration)/bin_scale)
                trials_matrix[i, spike_bin] += 1

        self.trials_matrix = trials_matrix

    def get_trial_data(self):

        return self.trials, self.trials_matrix

    def set_bin_size(self, bin_size):

        self.bin_size = bin_size

    def get_psth_data(self):
        
        binned_trials = []
        
        for event, spike_times in self.trials:
            bins = np.arange(self.pre_event_duration, self.post_event_duration+self.bin_size, self.bin_size)
            binned_spikes, _ = np.histogram(spike_times, bins=bins)
            binned_trials.append((event, binned_spikes))

        t_binned = np.arange(self.pre_event_duration, 
                             self.post_event_duration, 
                             self.bin_size) + self.bin_size / 2

        binned_trials_arr = np.stack([binned_spikes for event, binned_spikes in binned_trials])
        psth_data = np.mean(binned_trials_arr, axis=0) / (self.bin_size / 1000)

        self.t_binned = t_binned
        self.psth_data = psth_data

        return t_binned, psth_data

