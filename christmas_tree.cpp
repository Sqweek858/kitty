// ═══════════════════════════════════════════════════════════════════════════════
// 🎄 CYBERPUNK CHRISTMAS TREE - OpenGL Overlay v2
// ═══════════════════════════════════════════════════════════════════════════════
// Compile: g++ -o christmas_tree christmas_tree.cpp -lGL -lGLEW -lglfw -lm
// Run: ./christmas_tree &
// ═══════════════════════════════════════════════════════════════════════════════

#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <csignal>

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

namespace Config {
    constexpr int WIDTH = 200;
    constexpr int HEIGHT = 280;
    constexpr int MARGIN_RIGHT = 50;
    constexpr int MARGIN_BOTTOM = 100;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SHADERS
// ═══════════════════════════════════════════════════════════════════════════════

const char* vertexShaderSource = R"glsl(
#version 330 core
layout (location = 0) in vec2 aPos;
out vec2 fragCoord;

void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
    fragCoord = (aPos + 1.0) * 0.5;
}
)glsl";

const char* fragmentShaderSource = R"glsl(
#version 330 core
out vec4 FragColor;
in vec2 fragCoord;

uniform float uTime;
uniform vec2 uResolution;

float hash(float n) {
    return fract(sin(n) * 43758.5453123);
}

void main() {
    vec2 uv = fragCoord;
    float aspect = uResolution.x / uResolution.y;
    
    // Center coordinates, Y goes up
    vec2 p = uv - vec2(0.5, 0.35);
    p.x *= aspect;
    
    float time = uTime;
    
    // Simple rotation angle for lighting effect (not shape deformation)
    float rotAngle = time * 0.5;
    float rotPhase = sin(rotAngle);  // -1 to 1, for shading
    
    // ═══════════════════════════════════════════════════════════════════════
    // TREE PARAMETERS
    // ═══════════════════════════════════════════════════════════════════════
    float treeHeight = 0.55;
    float treeWidth = 0.28;
    float trunkHeight = 0.08;
    float trunkWidth = 0.045;
    
    vec3 finalColor = vec3(0.0);
    float finalAlpha = 0.0;
    
    // ═══════════════════════════════════════════════════════════════════════
    // TRUNK
    // ═══════════════════════════════════════════════════════════════════════
    float trunkTop = -0.22;
    float trunkBottom = trunkTop - trunkHeight;
    
    if (p.y > trunkBottom && p.y < trunkTop && abs(p.x) < trunkWidth) {
        float trunkShade = 0.7 + 0.3 * rotPhase * (p.x / trunkWidth);
        vec3 trunkColor = vec3(0.4, 0.22, 0.1) * trunkShade;
        finalColor = trunkColor;
        finalAlpha = smoothstep(trunkWidth, trunkWidth - 0.01, abs(p.x));
    }
    
    // ═══════════════════════════════════════════════════════════════════════
    // TREE CONE - 3 layered triangles for that classic tree look
    // ═══════════════════════════════════════════════════════════════════════
    
    // Layer 1 (bottom, widest)
    float layer1Bottom = -0.24;
    float layer1Top = layer1Bottom + 0.28;
    float layer1Width = 0.26;
    
    // Layer 2 (middle)
    float layer2Bottom = layer1Bottom + 0.15;
    float layer2Top = layer2Bottom + 0.26;
    float layer2Width = 0.21;
    
    // Layer 3 (top, narrowest)
    float layer3Bottom = layer2Bottom + 0.14;
    float layer3Top = layer3Bottom + 0.24;
    float layer3Width = 0.16;
    
    // Check each layer
    // Layer 1
    if (p.y > layer1Bottom && p.y < layer1Top) {
        float heightNorm = (p.y - layer1Bottom) / (layer1Top - layer1Bottom);
        float layerWidth = layer1Width * (1.0 - heightNorm);
        if (abs(p.x) < layerWidth) {
            float shade = 0.6 + 0.4 * (0.5 + 0.5 * rotPhase * (p.x / max(layerWidth, 0.01)));
            shade *= (0.85 + 0.15 * heightNorm);
            vec3 treeGreen = mix(vec3(0.0, 0.18, 0.1), vec3(0.0, 0.45, 0.25), shade);
            treeGreen += vec3(0.0, 0.15, 0.08) * (1.0 - abs(p.x) / layerWidth) * 0.5;
            float edgeSoftness = smoothstep(layerWidth, layerWidth - 0.015, abs(p.x));
            finalColor = treeGreen;
            finalAlpha = max(finalAlpha, edgeSoftness);
        }
    }
    
    // Layer 2
    if (p.y > layer2Bottom && p.y < layer2Top) {
        float heightNorm = (p.y - layer2Bottom) / (layer2Top - layer2Bottom);
        float layerWidth = layer2Width * (1.0 - heightNorm);
        if (abs(p.x) < layerWidth) {
            float shade = 0.6 + 0.4 * (0.5 + 0.5 * rotPhase * (p.x / max(layerWidth, 0.01)));
            shade *= (0.85 + 0.15 * heightNorm);
            vec3 treeGreen = mix(vec3(0.0, 0.18, 0.1), vec3(0.0, 0.45, 0.25), shade);
            treeGreen += vec3(0.0, 0.15, 0.08) * (1.0 - abs(p.x) / layerWidth) * 0.5;
            float edgeSoftness = smoothstep(layerWidth, layerWidth - 0.015, abs(p.x));
            finalColor = treeGreen;
            finalAlpha = max(finalAlpha, edgeSoftness);
        }
    }
    
    // Layer 3
    if (p.y > layer3Bottom && p.y < layer3Top) {
        float heightNorm = (p.y - layer3Bottom) / (layer3Top - layer3Bottom);
        float layerWidth = layer3Width * (1.0 - heightNorm);
        if (abs(p.x) < layerWidth) {
            float shade = 0.6 + 0.4 * (0.5 + 0.5 * rotPhase * (p.x / max(layerWidth, 0.01)));
            shade *= (0.85 + 0.15 * heightNorm);
            vec3 treeGreen = mix(vec3(0.0, 0.18, 0.1), vec3(0.0, 0.45, 0.25), shade);
            treeGreen += vec3(0.0, 0.15, 0.08) * (1.0 - abs(p.x) / layerWidth) * 0.5;
            float edgeSoftness = smoothstep(layerWidth, layerWidth - 0.015, abs(p.x));
            finalColor = treeGreen;
            finalAlpha = max(finalAlpha, edgeSoftness);
        }
    }
    
    // ═══════════════════════════════════════════════════════════════════════
    // CHRISTMAS LIGHTS
    // ═══════════════════════════════════════════════════════════════════════
    vec3 lightColors[8];
    lightColors[0] = vec3(1.0, 0.15, 0.5);    // Hot pink
    lightColors[1] = vec3(0.0, 1.0, 1.0);     // Cyan
    lightColors[2] = vec3(1.0, 0.85, 0.0);    // Gold
    lightColors[3] = vec3(0.65, 0.1, 1.0);    // Purple
    lightColors[4] = vec3(0.2, 1.0, 0.45);    // Neon green
    lightColors[5] = vec3(1.0, 0.45, 0.0);    // Orange
    lightColors[6] = vec3(0.2, 0.6, 1.0);     // Electric blue
    lightColors[7] = vec3(1.0, 0.05, 0.65);   // Magenta
    
    // Light positions (hand-placed for nice distribution)
    vec2 lightPositions[12];
    lightPositions[0]  = vec2(-0.12, -0.15);
    lightPositions[1]  = vec2( 0.10, -0.10);
    lightPositions[2]  = vec2(-0.06, -0.02);
    lightPositions[3]  = vec2( 0.14, -0.18);
    lightPositions[4]  = vec2(-0.08,  0.08);
    lightPositions[5]  = vec2( 0.06,  0.02);
    lightPositions[6]  = vec2(-0.03,  0.15);
    lightPositions[7]  = vec2( 0.09,  0.10);
    lightPositions[8]  = vec2(-0.05,  0.22);
    lightPositions[9]  = vec2( 0.04,  0.18);
    lightPositions[10] = vec2(-0.02,  0.28);
    lightPositions[11] = vec2( 0.02,  0.25);
    
    for (int i = 0; i < 12; i++) {
        vec2 lightPos = lightPositions[i];
        
        // Subtle movement with rotation
        lightPos.x += sin(rotAngle + float(i) * 0.5) * 0.015;
        
        float d = length(p - lightPos);
        
        // Blink pattern
        float blinkPhase = float(i) * 0.8 + hash(float(i)) * 6.28;
        float blinkSpeed = 2.0 + hash(float(i) + 5.0) * 2.0;
        float blink = 0.3 + 0.7 * pow(0.5 + 0.5 * sin(time * blinkSpeed + blinkPhase), 2.0);
        
        // Check if light is on "visible" side based on rotation
        float sideVisibility = 0.5 + 0.5 * sign(lightPos.x) * rotPhase;
        blink *= (0.3 + 0.7 * sideVisibility);
        
        // Core and glow
        float lightCore = smoothstep(0.025, 0.005, d) * blink;
        float lightGlow = smoothstep(0.07, 0.01, d) * blink * 0.5;
        
        int colorIdx = i - (i / 8) * 8;
        vec3 thisColor = lightColors[colorIdx];
        
        // Add to final color
        finalColor = mix(finalColor, thisColor, lightCore);
        finalColor += thisColor * lightGlow;
        finalAlpha = max(finalAlpha, lightCore + lightGlow * 0.5);
    }
    
    // ═══════════════════════════════════════════════════════════════════════
    // STAR ON TOP
    // ═══════════════════════════════════════════════════════════════════════
    vec2 starPos = vec2(0.0, 0.38);
    float starDist = length(p - starPos);
    
    // Pulsing
    float starPulse = 0.8 + 0.2 * sin(time * 3.0);
    
    // Star shape (5-pointed via angle)
    float starAngle = atan(p.y - starPos.y, p.x - starPos.x);
    float starShape = 0.025 + 0.015 * pow(abs(sin(starAngle * 2.5 + 0.5)), 2.0);
    starShape *= starPulse;
    
    float star = smoothstep(starShape, starShape * 0.3, starDist);
    
    // Star glow
    float starGlow = smoothstep(0.1, 0.0, starDist) * 0.6 * starPulse;
    
    // Star rays
    float rays = pow(abs(sin(starAngle * 5.0 + time * 1.2)), 4.0);
    float starRays = smoothstep(0.12, 0.02, starDist) * rays * 0.4 * starPulse;
    
    vec3 starGold = vec3(1.0, 0.85, 0.1);
    vec3 starWhite = vec3(1.0, 1.0, 0.95);
    
    // Apply star
    finalColor = mix(finalColor, starGold, starGlow + starRays);
    finalColor = mix(finalColor, mix(starGold, starWhite, 0.7), star);
    finalAlpha = max(finalAlpha, star + starGlow * 0.8 + starRays * 0.5);
    
    // ═══════════════════════════════════════════════════════════════════════
    // EDGE GLOW (neon cyberpunk style)
    // ═══════════════════════════════════════════════════════════════════════
    if (finalAlpha > 0.1 && finalAlpha < 0.95) {
        vec3 edgeGlow = vec3(0.0, 0.9, 0.5) * (1.0 - finalAlpha) * 0.3;
        finalColor += edgeGlow;
    }
    
    // ═══════════════════════════════════════════════════════════════════════
    // OUTPUT
    // ═══════════════════════════════════════════════════════════════════════
    
    // Vignette
    float vignette = 1.0 - smoothstep(0.4, 0.7, length(uv - 0.5));
    finalAlpha *= vignette;
    
    FragColor = vec4(finalColor, finalAlpha);
}
)glsl";

// ═══════════════════════════════════════════════════════════════════════════════
// GLOBALS
// ═══════════════════════════════════════════════════════════════════════════════

GLFWwindow* window = nullptr;
GLuint shaderProgram = 0;
GLuint VAO = 0, VBO = 0;
volatile bool running = true;

// ═══════════════════════════════════════════════════════════════════════════════
// SHADER COMPILATION
// ═══════════════════════════════════════════════════════════════════════════════

GLuint compileShader(GLenum type, const char* source) {
    GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &source, nullptr);
    glCompileShader(shader);
    
    GLint success;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char infoLog[512];
        glGetShaderInfoLog(shader, 512, nullptr, infoLog);
        fprintf(stderr, "Shader compilation error:\n%s\n", infoLog);
        return 0;
    }
    return shader;
}

GLuint createShaderProgram() {
    GLuint vertexShader = compileShader(GL_VERTEX_SHADER, vertexShaderSource);
    GLuint fragmentShader = compileShader(GL_FRAGMENT_SHADER, fragmentShaderSource);
    
    if (!vertexShader || !fragmentShader) return 0;
    
    GLuint program = glCreateProgram();
    glAttachShader(program, vertexShader);
    glAttachShader(program, fragmentShader);
    glLinkProgram(program);
    
    GLint success;
    glGetProgramiv(program, GL_LINK_STATUS, &success);
    if (!success) {
        char infoLog[512];
        glGetProgramInfoLog(program, 512, nullptr, infoLog);
        fprintf(stderr, "Shader linking error:\n%s\n", infoLog);
        return 0;
    }
    
    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);
    
    return program;
}

// ═══════════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════════

void setupQuad() {
    float vertices[] = {
        -1.0f, -1.0f,
         1.0f, -1.0f,
         1.0f,  1.0f,
        -1.0f, -1.0f,
         1.0f,  1.0f,
        -1.0f,  1.0f
    };
    
    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &VBO);
    
    glBindVertexArray(VAO);
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
}

void signalHandler(int sig) {
    running = false;
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════════════════

int main(int argc, char** argv) {
    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);
    
    if (!glfwInit()) {
        fprintf(stderr, "Failed to initialize GLFW\n");
        return 1;
    }
    
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_TRANSPARENT_FRAMEBUFFER, GLFW_TRUE);
    glfwWindowHint(GLFW_DECORATED, GLFW_FALSE);
    glfwWindowHint(GLFW_FLOATING, GLFW_TRUE);
    glfwWindowHint(GLFW_RESIZABLE, GLFW_FALSE);
    glfwWindowHint(GLFW_FOCUSED, GLFW_FALSE);
    glfwWindowHint(GLFW_FOCUS_ON_SHOW, GLFW_FALSE);
    glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE);
    
    GLFWmonitor* monitor = glfwGetPrimaryMonitor();
    const GLFWvidmode* mode = glfwGetVideoMode(monitor);
    
    int posX = mode->width - Config::WIDTH - Config::MARGIN_RIGHT;
    int posY = mode->height - Config::HEIGHT - Config::MARGIN_BOTTOM;
    
    window = glfwCreateWindow(Config::WIDTH, Config::HEIGHT, "Christmas Tree", nullptr, nullptr);
    if (!window) {
        fprintf(stderr, "Failed to create window\n");
        glfwTerminate();
        return 1;
    }
    
    glfwSetWindowPos(window, posX, posY);
    glfwShowWindow(window);
    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);
    
    glewExperimental = GL_TRUE;
    if (glewInit() != GLEW_OK) {
        fprintf(stderr, "Failed to initialize GLEW\n");
        glfwTerminate();
        return 1;
    }
    
    shaderProgram = createShaderProgram();
    if (!shaderProgram) {
        glfwTerminate();
        return 1;
    }
    
    setupQuad();
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    
    GLint uTimeLoc = glGetUniformLocation(shaderProgram, "uTime");
    GLint uResolutionLoc = glGetUniformLocation(shaderProgram, "uResolution");
    
    printf("\033[38;5;46m🎄 Cyberpunk Christmas Tree Running!\033[0m\n");
    printf("   Position: %d, %d\n", posX, posY);
    printf("   Size: %d x %d\n", Config::WIDTH, Config::HEIGHT);
    printf("   Press Ctrl+C to stop\n\n");
    
    while (running && !glfwWindowShouldClose(window)) {
        glClearColor(0.0f, 0.0f, 0.0f, 0.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        
        glUseProgram(shaderProgram);
        glUniform1f(uTimeLoc, (float)glfwGetTime());
        glUniform2f(uResolutionLoc, (float)Config::WIDTH, (float)Config::HEIGHT);
        
        glBindVertexArray(VAO);
        glDrawArrays(GL_TRIANGLES, 0, 6);
        
        glfwSwapBuffers(window);
        glfwPollEvents();
    }
    
    glDeleteVertexArrays(1, &VAO);
    glDeleteBuffers(1, &VBO);
    glDeleteProgram(shaderProgram);
    glfwDestroyWindow(window);
    glfwTerminate();
    
    printf("\n\033[38;5;196m🎄 Christmas Tree stopped. Crăciun Fericit!\033[0m\n");
    return 0;
}
