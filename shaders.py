from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

def load_shader(shader_file, shader_type):
    with open(shader_file) as f:
        shader_source = f.read()
    return compileShader(shader_source, shader_type)

def compile_program(*shaders):
    return compileProgram(*shaders)


# Function to render a full-screen quad
def render_quad():
    glBegin(GL_QUADS)
    glVertex2f(-1, -1)
    glVertex2f(1, -1)
    glVertex2f(1, 1)
    glVertex2f(-1, 1)
    glEnd()
