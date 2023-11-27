import sounddevice as sd

# Get a list of all audio devices
devices = sd.query_devices()

# Print information about each device
for i, device in enumerate(devices):
    print(f"Device {i}: {device['name']} (Input channels: {device['max_input_channels']}, Output channels: {device['max_output_channels']})")
