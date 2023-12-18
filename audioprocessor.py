import numpy as np
import threading
import queue
from scipy.fftpack import fft
from scipy.signal import blackman

class AudioProcessor:
    def __init__(self, channels=1, blocksize=512, samplerate=44100):
        
        # Initialize audio stream parameters
        self.channels = channels
        self.blocksize = blocksize
        self.samplerate = samplerate
        
        # Condition for notifying when new audio data is ready
        self.data_condition = threading.Condition()
        # Event for notifying when new bar volumes are ready
        self.new_audio_data = threading.Event()  
        # Lock for accessing bar volumes
        self.bar_volumes_lock = threading.Lock()
        # Lock for configuring audio processing
        self.config_lock = threading.Lock()
        
        # Precalculate for 20 bars
        self.config(20, False, False)
        
        # Thread for running the audio processing
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        # Convert the input data to a NumPy array
        indata = np.frombuffer(indata, dtype=np.float32)

        # Add the audio data
        with self.data_condition:
            self.raw_data = indata
            self.data_condition.notify()
        
    
    def config(self, num_bars, autosens, noise_reduction, low_cutoff=50, high_cutoff=10000):
        with self.config_lock:
            self.barNum = num_bars
            self.autosens = autosens
            self.noise_reduction = noise_reduction
            self.low_cutoff = low_cutoff
            self.high_cutoff = high_cutoff

            self.raw_data = None
            self.bar_volumes = [0] * num_bars  # Initialize bar volumes to 0

            # Add any additional initialization or configuration here

    def run(self):
        while True:
            # Make sure that its not reconfiguring
            with self.config_lock:
                # Wait for new raw audio data
                with self.data_condition:
                    self.data_condition.wait()
                    data = self.raw_data

                # Process the audio data
                self.bar_volumes = self.process_audio_data(data)

                # Signal that new audio data is ready
                self.new_audio_data.set()
            
    def calculate_frequency_bands(self, fft_data, num_bands):
        frequency_bands = np.zeros(num_bands)
        total_length = len(fft_data)
        log_max = np.log2(total_length)

        for band in range(num_bands):
            # Calculate the start and end indices for each band
            start = int(2 ** (log_max * band / num_bands)) if band > 0 else 0
            end = int(2 ** (log_max * (band + 1) / num_bands))
            end = min(end, total_length-1)
            
            # Sum the FFT data within this band
            frequency_bands[band] = np.sum(fft_data[start:end])
            
        return frequency_bands

    def process_audio_data(self, data): 
        # Apply a hanning window to the audio data
        window = np.hanning(len(data))
        windowed_data = data * window
        
        # Calculate the FFT of the audio data
        fft_data = fft(windowed_data)
        
        # Calculate amplitudes by squaring the absolute and imaginary components
        for i in range(len(fft_data)):
            fft_data[i] = np.sqrt(fft_data[i].real**2 + fft_data[i].imag**2).astype(np.float32)
            
        # Calculate the frequency bands
        frequency_bands = self.calculate_frequency_bands(fft_data, self.barNum)
        
        # Normalize the frequency bands
        max_volume = np.max(frequency_bands)
        if max_volume is not None and max_volume > 0:
            frequency_bands = frequency_bands / max_volume

        return frequency_bands
    
    def get_bar_volumes(self):
        # Return reference to bar volumes
        with self.bar_volumes_lock:
            return self.bar_volumes