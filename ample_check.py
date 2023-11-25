import pyaudio

# Initialize PyAudio
pa = pyaudio.PyAudio()

# Device index (replace with the index of your device)
device_index = 3  # Example: 2 for 'HD-Audio Generic: ALC287 Analog'

# Try different common sample rates
sample_rates = [44100, 48000, 32000]

stream = None
for rate in sample_rates:
    try:
        stream = pa.open(format=pyaudio.paInt16,
                         channels=2,
                         rate=rate,
                         input=True,
                         frames_per_buffer=1024,
                         input_device_index=device_index)
        print(f"Opened stream with sample rate: {rate}")
        break
    except OSError as e:
        print(f"Failed to open stream with sample rate {rate}: {e}")

if not stream:
    print("Failed to open stream with any sample rate.")
    pa.terminate()
    exit(1)

# Continue with your code...
