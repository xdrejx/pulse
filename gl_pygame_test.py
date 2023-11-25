import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import time
import sys
import numpy as np
import sounddevice as sd

# Global variable to hold the volume level
current_volume = 0

# Resolution of the screen
width = 800
height = 600

def audio_callback(indata, frames, time, status):
    global current_volume
    # Compute RMS volume
    volume_rms = np.linalg.norm(indata)
    current_volume = volume_rms

# Initialize Pygame and create a window
pygame.init()
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)

# Function to load and compile a shader
def load_shader(shader_file, shader_type):
    with open(shader_file) as f:
        shader_source = f.read()
    return compileShader(shader_source, shader_type)

# Load and compile the fragment shader
fragment_shader = load_shader("shader.frag", GL_FRAGMENT_SHADER)

# Create the shader program
shader_program = compileProgram(fragment_shader)

# Locate the uniform variable 'uIntensity' in the shader
uIntensity_location = glGetUniformLocation(shader_program, 'uIntensity')

# Function to render a full-screen quad
def render_quad():
    glBegin(GL_QUADS)
    glVertex2f(-1, -1)
    glVertex2f(1, -1)
    glVertex2f(1, 1)
    glVertex2f(-1, 1)
    glEnd()

# Start an input stream with the callback function
stream = sd.InputStream(device=3, channels=1, callback=audio_callback)
stream.start()

# Main loop
running = True
start_time = time.time()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Set the uniforms
    glUseProgram(shader_program)
    glUniform1f(glGetUniformLocation(shader_program, "iTime"), time.time() - start_time)
    glUniform2f(glGetUniformLocation(shader_program, "iResolution"), width, height)

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT)

    # Render the quad
    render_quad()
    
    # Set the intensity of the shader
    # current_volume is updated by the audio_callback function
    glUniform1f(uIntensity_location, current_volume)

    # Swap the buffer
    pygame.display.flip()
    pygame.time.wait(10)

# Cleanup
stream.stop()
stream.close()
glDeleteProgram(shader_program)
pygame.quit()
