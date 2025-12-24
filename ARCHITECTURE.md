# Cyberpunk Terminal - Architecture Documentation

## 📐 System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Cyberpunk Terminal                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │         Application Layer (Main)                  │    │
│  │  - CyberpunkTerminalApp                           │    │
│  │  - Mode management                                │    │
│  │  - Component orchestration                        │    │
│  └───────────┬───────────────────────────────────────┘    │
│              │                                             │
│  ┌───────────▼───────────────────────────────────────┐    │
│  │         Presentation Layer (UI)                   │    │
│  │  - MenuBar, StatusBar                             │    │
│  │  - BorderedContainer                              │    │
│  │  - AutocompletePanel                              │    │
│  │  - TextInput                                      │    │
│  └───────────┬───────────────────────────────────────┘    │
│              │                                             │
│  ┌───────────▼───────────────────────────────────────┐    │
│  │         Business Logic Layer                      │    │
│  │  - TerminalSession (command execution)            │    │
│  │  - InputContext (input handling)                  │    │
│  │  - OutputBuffer (output management)               │    │
│  │  - EnvironmentManager (env/cwd)                   │    │
│  └───────────┬───────────────────────────────────────┘    │
│              │                                             │
│  ┌───────────▼───────────────────────────────────────┐    │
│  │         Graphics Layer                            │    │
│  │  - GraphicsCompositor                             │    │
│  │  - ParallaxBackground                             │    │
│  │  - ChristmasTree3D                                │    │
│  │  - ParticleSystems                                │    │
│  └───────────┬───────────────────────────────────────┘    │
│              │                                             │
│  ┌───────────▼───────────────────────────────────────┐    │
│  │         Rendering Layer (Core)                    │    │
│  │  - TerminalEngine (main loop)                     │    │
│  │  - ScreenBuffer (double buffering)                │    │
│  │  - ANSI escape sequences                          │    │
│  └───────────┬───────────────────────────────────────┘    │
│              │                                             │
│  ┌───────────▼───────────────────────────────────────┐    │
│  │         System Layer                              │    │
│  │  - Terminal I/O (termios, tty)                    │    │
│  │  - Process management (subprocess)                │    │
│  │  - Signal handling                                │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Module Breakdown

### 1. terminal_core.py - Core Engine

**Purpose**: Foundation of the terminal system, handles low-level terminal operations and main event loop.

**Key Components**:
- `TerminalEngine`: Main event loop, coordinates all systems
- `ScreenBuffer`: Double-buffered rendering with dirty region tracking
- `TerminalState`: Terminal state save/restore
- `InputHandler`: Non-blocking input reading
- `ANSIEscape`: ANSI escape code utilities
- `PerformanceMetrics`: FPS tracking and performance monitoring

**Responsibilities**:
- Terminal initialization and cleanup
- Event loop management (60 FPS)
- Screen buffer management
- Input collection
- Signal handling (SIGTERM, SIGINT, SIGWINCH)
- Performance tracking

**Dependencies**: None (uses only Python stdlib)

### 2. shader_system.py - Graphics Shader Simulation

**Purpose**: Provides GLSL/HLSL-like shader system in pure Python for advanced graphics effects.

**Key Components**:
- `Vec2/Vec3/Vec4`: Vector mathematics
- `Mat4`: 4x4 matrix operations
- `Color`: Color manipulation with HSV/RGB
- `NoiseGenerator`: Procedural noise (Perlin, Worley)
- `LightingModel`: Phong and Blinn-Phong lighting
- `ShaderProgram`: Base class for shader programs
- `ParallaxShader`: Parallax scrolling shader
- `ChristmasTreeShader`: 3D tree rendering shader
- `SnowShader`: Procedural snow shader
- `PostProcessing`: Post-processing effects

**Responsibilities**:
- Vector and matrix mathematics
- Lighting calculations
- Procedural content generation
- Shader program execution
- Post-processing effects

**Dependencies**: `math`, `random`, `numpy` (optional, not used currently)

### 3. ui_components.py - User Interface Components

**Purpose**: Rich UI component library with gradient borders and animations.

**Key Components**:
- `UIComponent`: Base class for all UI elements
- `BorderedContainer`: Container with animated gradient border
- `MenuBar`: Top menu bar with items
- `AutocompletePanel`: Autocomplete suggestions panel
- `StatusBar`: Bottom status bar with segments
- `TextInput`: Single-line text input with cursor
- `GradientGenerator`: Various gradient types

**Responsibilities**:
- UI component rendering
- Border drawing with gradients
- Component layout
- Animation management
- User interaction handling

**Dependencies**: `shader_system` (for Color)

### 4. input_manager.py - Input Management

**Purpose**: Comprehensive input handling system with keybindings, text editing, and history.

**Key Components**:
- `KeyParser`: Parse terminal key sequences
- `KeyBindingManager`: Manage keybindings
- `TextBuffer`: Text editing with undo/redo
- `CommandHistory`: Command history with navigation
- `AutocompleteEngine`: Fuzzy autocomplete
- `InputContext`: High-level input management

**Responsibilities**:
- Key parsing and normalization
- Keybinding dispatch
- Text editing operations
- Command history management
- Autocomplete suggestions

**Dependencies**: None

### 5. terminal_session.py - Terminal Session Management

**Purpose**: Manages terminal session, command execution, and output buffering.

**Key Components**:
- `CommandExecutor`: Execute commands sync/async
- `OutputBuffer`: Store and manage output
- `EnvironmentManager`: Manage env vars and cwd
- `BuiltinCommands`: Built-in command implementations
- `TerminalSession`: Complete session manager

**Responsibilities**:
- Command parsing and execution
- Output capture and storage
- Environment variable management
- Working directory tracking
- Built-in command handling

**Dependencies**: `subprocess`, `threading`, `queue`

### 6. graphics_engine.py - Graphics Rendering

**Purpose**: Advanced graphics rendering with parallax, 3D objects, and particles.

**Key Components**:
- `ParticleSystem`: Generic particle system
- `SnowParticleSystem`: Snow particles with physics
- `SparkleSystem`: Sparkle effects
- `ParallaxBackground`: Multi-layer parallax
- `ChristmasTree3D`: 3D Christmas tree
- `GraphicsCompositor`: Composite all graphics layers

**Responsibilities**:
- Particle simulation
- 3D object rendering
- Parallax effect
- Layer composition
- Animation updates

**Dependencies**: `shader_system`

### 7. cyberpunk_terminal.py - Main Application

**Purpose**: Integrates all components into a complete application.

**Key Components**:
- `CyberpunkTerminalApp`: Main application class

**Responsibilities**:
- Component initialization
- Update loop
- Render loop
- Input routing
- Mode management
- Application lifecycle

**Dependencies**: All other modules

### 8. config.py - Configuration Management

**Purpose**: User configuration and theme management.

**Key Components**:
- `ThemeColors`: Theme color definitions
- `UserConfig`: User configuration
- `ConfigManager`: Load/save configuration

**Dependencies**: None

### 9. utils.py - Utility Functions

**Purpose**: Common utility functions used across the application.

**Key Components**:
- Math utilities (clamp, lerp, smoothstep)
- Color utilities (RGB/HSV conversion)
- String utilities (truncate, pad, wrap)
- Time utilities (format_time)
- Performance utilities (Timer, FPSCounter)

**Dependencies**: None

## 📊 Data Flow

### 1. Input Flow

```
Terminal Input
    ↓
InputHandler (raw key)
    ↓
KeyParser (KeyPress)
    ↓
InputContext (handle)
    ↓
┌─────────────────┴─────────────────┐
│                                   │
KeyBindingManager              TextBuffer
(dispatch action)              (edit text)
    ↓                              ↓
Application Callback          Text Changed
                                  ↓
                          Autocomplete Update
```

### 2. Command Execution Flow

```
Command Submit
    ↓
TerminalSession
    ↓
Command Parse
    ↓
┌──────────┴───────────┐
│                      │
Built-in?          External?
    ↓                  ↓
BuiltinCommands    CommandExecutor
    ↓                  ↓
Execute            subprocess
    ↓                  ↓
    └──────────┬───────┘
               ↓
         OutputBuffer
               ↓
         Display Update
```

### 3. Render Flow

```
Main Loop (60 FPS)
    ↓
Update Phase
    ├─→ Graphics Update (particles, animations)
    ├─→ UI Update (gradients, timers)
    └─→ Session Update (command completion)
    ↓
Render Phase
    ├─→ Clear ScreenBuffer
    ├─→ Layer 0: Parallax Background
    ├─→ Layer 1: 3D Objects (tree)
    ├─→ Layer 2: UI Components (containers)
    ├─→ Layer 3: Particles (snow, sparkles)
    ├─→ Layer 4: Menu Bar
    └─→ Layer 5: Status Bar
    ↓
Buffer Swap
    ↓
Differential Render
    ↓
ANSI Output to Terminal
```

## 🎯 Design Patterns

### 1. Model-View-Controller (MVC)

- **Model**: `TerminalSession`, `OutputBuffer`, `EnvironmentManager`
- **View**: All `ui_components`, `graphics_engine`
- **Controller**: `InputContext`, `KeyBindingManager`, `CyberpunkTerminalApp`

### 2. Observer Pattern

Used for callbacks:
- Command completion callbacks
- Output line callbacks
- Input change callbacks
- Resize callbacks

### 3. Strategy Pattern

Used for:
- Shader programs (different rendering strategies)
- Gradient generators (different gradient algorithms)
- Border styles

### 4. Composite Pattern

Used for:
- UI components hierarchy
- Graphics layer composition

### 5. Command Pattern

Used for:
- Keybindings (action as command)
- Undo/redo system (edit operations)

### 6. State Pattern

Used for:
- Application modes (NORMAL, COMMAND_INPUT, MENU)
- Terminal state management

### 7. Factory Pattern

Used for:
- Particle creation
- UI component creation

## 🔄 Event Loop

```python
while running:
    # 1. Timing
    current_time = time.time()
    delta_time = current_time - last_time
    
    # 2. Input
    while has_input():
        key = read_key()
        handle_input(key)
    
    # 3. Update
    update_graphics(delta_time)
    update_ui(delta_time)
    update_session(delta_time)
    
    # 4. Render
    screen.clear()
    render_all_layers(screen)
    screen.swap_buffers()
    
    # 5. Output
    commands = screen.get_render_commands()
    output_to_terminal(commands)
    
    # 6. Frame timing
    sleep(target_frame_time - elapsed)
```

## 🎨 Rendering Pipeline

### Double Buffering

```
Front Buffer (displayed)    Back Buffer (being drawn)
    │                            │
    │                            │ ← render_all_layers()
    │                            │
    └──────── swap ──────────────┘
    │
    ↓
Differential Render
    │
    ↓
ANSI Commands
    │
    ↓
Terminal Output
```

### Dirty Region Tracking

Only updates changed regions for performance:

```python
for y in range(height):
    for x in range(width):
        if front_buffer[y][x] != back_buffer[y][x]:
            # Generate update command
            commands.append(cursor_to(y, x))
            commands.append(set_color(color))
            commands.append(char)
```

## 🔐 Thread Safety

- **Main Thread**: Event loop, rendering, UI
- **Worker Threads**: Async command execution
- **Thread Communication**: Callbacks, thread-safe queues

## 📈 Performance Optimizations

1. **Double Buffering**: Reduces flicker
2. **Dirty Region Tracking**: Only update changed areas
3. **Differential Rendering**: Minimize ANSI output
4. **Adaptive Quality**: Adjust graphics based on performance
5. **Frame Timing**: Sleep only what's needed
6. **Lazy Evaluation**: Compute only what's visible
7. **Object Pooling**: Reuse particle objects

## 🧪 Testing Strategy

- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **Performance Tests**: Measure FPS and responsiveness
- **Visual Tests**: Manual verification of rendering

## 📝 Code Style

- **PEP 8** compliant
- **Type hints** everywhere
- **Docstrings** for all public APIs
- **Comments** for complex logic
- **Clear naming** conventions

## 🚀 Future Extensions

### Plugin System

```python
class Plugin:
    def on_load(self): pass
    def on_update(self, dt): pass
    def on_render(self, screen): pass
    def on_command(self, cmd): pass
```

### Remote Connection

```python
class RemoteSession(TerminalSession):
    def __init__(self, ssh_client):
        self.ssh = ssh_client
```

### Session Recording

```python
class SessionRecorder:
    def record_frame(self, screen): pass
    def save_to_file(self, path): pass
```

---

This architecture ensures:
- ✅ **Modularity**: Easy to modify individual components
- ✅ **Testability**: Each component can be tested independently
- ✅ **Extensibility**: Easy to add new features
- ✅ **Maintainability**: Clear structure and responsibilities
- ✅ **Performance**: Optimized rendering and updates
- ✅ **Reliability**: Proper error handling and state management
