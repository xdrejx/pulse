import numpy as np
import sounddevice as sd
import pyaudio

# Number of frequency bands
num_bands = 10
frequency_bands_volumes = [0] * num_bands

def set_number_of_bands(n):
    global num_bands, frequency_bands_volumes
    num_bands = n
    frequency_bands_volumes = [0] * n
    
def calculate_frequency_bands(fft_data, num_bands):
    frequency_bands = np.zeros(num_bands)
    total_length = len(fft_data)
    log_max = np.log2(total_length)

    for band in range(num_bands):
        # Calculate the start and end indices for each band
        start = int(2 ** (log_max * band / num_bands)) if band > 0 else 0
        end = int(2 ** (log_max * (band + 1) / num_bands))
        end = min(end, total_length-1)  # Ensure end index doesn't exceed total length
        
        # print(start, end, fft_data[start], fft_data[end])

        # Sum the FFT data within this band
        frequency_bands[band] = np.sum(fft_data[start:end])

    return frequency_bands
    
def audio_callback(indata, frames, time, status):
    global frequency_bands_volumes

    audio_data = np.frombuffer(indata, dtype=np.float32)

    # Apply a window function to the audio data to reduce spectral leakage
    window = np.hanning(len(audio_data))
    windowed_data = audio_data * window
    
    # Calculate the FFT of the audio data
    fft_data = np.fft.fft(windowed_data)
    
    # calculate amplitudes by squaring the absolute and imaginary components
    for i in range(len(fft_data)):
        fft_data[i] = np.sqrt(fft_data[i].real**2 + fft_data[i].imag**2).astype(np.float32)
    
    frequency_bands = calculate_frequency_bands(fft_data, num_bands)
            
    
    #normalize the frequency bands
    max_volume = np.max(frequency_bands)
    if max_volume > 0:
        #as float
        frequency_bands_volumes = frequency_bands / max_volume
        
            
        
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
