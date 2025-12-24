#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, time, math, random, signal, shutil

# Braille dots map
DOTS = [(0,0,1), (0,1,2), (0,2,4), (0,3,8), (1,0,16), (1,1,32), (1,2,64), (1,3,128)]

def braille_cell(bits):
    return chr(0x2800 + bits) if bits else " "

def clamp(x, a, b): return a if x < a else b if x > b else x

def rgb(r,g,b): return f"\x1b[38;2;{int(r)};{int(g)};{int(b)}m"
RESET = "\x1b[0m"

# Snow particles
snow_particles = []

def draw_frame(cols, rows, t):
    W, H = cols*2, rows*4
    cx, cy = W//2, int(H*0.46)
    height = int(H*0.60)
    radius = int(W*0.30)
    trunk_h = int(H*0.10)

    # Lighting
    lx = math.cos(t*0.9); ly = -0.2; lz = math.sin(t*0.6)
    
    # Buffer: (r,g,b) or None
    buf = [[None]*W for _ in range(H)]

    # 1. Update and Draw Snow
    global snow_particles
    # Spawn new snow
    if random.random() < 0.4:
        snow_particles.append([random.randint(0, W-1), 0, random.uniform(0.2, 0.8)]) # x, y, speed
    
    # Move snow
    new_snow = []
    for p in snow_particles:
        p[1] += p[2] # y += speed
        p[0] += math.sin(t + p[1]*0.1) * 0.5 # sway
        if p[1] < H:
            new_snow.append(p)
            ix, iy = int(p[0]), int(p[1])
            if 0 <= ix < W and 0 <= iy < H:
                # White/Cyan snow
                buf[iy][ix] = (220, 240, 255)
    snow_particles = new_snow

    # 2. Draw Tree (Cones)
    # Use layers for a "3D" feel
    levels = 15
    for i in range(levels):
        y_norm = i / levels # 0 top, 1 bottom
        layer_r = radius * y_norm
        layer_y_start = cy - int(height * (1.0 - y_norm))
        layer_h = height // levels + 2
        
        for ly_off in range(layer_h):
            curr_y = layer_y_start + ly_off
            if curr_y < 0 or curr_y >= H: continue
            
            # width at this y
            curr_r = int(layer_r * (1.0 + ly_off/layer_h))
            
            for x in range(cx - curr_r, cx + curr_r + 1):
                if x < 0 or x >= W: continue
                
                # Check circular shape
                dx = x - cx
                # approximate 3d cone normal
                nz = dx / (curr_r if curr_r else 1)
                
                # Light calc
                ndotl = clamp(nz*lx + ly, 0, 1) 
                
                # Color gradient (Cyberpunk Pine)
                # Dark Green -> Neon Green
                r_val = 20 + 40 * ndotl
                g_val = 100 + 155 * ndotl
                b_val = 50 + 50 * ndotl
                
                # Glitch effect
                if random.random() < 0.001:
                    r_val, g_val, b_val = 255, 0, 255 # Purple glitch
                
                buf[curr_y][x] = (int(r_val), int(g_val), int(b_val))

    # 3. Trunk
    tw = max(2, W//30)
    for y in range(trunk_h):
        sy = cy + y + 2
        if 0 <= sy < H:
            for x in range(cx - tw, cx + tw):
                if 0 <= x < W:
                    buf[sy][x] = (60, 40, 20)

    # 4. Star (Pulsing)
    sx, sy = cx, cy - height - 2
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            px, py = sx+dx, sy+dy
            if 0 <= px < W and 0 <= py < H:
                dist = dx*dx + dy*dy
                if dist < 6:
                    pulse = (math.sin(t*5)+1)/2
                    br = 150 + 105*pulse
                    buf[py][px] = (255, int(br), 0)

    # 5. Render to Braille
    out_lines = []
    for row in range(rows):
        y0 = row*4
        line_chars = []
        prev_col = None
        
        for col in range(cols):
            x0 = col*2
            bits = 0
            rs, gs, bs, n = 0,0,0,0
            
            for sx_off in range(2):
                for sy_off in range(4):
                    bx, by = x0+sx_off, y0+sy_off
                    if 0 <= bx < W and 0 <= by < H and buf[by][bx]:
                        r,g,b = buf[by][bx]
                        rs+=r; gs+=g; bs+=b; n+=1
                        for (dx,dy,mask) in DOTS:
                            if dx == sx_off and dy == sy_off:
                                bits |= mask
            
            if n > 0:
                curr_col = rgb(rs//n, gs//n, bs//n)
                if curr_col != prev_col:
                    line_chars.append(curr_col)
                    prev_col = curr_col
                line_chars.append(braille_cell(bits))
            else:
                if prev_col is not None:
                    line_chars.append(RESET)
                    prev_col = None
                line_chars.append(" ")
                
        if prev_col is not None:
            line_chars.append(RESET)
        out_lines.append("".join(line_chars))
        
    return "\n".join(out_lines)

def main():
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    sys.stdout.write("\x1b[?25l") # hide cursor
    
    # Init size
    cols, rows = shutil.get_terminal_size((80, 24))
    cols = max(40, cols-2)
    rows = max(20, rows-2)
    
    t0 = time.time()
    try:
        while True:
            t = time.time() - t0
            frame = draw_frame(cols, rows, t)
            sys.stdout.write("\x1b[H") # home
            sys.stdout.write(frame)
            sys.stdout.flush()
            time.sleep(0.08)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(RESET + "\x1b[?25h")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
