import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import time

# Initialize Pygame and create a window
pygame.init()
pygame.display.set_mode((800, 600), DOUBLEBUF|OPENGL)

# Function to load and compile a shader
def load_shader(shader_file, shader_type):
    with open(shader_file) as f:
        shader_source = f.read()
    return compileShader(shader_source, shader_type)

# Load and compile the fragment shader
fragment_shader = load_shader("shader.frag", GL_FRAGMENT_SHADER)

# Create the shader program
shader_program = compileProgram(fragment_shader)

# Function to render a full-screen quad
def render_quad():
    glBegin(GL_QUADS)
    glVertex2f(-1, -1)
    glVertex2f( 1, -1)
    glVertex2f( 1,  1)
    glVertex2f(-1,  1)
    glEnd()

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
    glUniform2f(glGetUniformLocation(shader_program, "iResolution"), 800, 600)

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT)

    # Render the quad
    render_quad()

    # Swap the buffer
    pygame.display.flip()
    pygame.time.wait(10)

# Cleanup
glDeleteProgram(shader_program)
pygame.quit()