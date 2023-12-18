import numpy as np #importing Numpy with an alias np
import pyaudio as pa 
import struct 
import matplotlib.pyplot as plt 

CHUNK = 1024 * 1
FORMAT = pa.paInt16
CHANNELS = 1
RATE = 44100 # in Hz

p = pa.PyAudio()

stream = p.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)



fig, ax = plt.subplots(1)
# Create the frequency axis for the FFT plot
x_fft = np.linspace(0, RATE, CHUNK)
# Plot the initial FFT data (which is random here) in blue ('b')
line_fft, = ax.semilogx(x_fft, np.random.rand(CHUNK), 'b')
# Set the limits for the x and y axes
ax.set_xlim(20, RATE / 2)
ax.set_ylim(0, 1)
# Show the plot
fig.show()

while True:
    # Read data from the stream
    data = stream.read(CHUNK)
    
    # Unpack the audio data
    dataInt = struct.unpack(str(CHUNK) + 'h', data)
    # Update the FFT plot data
    line_fft.set_ydata(np.abs(np.fft.fft(dataInt)) * 2 / (11000 * CHUNK))
    # Redraw the canvas to update the plot
    fig.canvas.draw()
    fig.canvas.flush_events()