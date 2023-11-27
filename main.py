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

# Locate the uniform variable 'uIntensity' in the shader
bar1 = glGetUniformLocation(shader_program, 'bar1')
bar2 = glGetUniformLocation(shader_program, 'bar2')
bar3 = glGetUniformLocation(shader_program, 'bar3')
bar4 = glGetUniformLocation(shader_program, 'bar4')
bar5 = glGetUniformLocation(shader_program, 'bar5')

# Start an input stream with the callback function
stream = sd.InputStream(device=5, channels=1, callback=audio_callback)
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
    
    # set bars to band volumes
    glUniform1f(bar1, band_volumes[0])
    glUniform1f(bar2, band_volumes[1])
    glUniform1f(bar3, band_volumes[2])
    glUniform1f(bar4, band_volumes[3])
    glUniform1f(bar5, band_volumes[4])
    
    print(band_volumes)

    # Re-enable the shader for the rest of the rendering
    glUseProgram(shader_program)

    # Swap the buffer
    pygame.display.flip()
    pygame.time.wait(10)

# Cleanup
stream.stop()
stream.close()
glDeleteProgram(shader_program)
pygame.quit()
