from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np

vertex_shader_source = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
out vec3 FragPos;
out vec3 Normal;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
void main()
{
    FragPos = vec3(model * vec4(position, 1.0));
    Normal = mat3(transpose(inverse(model))) * normal;
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
"""

fragment_shader_source = """
#version 330 core
in vec3 FragPos;
in vec3 Normal;
out vec4 FragColor;
uniform vec3 lightPos;
uniform vec3 cameraPos;
uniform vec3 hairColor;
const int NUM_HAIRS = 100;
uniform vec3 hairPositions[NUM_HAIRS];

void main()
{
    vec3 lightDir = normalize(lightPos - FragPos);
    float diffuseStrength = max(dot(Normal, lightDir), 0.0);
    float shadowIntensity = 0.0;

    for (int i = 0; i < NUM_HAIRS; i++)
    {
        vec3 hairToLight = lightPos - hairPositions[i];
        if (dot(hairToLight, hairToLight) < dot(lightDir, lightDir))
        {
            shadowIntensity += 1.0;
        }
    }

    shadowIntensity /= float(NUM_HAIRS);
    float lightIntensity = diffuseStrength * (1.0 - shadowIntensity);
    vec3 finalColor = lightIntensity * hairColor;
    FragColor = vec4(finalColor, 1.0);
}
"""

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glutSwapBuffers()

def main():
    # Инициализация GLUT
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Hair Shadows")

    # Инициализация GLEW
    glewInit()

    # Компиляция и связывание шейдерной программы
    vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
    shader_program = compileProgram(vertex_shader, fragment_shader)

    # Создание вершинного буфера и вершинного массива
    vertices = np.array([
        -0.5, -0.5, 0.0,  0.0, 0.0, 1.0,
         0.5, -0.5, 0.0,  0.0, 0.0, 1.0,
         0.0,  0.5, 0.0,  0.0, 0.0, 1.0
    ], dtype=np.float32)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, None)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glBindVertexArray(0)

    # Определение uniform-переменных
    light_pos_loc = glGetUniformLocation(shader_program, b"lightPos")
    camera_pos_loc = glGetUniformLocation(shader_program, b"cameraPos")
    hair_color_loc = glGetUniformLocation(shader_program, b"hairColor")

    # Установка значений uniform-переменных
    glUniform3f(light_pos_loc, 1.0, 1.0, 1.0)
    glUniform3f(camera_pos_loc, 0.0, 0.0, 0.0)
    glUniform3f(hair_color_loc, 0.8, 0.4, 0.1)

    # Основной цикл отрисовки
    glutDisplayFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()
