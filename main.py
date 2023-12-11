import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import time
import numpy as np
import sounddevice as sd

from audio import *
from shaders import *
from config import *

# Initialize Pygame and create a window
pygame.init()
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)

# Load and compile the fragment shader
fragment_shader = load_shader("shadbar.frag", GL_FRAGMENT_SHADER)

# Create the shader program
shader_program = compileProgram(fragment_shader)

# Locate the uniform variable 'barHeights' in the shader
loc_barHeights = glGetUniformLocation(shader_program, "barHeights")

# Find index of pulseaudio device
pa_index = find_pulseaudio()
print(pa_index)

# Start an input stream with the callback function
stream = sd.InputStream(device=pa_index, channels=1, callback=audio_callback)
stream.start()

# Set the number of frequency bands
set_number_of_bands(5)

# Main loop
running = True
start_time = time.time()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Set the uniforms for your existing shader
    glUseProgram(shader_program)
    glUniform1f(glGetUniformLocation(shader_program, "iTime"), time.time() - start_time)
    glUniform2f(glGetUniformLocation(shader_program, "iResolution"), width, height)

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT)

    # Render the quad
    render_quad()
    
    band_volumes = get_frequency_band_volumes()
    print(band_volumes)

    # Set bars to band volumes
    if loc_barHeights != -1:
        glUniform1fv(loc_barHeights, 5, band_volumes)
    else:
        print("Uniform 'barHeights' not found in the shader program")


    # Swap the buffer
    pygame.display.flip()
    pygame.time.wait(10)

# Cleanup
stream.stop()
stream.close()
glDeleteProgram(shader_program)
pygame.quit()
