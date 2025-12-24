#!/usr/bin/env python3
# -- coding: utf-8 --
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

def draw_frame(cols, rows, t):
    # canvas subpixel: width = cols*2, height = rows*4
    W, H = cols*2, rows*4
    # centru și raze pentru con (arbore) în spațiul ecranului
    cx, cy = W//2, int(H*0.46)
    # parametri „3D” simulați
    height = int(H*0.60)
    radius = int(W*0.30)
    trunk_h = int(H*0.10)

    # lumină direcțională în rotire (mai lentă și mai subtilă)
    lx = math.cos(t*0.3); ly = -0.3; lz = math.sin(t*0.25)
    # buffer subpixeli: (r,g,b)
    buf = [[None]*W for _ in range(H)]

    # fundal (ușor întunecat)
    bg = (10, 12, 14)
    
    # zăpadă care pică
    snow_count = 30
    random.seed(int(t * 10))
    snow_particles = []
    for i in range(snow_count):
        sx = int((random.random() * W))
        sy = int((random.random() * H + t * 15) % H)
        snow_particles.append((sx, sy))

    # conul (frunzișul) cu shading îmbunătățit
    for y in range(height):
        # lățimea conului la înălțimea y
        r = int(radius * (1 - y/height))
        sy = cy - y
        if sy < 0 or sy >= H: continue
        for x in range(cx - r, cx + r + 1):
            if x < 0 or x >= W: continue
            
            # Calculează distanța de la centru pentru efect 3D
            dx = (x - cx) / max(r, 1)
            dist_from_center = abs(dx)
            
            # Normal vector pentru suprafața conică
            nx = dx
            ny = 0.4
            nz = math.sqrt(max(0, 1 - nx*nx - ny*ny))
            
            # Normalizare
            length = math.sqrt(nx*nx + ny*ny + nz*nz)
            if length > 0:
                nx /= length; ny /= length; nz /= length
            
            # Lambert shading + ambient
            ndotl = clamp(nx*lx + ny*ly + nz*lz, 0, 1)
            ambient = 0.25
            diffuse = 0.75 * ndotl
            lighting = ambient + diffuse
            
            # Rim light pentru contur 3D
            rim = (1 - abs(dx)) * 0.2
            
            # Culoare brad cu gradient vertical
            base = (15, 100, 35)
            tip  = (40, 180, 70)
            k = y / height
            g = (base[0]*(1-k) + tip[0]*k,
                 base[1]*(1-k) + tip[1]*k,
                 base[2]*(1-k) + tip[2]*k)
            
            # Aplică iluminare + rim light
            shade = (
                clamp(g[0] * lighting + rim * 50, 0, 255),
                clamp(g[1] * lighting + rim * 80, 0, 255),
                clamp(g[2] * lighting + rim * 50, 0, 255)
            )
            buf[sy][x] = (int(shade[0]), int(shade[1]), int(shade[2]))

    # trunchi cu textură îmbunătățită
    tw = max(3, W//28)
    for y in range(trunk_h):
        sy = cy + y + 2
        if sy < 0 or sy >= H: continue
        for x in range(cx - tw, cx + tw):
            if 0 <= x < W:
                # Shading pe trunchi
                dx = (x - cx) / max(tw, 1)
                ndotl = clamp(0.4 + 0.6 * math.cos(dx * math.pi * 0.5), 0, 1)
                
                # Adaugă "coajă" cu noise
                bark_noise = (math.sin(x * 0.7) * math.cos(y * 0.5) * 0.15 + 1) * 0.5
                
                brown = (
                    clamp(90 * ndotl * bark_noise, 20, 130),
                    clamp(55 * ndotl * bark_noise, 15, 80),
                    clamp(30 * ndotl * bark_noise, 10, 50)
                )
                buf[sy][x] = (int(brown[0]), int(brown[1]), int(brown[2]))

    # stea sus (pulsează și strălucește)
    sx, sy = cx, cy - height - 3
    star_pulse = 0.5 + 0.5 * math.sin(t * 4.0)
    star_size = 2 + int(star_pulse)
    
    for dy in range(-star_size, star_size + 1):
        for dx in range(-star_size, star_size + 1):
            x, y = sx + dx, sy + dy
            if 0 <= x < W and 0 <= y < H:
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < star_size:
                    intensity = (1 - dist / star_size) * star_pulse
                    col = (
                        clamp(200 + int(55 * intensity), 0, 255),
                        clamp(180 + int(75 * intensity), 0, 255),
                        clamp(60 + int(80 * intensity), 0, 255)
                    )
                    buf[y][x] = col

    # globuri (poziții fixe + flicker îmbunătățit)
    random.seed(42)
    bulbs = []
    for band in range(10, height-8, max(4, height//12)):
        r = int(radius * (1 - band/height) * 0.8)
        num_bulbs = 5 + (band % 3)
        for i in range(num_bulbs):
            ang = (i/num_bulbs)*math.pi*2 + band*0.4 + t*0.1
            x = int(cx + r*math.cos(ang))
            y = cy - band
            bulbs.append((x, y, ang))
    
    for (x, y, ang) in bulbs:
        if 0 <= x < W and 0 <= y < H:
            hue = (math.sin(ang + t*0.5) * 0.5 + 0.5)
            # pâlpâit îmbunătățit
            flick = 0.6 + 0.4 * math.sin(t * 8.0 + x*1.2 + y*0.8)
            
            # Culori mai vibrante
            if hue < 0.33:
                # Roșu
                r, g, b = int(255*flick), int(40*flick), int(60*flick)
            elif hue < 0.66:
                # Verde/Cyan
                r, g, b = int(40*flick), int(220*flick), int(180*flick)
            else:
                # Galben/Gold
                r, g, b = int(255*flick), int(200*flick), int(40*flick)
            
            col = (clamp(r, 0, 255), clamp(g, 0, 255), clamp(b, 0, 255))
            buf[y][x] = col
            
            # Halo mai mare
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    hx, hy = x + dx, y + dy
                    if 0 <= hx < W and 0 <= hy < H and (dx != 0 or dy != 0):
                        if buf[hy][hx] is not None:
                            br, gc, bc = buf[hy][hx]
                            blend = 0.4
                            buf[hy][hx] = (
                                min(255, int(br*(1-blend) + col[0]*blend)),
                                min(255, int(gc*(1-blend) + col[1]*blend)),
                                min(255, int(bc*(1-blend) + col[2]*blend))
                            )
    
    # Zăpadă
    for (sx, sy) in snow_particles:
        if 0 <= sx < W and 0 <= sy < H:
            buf[sy][sx] = (220, 230, 255)

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
            time.sleep(0.07)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(RESET + "\x1b[?25h")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
