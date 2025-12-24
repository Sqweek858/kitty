#!/usr/bin/env python3
# -- coding: utf-8 --
import sys
import time
import math
import random
import shutil
import signal

# -----------------------------------------------------------------------------
# Configuration & Constants
# -----------------------------------------------------------------------------
# Braille patterns: 2x4 dots per character
# Dots mapping:
#   1 4
#   2 5
#   3 6
#   7 8
# Unicode offset: 0x2800
DOT_MAP = [
    (0, 0, 0x01), (1, 0, 0x08),
    (0, 1, 0x02), (1, 1, 0x10),
    (0, 2, 0x04), (1, 2, 0x20),
    (0, 3, 0x40), (1, 3, 0x80)
]

def rgb(r, g, b):
    """Return ANSI escape sequence for truecolor foreground."""
    return f"\x1b[38;2;{int(r)};{int(g)};{int(b)}m"

RESET = "\x1b[0m"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
CLEAR_SCREEN = "\x1b[2J\x1b[H"
HOME_CURSOR = "\x1b[H"

class Canvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Pixel buffer: each element is (r, g, b) or None
        # We use a 1D array for performance, index = y * width + x
        self.pixels = [None] * (width * height)
        self.depth_buffer = [-9999.0] * (width * height)

    def clear(self):
        self.pixels = [None] * (len(self.pixels))
        self.depth_buffer = [-9999.0] * (len(self.depth_buffer))

    def set_pixel(self, x, y, r, g, b, depth=0.0):
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = y * self.width + x
            if depth > self.depth_buffer[idx]:
                self.pixels[idx] = (r, g, b)
                self.depth_buffer[idx] = depth

    def render(self):
        # Convert pixels to Braille characters
        # Output cols = width // 2, Output rows = height // 4
        out_cols = self.width // 2
        out_rows = self.height // 4
        
        buffer = []
        prev_color = None
        
        for r in range(out_rows):
            line_parts = []
            for c in range(out_cols):
                base_x = c * 2
                base_y = r * 4
                
                dots = 0
                # Calculate average color for the cell
                sum_r, sum_g, sum_b, count = 0, 0, 0, 0
                
                for dx, dy, mask in DOT_MAP:
                    px = base_x + dx
                    py = base_y + dy
                    if 0 <= px < self.width and 0 <= py < self.height:
                        idx = py * self.width + px
                        pixel = self.pixels[idx]
                        if pixel:
                            dots |= mask
                            sum_r += pixel[0]
                            sum_g += pixel[1]
                            sum_b += pixel[2]
                            count += 1
                
                if count > 0:
                    avg_color = rgb(sum_r // count, sum_g // count, sum_b // count)
                    if avg_color != prev_color:
                        line_parts.append(avg_color)
                        prev_color = avg_color
                    
                    if dots == 0:
                         # Should not happen if count > 0 usually, but braille logic is distinct
                         # If pixels exist but map to 0 dots (unlikely with this map), we show space?
                         # Actually if pixel exists, at least one dot is set.
                         pass
                    
                    line_parts.append(chr(0x2800 + dots))
                else:
                    if prev_color is not None:
                        line_parts.append(RESET)
                        prev_color = None
                    line_parts.append(" ")
            
            if prev_color is not None:
                line_parts.append(RESET)
                prev_color = None
            line_parts.append("\n")
            buffer.append("".join(line_parts))
            
        return "".join(buffer)

# -----------------------------------------------------------------------------
# 3D Math & Objects
# -----------------------------------------------------------------------------
def rotate_y(x, y, z, theta):
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return x * cos_t + z * sin_t, y, -x * sin_t + z * cos_t

def project(x, y, z, width, height, scale=1.0):
    # Simple perspective projection
    # Camera at (0, 0, -5)
    cam_z = 5.0
    factor = scale / (z + cam_z)
    px = int(x * factor * width + width / 2)
    py = int(-y * factor * width + height / 2) # Aspect ratio assumed roughly square per unit
    return px, py, z

class Tree:
    def __init__(self):
        self.layers = 15
        self.lights = []
        # Generate random lights positions on the cone surface
        # We'll calculate them dynamically during render to rotate
        self.static_lights = []
        for i in range(50):
            h = random.uniform(0, 1) # Height 0 to 1
            angle = random.uniform(0, math.pi * 2)
            r = 1.0 - h # Radius at height h
            self.static_lights.append((h, angle, r))

    def draw(self, canvas, time_t):
        w, h = canvas.width, canvas.height
        
        # Tree rotation
        theta = time_t * 1.0
        
        # 1. Draw Tree Body (Cones)
        # We simulate a cone by drawing points
        # Density needs to be high for solid look
        
        steps_h = 60
        for i in range(steps_h):
            y_norm = i / steps_h # 0 (base) to 1 (tip)
            radius = (1.0 - y_norm) * 0.8
            y_world = y_norm * 2.0 - 1.0 # -1 to 1
            
            circumference = 2 * math.pi * radius
            steps_a = int(circumference * 60) + 1
            
            for j in range(steps_a):
                angle = (j / steps_a) * math.pi * 2
                x_world = radius * math.cos(angle)
                z_world = radius * math.sin(angle)
                
                # Deform slightly for branches
                r_mod = 1.0 + 0.1 * math.sin(angle * 5 + y_norm * 10)
                x_world *= r_mod
                z_world *= r_mod

                # Rotate
                rx, ry, rz = rotate_y(x_world, y_world, z_world, theta)
                
                # Project
                px, py, pz = project(rx, ry, rz, w, h, scale=0.8)
                
                # Lighting (Normals)
                # Normal of a cone surface approx (x, 0.5, z)
                nx, ny, nz = x_world, 0.5, z_world
                # Rotate normal
                nrx, nry, nrz = rotate_y(nx, ny, nz, theta)
                
                # Light dir
                ldx, ldy, ldz = 0.5, 0.5, -1.0 # Front-top-right
                dot = nrx * ldx + nry * ldy + nrz * ldz
                dot = max(0.0, dot)
                
                # Color gradient (Dark Green to Light Green)
                base_g = 60 + int(y_norm * 100)
                col_r = int(20 * dot)
                col_g = int(base_g * (0.5 + 0.5 * dot))
                col_b = int(20 * dot)
                
                canvas.set_pixel(px, py, col_r, col_g, col_b, depth=pz)

        # 2. Draw Trunk
        trunk_h = 0.4
        trunk_r = 0.15
        for i in range(20):
            y_norm = i / 20
            y_world = -1.0 - y_norm * trunk_h
            steps_a = 20
            for j in range(steps_a):
                angle = (j / steps_a) * math.pi * 2
                x_world = trunk_r * math.cos(angle)
                z_world = trunk_r * math.sin(angle)
                
                rx, ry, rz = rotate_y(x_world, y_world, z_world, theta)
                px, py, pz = project(rx, ry, rz, w, h, scale=0.8)
                
                # Brown
                canvas.set_pixel(px, py, 100, 60, 20, depth=pz)

        # 3. Draw Lights/Ornaments
        for idx, (lh, lang, lr) in enumerate(self.static_lights):
            # Blink logic
            if idx % 3 == 0:
                blink = math.sin(time_t * 5 + idx) > 0
                if not blink: continue
            
            y_world = lh * 2.0 - 1.0
            x_world = lr * 0.8 * math.cos(lang)
            z_world = lr * 0.8 * math.sin(lang)
            
            rx, ry, rz = rotate_y(x_world, y_world, z_world, theta)
            px, py, pz = project(rx, ry, rz, w, h, scale=0.8)
            
            # Colors: Red, Gold, Blue
            colors = [(255, 0, 0), (255, 215, 0), (0, 100, 255)]
            c = colors[idx % 3]
            
            # Draw a bigger dot (cross)
            canvas.set_pixel(px, py, c[0], c[1], c[2], depth=pz + 0.1)
            canvas.set_pixel(px+1, py, c[0], c[1], c[2], depth=pz + 0.1)
            canvas.set_pixel(px, py+1, c[0], c[1], c[2], depth=pz + 0.1)
            canvas.set_pixel(px-1, py, c[0], c[1], c[2], depth=pz + 0.1)
            canvas.set_pixel(px, py-1, c[0], c[1], c[2], depth=pz + 0.1)

        # 4. Star on top
        star_y = 1.05
        sx, sy, sz = rotate_y(0, star_y, 0, theta)
        spx, spy, spz = project(sx, sy, sz, w, h, scale=0.8)
        
        pulse = 0.5 + 0.5 * math.sin(time_t * 3)
        star_c = (255, 255, int(100 + 155 * pulse))
        
        # Draw Star Shape
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if abs(dx) + abs(dy) <= 4:
                    canvas.set_pixel(spx+dx, spy+dy, star_c[0], star_c[1], star_c[2], depth=spz+0.2)


class SnowSystem:
    def __init__(self, count=100):
        self.flakes = []
        for _ in range(count):
            self.flakes.append([random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)])

    def update_and_draw(self, canvas, time_t, dt):
        w, h = canvas.width, canvas.height
        for f in self.flakes:
            f[1] -= 1.0 * dt # Fall down
            f[0] += math.sin(time_t + f[1]) * 0.01 # Sway
            
            if f[1] < -2:
                f[1] = 2
                f[0] = random.uniform(-2, 2)
                f[2] = random.uniform(-2, 2)
            
            # Project
            px, py, pz = project(f[0], f[1], f[2], w, h, scale=0.8)
            
            canvas.set_pixel(px, py, 200, 200, 255, depth=pz - 10) # Background snow

class StarField:
    def __init__(self, count=200):
        self.stars = []
        for _ in range(count):
            self.stars.append((random.random(), random.random(), random.uniform(0.5, 1.5))) # x, y, size

    def draw(self, canvas):
        w, h = canvas.width, canvas.height
        for x, y, s in self.stars:
            px = int(x * w)
            py = int(y * h)
            # Twinkle
            if random.random() > 0.95:
                col = (255, 255, 255)
            else:
                col = (100, 100, 150)
            canvas.set_pixel(px, py, col[0], col[1], col[2], depth=-100)

def main():
    # Setup
    cols, rows = shutil.get_terminal_size()
    # Braille canvas: 2x width, 4x height resolution
    cw, ch = cols * 2, rows * 4
    
    canvas = Canvas(cw, ch)
    tree = Tree()
    snow = SnowSystem(150)
    stars = StarField(300)
    
    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.write(CLEAR_SCREEN)
    
    t0 = time.time()
    last_t = t0
    
    try:
        while True:
            cur_t = time.time()
            dt = cur_t - last_t
            last_t = cur_t
            t = cur_t - t0
            
            canvas.clear()
            
            # Draw Layers
            stars.draw(canvas)
            snow.update_and_draw(canvas, t, dt)
            tree.draw(canvas, t)
            
            # Render
            frame = canvas.render()
            
            sys.stdout.write(HOME_CURSOR)
            sys.stdout.write(frame)
            
            # Stats or text
            # sys.stdout.write(f"{RESET}FPS: {1.0/dt:.1f}")
            
            sys.stdout.flush()
            
            time.sleep(0.05)
            
            # Check for resize
            nc, nr = shutil.get_terminal_size()
            if nc != cols or nr != rows:
                cols, rows = nc, nr
                cw, ch = cols * 2, rows * 4
                canvas = Canvas(cw, ch)
                sys.stdout.write(CLEAR_SCREEN)

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(RESET)
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.write(CLEAR_SCREEN)

if __name__ == "__main__":
    main()
