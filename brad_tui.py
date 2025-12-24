#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, time, math, random, signal
import shutil

# desen pe matrice de "sub-pixeli" Braille (2x4 per celulă)
# https://en.wikipedia.org/wiki/Braille_Patterns
DOTS = [(0,0,1), (0,1,2), (0,2,4), (0,3,8), (1,0,16), (1,1,32), (1,2,64), (1,3,128)]

def braille_cell(bits):
    return chr(0x2800 + bits) if bits else " "

def clamp(x, a, b): return a if x < a else b if x > b else x

def rgb(r,g,b): return f"\x1b[38;2;{int(r)};{int(g)};{int(b)}m"
RESET = "\x1b[0m"

# Snow particles
snow_particles = []

def init_snow(W, H, count=50):
    global snow_particles
    snow_particles = []
    for _ in range(count):
        snow_particles.append({
            'x': random.uniform(0, W),
            'y': random.uniform(0, H),
            'speed': random.uniform(0.2, 0.8),
            'sway': random.uniform(0, 2*math.pi)
        })

def update_snow(W, H, dt):
    global snow_particles
    if not snow_particles:
        init_snow(W, H)
    
    for p in snow_particles:
        p['y'] += p['speed']
        p['x'] += math.sin(p['sway']) * 0.3
        p['sway'] += 0.1
        if p['y'] >= H:
            p['y'] = 0
            p['x'] = random.uniform(0, W)

def draw_frame(cols, rows, t):
    # canvas subpixel: width = cols*2, height = rows*4
    W, H = cols*2, rows*4
    # centru și raze pentru con (arbore) în spațiul ecranului
    cx, cy = W//2, int(H*0.75)  # Moved tree down a bit
    # parametri „3D” simulați
    height = int(H*0.65)
    radius = int(W*0.35)
    trunk_h = int(H*0.10)

    # lumină direcțională în rotire
    lx = math.cos(t*0.9); ly = -0.5; lz = math.sin(t*0.6)
    # buffer subpixeli: (r,g,b)
    # Background gradient
    buf = [[None]*W for _ in range(H)]
    
    # Update snow
    update_snow(W, H, 0.1)

    # Draw background snow
    for p in snow_particles:
        px, py = int(p['x']), int(p['y'])
        if 0 <= px < W and 0 <= py < H:
             # Depth effect: dimmer if "far" (slower)
             b = int(150 + p['speed']*100)
             buf[py][px] = (b, b, b+20)

    # conul (frunzișul) - Multiple layers for 3D effect
    layers = 5
    layer_height = height / layers
    
    for i in range(layers):
        layer_y_start = cy - height + i * (height // layers)
        layer_h = int(height // layers * 1.5) # Overlap
        current_radius = int(radius * (i+1) / layers)
        
        # Draw cone segment
        for y in range(layer_h):
            py = int(layer_y_start + y)
            if py < 0 or py >= H: continue
            
            rel_y = y / layer_h
            r = int(current_radius * (0.2 + 0.8 * rel_y)) # Cone shape
            
            sy = py
            for x in range(cx - r, cx + r + 1):
                if x < 0 or x >= W: continue
                
                # Check circularity for 3D feel
                dx = (x - cx)
                if dx*dx + (y-layer_h)**2 * 0.2 > r*r: continue # Fake perspective

                # Normal map logic
                nx = dx / r
                ny = 0.3
                nz = math.sqrt(max(0, 1 - nx*nx - ny*ny))
                
                # Lighting
                ndotl = clamp(nx*lx + ny*ly + nz*lz, 0, 1)
                
                # Base Color
                base = (10, 80 + i*10, 20)
                tip  = (40, 160 + i*15, 60)
                
                # Gradient
                k = 1 - rel_y
                col_r = base[0]*(1-k) + tip[0]*k
                col_g = base[1]*(1-k) + tip[1]*k
                col_b = base[2]*(1-k) + tip[2]*k
                
                # Shadow from layer above
                shadow = 1.0
                if i > 0 and y < layer_h * 0.3:
                    shadow = 0.6 + 0.4 * (y / (layer_h*0.3))

                # Final shade
                light = 0.3 + 0.7 * ndotl
                
                final_r = int(col_r * light * shadow)
                final_g = int(col_g * light * shadow)
                final_b = int(col_b * light * shadow)
                
                buf[sy][x] = (final_r, final_g, final_b)

    # trunchi
    tw = max(3, W//25)
    for y in range(trunk_h):
        sy = cy + y
        if sy < 0 or sy >= H: continue
        for x in range(cx - tw, cx + tw):
            if 0 <= x < W:
                # Cylindrical shading
                xn = (x - cx) / tw
                ndotl = clamp(0.3 + 0.7*math.cos(xn*1.5 + t*0.2), 0, 1)
                brown = (100*ndotl, 60*ndotl, 30*ndotl)
                buf[sy][x] = (int(brown[0]), int(brown[1]), int(brown[2]))

    # stea sus (pulsează)
    sx, sy = cx, cy - height - 3
    for dy in range(-2,3):
        for dx in range(-3,4):
            x, y = sx+dx, sy+dy
            if 0 <= x < W and 0 <= y < H:
                dist = dx*dx + dy*dy
                if dist < 6:
                    p = 0.5 + 0.5*math.sin(t*4.0)
                    col = (255, 220, 50 + int(50*p))
                    # Glow
                    buf[y][x] = col

    # globuri (poziții fixe + flicker)
    random.seed(42)
    bulbs = []
    for band in range(10, height-5, max(5, height//10)):
        r = int(radius * (1 - band/height) * 0.8)
        for i in range(5):
            ang = (i/5)*math.pi*2 + band*0.5
            x = int(cx + r*math.cos(ang + t*0.5)) # Rotate bulbs with tree? No, just static positions on cone
            # 3D rotation effect for bulbs
            rot_ang = ang + t * 0.5
            z = r * math.sin(rot_ang)
            if z < 0: continue # Behind the tree

            x_2d = int(cx + r * math.cos(rot_ang))
            y_2d = cy - band + int(z * 0.1) # Tilt
            
            bulbs.append((x_2d, y_2d))

    for (x,y) in bulbs:
        if 0 <= x < W and 0 <= y < H:
            hue = (math.sin(x*0.1 + y*0.1) * 0.5 + 0.5)
            # palpaire
            flick = 0.8 + 0.2*math.sin(t*10.0 + x)
            r = int(220 + 35*hue)
            g = int(50 + 50*(1-hue))
            b = int(50 + 200*hue)
            col = (clamp(r*flick,0,255), clamp(g*flick,0,255), clamp(b*flick,0,255))
            buf[y][x] = (int(col[0]), int(col[1]), int(col[2]))

    # compunere în celule Braille
    out_lines = []
    for row in range(rows):
        y0 = row*4
        line = []
        prev_rgb = None
        for col in range(cols):
            x0 = col*2
            bits = 0
            # mix simplu pentru culoare celulă: medie pe subpixeli validați
            rs = gs = bs = n = 0
            for sx in range(2):
                for sy in range(4):
                    x, y = x0+sx, y0+sy
                    if 0 <= x < W and 0 <= y < H and buf[y][x] is not None:
                        r,g,b = buf[y][x]
                        rs += r; gs += g; bs += b; n += 1
                        # setează bitul braille
                        for (dx,dy,mask) in DOTS:
                            if dx == sx and dy == sy:
                                bits |= mask
            if n == 0:
                # fundal
                if prev_rgb is not None:
                    line.append(RESET)
                    prev_rgb = None
                line.append(" ")
            else:
                r = rs//n; g = gs//n; b = bs//n
                colseq = rgb(r,g,b)
                if colseq != prev_rgb:
                    line.append(colseq); prev_rgb = colseq
                line.append(braille_cell(bits))
        if prev_rgb is not None:
            line.append(RESET)
        out_lines.append("".join(line))
    return "\n".join(out_lines)

def main():
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    sys.stdout.write("\x1b[?25l")  # hide cursor
    sys.stdout.write("\x1b[2J\x1b[H")  # clear
    sys.stdout.flush()

    # dimensiunea consolei (în celule text)
    cols, rows = shutil.get_terminal_size((80, 24))
    # lasă puțin spațiu de margini
    cols = max(40, cols-2)
    rows = max(20, rows-2)

    t0 = time.time()
    try:
        while True:
            t = time.time() - t0
            frame = draw_frame(cols, rows, t)
            sys.stdout.write("\x1b[H")  # home
            sys.stdout.write(frame)
            sys.stdout.write(RESET)
            sys.stdout.flush()
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(RESET + "\x1b[?25h")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
