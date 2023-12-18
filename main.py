import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import time
import numpy as np
import sounddevice as sd
import threading

from audio import *
from shaders import *
from config import *
from audioprocessor import *

# Initialize Pygame and create a window
pygame.init()
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)

# Load and compile the fragment shader
fragment_shader = load_shader("bars.frag", GL_FRAGMENT_SHADER)

# Create the shader program
shader_program = compileProgram(fragment_shader)

# Locate the uniform variable 'barHeights' in the shader
loc_barHeights = glGetUniformLocation(shader_program, "barHeights")
# Locate the uniform variable 'numBars' in the shader
num_bars_location = glGetUniformLocation(shader_program, "numBars")
# Locate the uniform variable 'iResolution' in the shader
loc_iResolution = glGetUniformLocation(shader_program, "iResolution")
# Locate the uniform variable 'iTime' in the shader
loc_iTime = glGetUniformLocation(shader_program, "iTime")

glUseProgram(shader_program)
glUniform1i(num_bars_location, numBands)
glUniform2f(loc_iResolution, width, height)


# Find index of pulseaudio device
pa_index = find_pulseaudio()
print(pa_index)

# Create an instance of AudioProcessor
audio_processor = AudioProcessor()

# Start an input stream with the audio_callback method of audio_processor as the callback function
stream = sd.InputStream(
    device=pa_index,
    channels=audio_processor.channels,
    callback=audio_processor.audio_callback,
    blocksize=audio_processor.blocksize,
    samplerate=audio_processor.samplerate
)
stream.start()


# Set the number of frequency bands
set_number_of_bands(numBands)

# Main loop
running = True
start_time = time.time()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # imput 'q' to quit using event pygame.QUIT
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        running = False

    # Wait for new audio data to be ready
    audio_processor.new_audio_data.wait()
    band_volumes = audio_processor.get_bar_volumes()

    # Set the uniforms for your existing shader
    glUseProgram(shader_program)
    glUniform1f(glGetUniformLocation(shader_program, "iTime"), time.time() - start_time)
    glUniform2f(glGetUniformLocation(shader_program, "iResolution"), width, height)

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT)

    # Render the quad
    render_quad()
    

    # Set bars to band volumes
    if loc_barHeights != -1:
        glUniform1fv(loc_barHeights, numBands, band_volumes)
    else:
        print("Uniform 'barHeights' not found in the shader program")


    # Swap the buffer
    pygame.display.flip()
    pygame.time.wait(10)

    # Clear the event so the main loop will wait again
    audio_processor.new_audio_data.clear()
    
# Cleanup
stream.stop()
stream.close()
glDeleteProgram(shader_program)
pygame.quit()

print("dbg: end of main.py")
