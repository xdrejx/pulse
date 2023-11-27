import pyaudio

pa = pyaudio.PyAudio()

# List all audio devices
for i in range(pa.get_device_count()):
    dev_info = pa.get_device_info_by_index(i)
    print(f"Device {i}: {dev_info['name']} (Input channels: {dev_info['maxInputChannels']})")
    

# Close PyAudio
pa.terminate()
