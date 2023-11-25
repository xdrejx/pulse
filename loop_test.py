import sounddevice as sd
import numpy as np

# Callback function to print the volume
def audio_callback(indata, frames, time, status):
    # Compute RMS volume
    volume_rms = np.sqrt(np.mean(indata**2))
    # Convert to dB
    volume_db = 20 * np.log10(volume_rms)
    # Print volume
    print(f"Volume: {volume_db:.2f} dB")

# Open an audio stream using 'pulse' as the input device
stream = sd.InputStream(device=3, channels=1, callback=audio_callback)

# Start the stream and print the volume in a loop
with stream:
    print("Streaming started, press Ctrl+C to stop...")
    try:
        while True:
            sd.sleep(1000)  # Sleep for 1 second
    except KeyboardInterrupt:
        print("Streaming stopped.")
