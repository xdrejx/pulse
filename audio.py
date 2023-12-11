import numpy as np
import sounddevice as sd
import pyaudio

# Number of frequency bands
num_bands = 5
frequency_bands_volumes = [0] * num_bands

def set_number_of_bands(n):
    global num_bands, frequency_bands_volumes
    num_bands = n
    frequency_bands_volumes = [0] * n
    
def audio_callback(indata, frames, time, status):
    global frequency_bands_volumes

    audio_data = np.frombuffer(indata, dtype=np.float32)

    # Use a larger FFT size for more bins
    fft_size = 16
    fft_result = np.fft.rfft(audio_data, n=fft_size)

    magnitude = np.abs(fft_result)

    # Select the first 5 bins for simplicity (you may need a more sophisticated selection method)
    selected_bins = magnitude[:5]

    # Normalization (optional, based on your visualization requirements)
    normalized_volumes = selected_bins / np.sum(selected_bins)

    frequency_bands_volumes = normalized_volumes


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
