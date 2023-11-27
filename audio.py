import numpy as np
import sounddevice as sd
import pyaudio

# Number of frequency bands
num_bands = 10
frequency_bands_volumes = [0] * num_bands
# For peak detection and smoothing
peak_values = np.zeros(num_bands)
decay_rate = 0.05  # How quickly peaks fall
smoothing_factor = 0.5  # Smoothing applied to the volume changes
noise_floor = 1e-10  # Threshold for noise gate

def set_number_of_bands(n):
    global num_bands, frequency_bands_volumes, peak_values
    num_bands = n
    frequency_bands_volumes = [0] * n
    peak_values = np.zeros(n)

def audio_callback(indata, frames, time, status):
    global frequency_bands_volumes, peak_values
    # Apply a window to the signal
    window = np.hanning(len(indata[:, 0]))
    windowed_data = indata[:, 0] * window

    # Perform FFT and get power spectrum
    fft_result = np.fft.rfft(windowed_data)
    power_spectrum = np.abs(fft_result)**2

    # Determine frequency band ranges (logarithmic scale)
    freq_bins = np.fft.rfftfreq(len(windowed_data), 1/44100)  # Replace with actual sample rate
    min_freq = min(freq_bins) if min(freq_bins) > 0 else 1
    max_freq = max(freq_bins)
    # Logarithmic division of frequencies
    log_freqs = np.logspace(np.log10(min_freq), np.log10(max_freq), num=num_bands+1)

    # Compute the power in each frequency band
    for i in range(num_bands):
        band_mask = (freq_bins >= log_freqs[i]) & (freq_bins < log_freqs[i+1])
        band_power = np.sum(power_spectrum[band_mask])
        # Apply dynamic range compression
        band_power = np.log1p(band_power)
        # Smooth the transition of the band power
        band_power = (smoothing_factor * band_power + 
                      (1 - smoothing_factor) * frequency_bands_volumes[i])
        # Update peak value if current band power is higher
        if band_power > peak_values[i]:
            peak_values[i] = band_power
        # Otherwise, let the peak value decay over time
        peak_values[i] -= decay_rate * peak_values[i]
        # Noise gate to filter out very low amplitudes
        if peak_values[i] < noise_floor:
            peak_values[i] = 0

    # Normalize band volumes to a 0-1 range based on peak values
    # Avoid division by zero by adding noise_floor to the denominator
    frequency_bands_volumes = [volume / (max(peak_values) + noise_floor) for volume in peak_values]

def get_frequency_band_volumes():
    # Return the normalized volumes
    return frequency_bands_volumes

# function that lists all sound devices and finds the index of pulseaudio
def find_pulseaudio():

    pa = pyaudio.PyAudio()

    # List all audio devices
    for i in range(pa.get_device_count()):
        dev_info = pa.get_device_info_by_index(i)
        if dev_info['name'] == "pulse":
            return dev_info['index']

    # Close PyAudio
    pa.terminate()

    return -1
