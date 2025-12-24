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

    # lumină direcțională în rotire
    lx = math.cos(t*0.9); ly = -0.2; lz = math.sin(t*0.6)
    # buffer subpixeli: (r,g,b, on/off)
    buf = [[None]*W for _ in range(H)]

    # fundal (ușor întunecat)
    bg = (10, 12, 14)

    # conul (frunzișul)
    for y in range(height):
        # lățimea conului la înălțimea y
        r = int(radius * (1 - y/height))
        sy = cy - y
        if sy < 0 or sy >= H: continue
        for x in range(cx - r, cx + r + 1):
            if x < 0 or x >= W: continue
            # normal aproximat pentru shading (pe con)
            nx = (x - cx) / max(r,1)
            ny = 0.6
            nz = (height - y) / height
            # lambert
            ndotl = clamp(nx*lx + ny*ly + nz*lz, 0, 1)
            # culoare brad cu gradient
            base = (20, 120, 40)
            tip  = (60, 200, 80)
            k = y / height
            g = (base[0]*(1-k) + tip[0]*k,
                 base[1]*(1-k) + tip[1]*k,
                 base[2]*(1-k) + tip[2]*k)
            shade = (g[0]*(0.3+0.7*ndotl), g[1]*(0.3+0.7*ndotl), g[2]*(0.3+0.7*ndotl))
            buf[sy][x] = (int(shade[0]), int(shade[1]), int(shade[2]))

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

    # globuri (poziții fixe + flicker)
    random.seed(42)
    bulbs = []
    for band in range(8, height-6, max(3, height//14)):
        r = int(radius * (1 - band/height))
        for i in range(6):
            ang = (i/6)*math.pi*2 + band*0.23
            x = int(cx + r*math.cos(ang))
            y = cy - band
            bulbs.append((x,y))
    for (x,y) in bulbs:
        if 0 <= x < W and 0 <= y < H:
            hue = (math.sin(x*0.2 + y*0.3) * 0.5 + 0.5)
            # palpaire
            flick = 0.7 + 0.3*math.sin(t*7.0 + x*0.7 + y*0.5)
            r = int(200 + 55*hue)
            g = int(80 + 140*(1-hue))
            b = int(110 + 110*(1-abs(0.5-hue)*2))
            col = (clamp(r*flick,0,255), clamp(g*flick,0,255), clamp(b*flick,0,255))
            buf[y][x] = (int(col[0]), int(col[1]), int(col[2]))
            # mic halo
            for hx in (x-1, x+1):
                if 0 <= hx < W and 0 <= y < H and buf[y][hx] is not None:
                    br,gc,bc = buf[y][hx]
                    buf[y][hx] = (min(255,int(br*0.7+col[0]*0.3)),
                                  min(255,int(gc*0.7+col[1]*0.3)),
                                  min(255,int(bc*0.7+col[2]*0.3)))

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
