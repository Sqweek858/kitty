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

    # lumină direcțională în rotire (îmbunătățită pentru 3D)
    lx = math.cos(t*0.9); ly = -0.2; lz = math.sin(t*0.6)
    # buffer subpixeli: (r,g,b, on/off)
    buf = [[None]*W for _ in range(H)]
    
    # Buffer pentru umbre (shadow map)
    shadow_buf = [[0.0]*W for _ in range(H)]

    # fundal (ușor întunecat)
    bg = (10, 12, 14)
    
    # Zăpadă - particule care cad
    snow_particles = []
    if not hasattr(draw_frame, '_snow_init'):
        draw_frame._snow_init = True
        draw_frame._snow = [(random.uniform(0, W), random.uniform(-H, 0), random.uniform(0.5, 2.0)) for _ in range(30)]

    # UMBRĂ - desenează umbra bradului pe pământ (sub brad)
    shadow_y_start = cy + trunk_h + 2
    for y_offset in range(5):
        sy = shadow_y_start + y_offset
        if sy >= H: break
        shadow_width = int(radius * 0.8 * (1 - y_offset/5))
        for x in range(cx - shadow_width, cx + shadow_width):
            if 0 <= x < W:
                # Umbră mai întunecată la bază, mai deschisă la margini
                dist_from_center = abs(x - cx) / max(shadow_width, 1)
                shadow_intensity = (1 - dist_from_center) * (1 - y_offset/5) * 0.3
                shadow_buf[sy][x] = shadow_intensity

    # conul (frunzișul) - ÎMBUNĂTĂȚIT cu contururi 3D reale
    for y in range(height):
        # lățimea conului la înălțimea y
        r = int(radius * (1 - y/height))
        sy = cy - y
        if sy < 0 or sy >= H: continue
        
        # Contururi 3D - detectează marginile pentru contur mai pronunțat
        for x in range(cx - r, cx + r + 1):
            if x < 0 or x >= W: continue
            
            # Distanța de la centru
            dist_from_center = abs(x - cx)
            is_edge = (dist_from_center >= r - 2)  # Margine
            
            # normal aproximat pentru shading (pe con) - îmbunătățit
            nx = (x - cx) / max(r,1)
            ny = 0.6 + 0.2 * (1 - y/height)  # Normal mai pronunțat la vârf
            nz = (height - y) / height
            
            # Normalizare normală
            norm_len = math.sqrt(nx*nx + ny*ny + nz*nz)
            if norm_len > 0:
                nx /= norm_len; ny /= norm_len; nz /= norm_len
            
            # lambert shading îmbunătățit
            ndotl = clamp(nx*lx + ny*ly + nz*lz, 0, 1)
            
            # Contururi 3D - umbrire mai pronunțată la margini
            if is_edge:
                ndotl *= 0.6  # Margini mai întunecate pentru efect 3D
            
            # culoare brad cu gradient
            base = (20, 120, 40)
            tip  = (60, 200, 80)
            k = y / height
            g = (base[0]*(1-k) + tip[0]*k,
                 base[1]*(1-k) + tip[1]*k,
                 base[2]*(1-k) + tip[2]*k)
            
            # Shading cu umbră
            shadow_factor = 1.0 - shadow_buf[sy][x] * 0.2
            shade = (g[0]*(0.3+0.7*ndotl)*shadow_factor, 
                    g[1]*(0.3+0.7*ndotl)*shadow_factor, 
                    g[2]*(0.3+0.7*ndotl)*shadow_factor)
            buf[sy][x] = (int(clamp(shade[0], 0, 255)), 
                          int(clamp(shade[1], 0, 255)), 
                          int(clamp(shade[2], 0, 255)))

    # trunchi
    tw = max(2, W//30)
    for y in range(trunk_h):
        sy = cy + y + 2
        if sy < 0 or sy >= H: continue
        for x in range(cx - tw, cx + tw):
            if 0 <= x < W:
                ndotl = clamp(0.3 + 0.7*math.cos((x-cx)*0.5), 0, 1)
                brown = (110*ndotl, 70*ndotl, 40*ndotl)
                buf[sy][x] = (int(brown[0]), int(brown[1]), int(brown[2]))

    # stea sus (pulsează)
    sx, sy = cx, cy - height - 2
    for dy in range(-1,3):
        for dx in range(-2,3):
            x, y = sx+dx, sy+dy
            if 0 <= x < W and 0 <= y < H:
                p = 0.5 + 0.5*math.sin(t*3.0 + (dx*dx+dy*dy))
                col = (240, 220, 80 + int(60*p))
                buf[y][x] = col

    # globuri (poziții fixe + flicker ÎMBUNĂTĂȚIT)
    if not hasattr(draw_frame, '_bulbs_init'):
        draw_frame._bulbs_init = True
        random.seed(42)
        draw_frame._bulbs = []
        for band in range(8, height-6, max(3, height//14)):
            r = int(radius * (1 - band/height))
            for i in range(6):
                ang = (i/6)*math.pi*2 + band*0.23
                x = int(cx + r*math.cos(ang))
                y = cy - band
                draw_frame._bulbs.append((x, y, random.random()))
    
    bulbs = draw_frame._bulbs
    for (x, y, phase) in bulbs:
        if 0 <= x < W and 0 <= y < H:
            hue = (math.sin(x*0.2 + y*0.3 + phase) * 0.5 + 0.5)
            # Pâlpâire mai realistă - unele becuri pâlpâiesc mai mult
            flick_base = 0.5 + phase * 0.3  # Fiecare bec are o intensitate de bază diferită
            flick_speed = 5.0 + phase * 3.0  # Viteze diferite de pâlpâire
            flick = flick_base + (1 - flick_base) * 0.5 * (1 + math.sin(t * flick_speed + x*0.7 + y*0.5))
            
            # Culori mai vibrante
            r = int(200 + 55*hue)
            g = int(80 + 140*(1-hue))
            b = int(110 + 110*(1-abs(0.5-hue)*2))
            col = (clamp(r*flick,0,255), clamp(g*flick,0,255), clamp(b*flick,0,255))
            buf[y][x] = (int(col[0]), int(col[1]), int(col[2]))
            
            # Halo mai mare și mai pronunțat
            for hy in (y-1, y, y+1):
                for hx in (x-1, x, x+1):
                    if 0 <= hx < W and 0 <= hy < H and buf[hy][hx] is not None:
                        dist = math.sqrt((hx-x)**2 + (hy-y)**2)
                        if dist <= 1.5:
                            intensity = 1.0 - dist * 0.4
                            br, gc, bc = buf[hy][hx]
                            buf[hy][hx] = (min(255, int(br*0.6 + col[0]*0.4*intensity)),
                                          min(255, int(gc*0.6 + col[1]*0.4*intensity)),
                                          min(255, int(bc*0.6 + col[2]*0.4*intensity)))
    
    # ZĂPADĂ - animație cu particule care cad spre brad
    if not hasattr(draw_frame, '_snow'):
        draw_frame._snow = [(random.uniform(0, W), random.uniform(-H, 0), random.uniform(0.5, 2.0)) for _ in range(30)]
    
    snow = draw_frame._snow
    new_snow = []
    for sx, sy, speed in snow:
        # Actualizează poziția (cade în jos și ușor spre centru)
        new_sy = sy + speed * 0.3
        drift = (cx - sx) * 0.01  # Derivează ușor spre centru (brad)
        new_sx = sx + drift
        
        # Dacă a ajuns jos sau a ieșit din ecran, resetează
        if new_sy > H or new_sx < 0 or new_sx >= W:
            new_sx = random.uniform(0, W)
            new_sy = random.uniform(-H*0.5, 0)
            speed = random.uniform(0.5, 2.0)
        
        new_snow.append((new_sx, new_sy, speed))
        
        # Desenează fulgul de zăpadă
        ix, iy = int(new_sx), int(new_sy)
        if 0 <= ix < W and 0 <= iy < H:
            # Verifică dacă e peste brad (nu desena zăpada peste brad)
            dist_from_center = abs(ix - cx)
            tree_radius_at_y = int(radius * (1 - (cy - iy)/height)) if iy < cy else radius
            if dist_from_center > tree_radius_at_y + 2:  # Doar în afara bradului
                snow_col = (200, 220, 255)  # Alb-albăstrui
                buf[iy][ix] = snow_col
                # Mică umbră sub fulg
                if iy + 1 < H and buf[iy+1][ix] is not None:
                    old_col = buf[iy+1][ix]
                    buf[iy+1][ix] = tuple(min(255, c + 20) for c in old_col)
                elif iy + 1 < H:
                    buf[iy+1][ix] = (30, 32, 34)  # Umbră ușoară pe fundal
    
    draw_frame._snow = new_snow

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
