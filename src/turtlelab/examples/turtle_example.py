import math
import random

# -----------------------------
# Celestial Lotus Mandala
# -----------------------------


screen = s
screen.bgcolor("#060816")
screen.colormode(255)
screen.tracer(0, 0)

pen = t
pen.speed(3)
pen.pensize(2)
pen.penup()

rng = random.Random(42)

def rgb(hexcolor):
    hexcolor = hexcolor.lstrip("#")
    return tuple(int(hexcolor[i:i+2], 16) for i in (0, 2, 4))

def mix(c1, c2, a):
    return tuple(int(c1[i] * (1 - a) + c2[i] * a) for i in range(3))

def goto(p, x, y):
    p.penup()
    p.goto(x, y)
    p.pendown()

def draw_polygon(p, n, radius, rotation=0, color=(255, 255, 255), pensize=1):
    p.pensize(pensize)
    p.pencolor(color)
    pts = []
    for i in range(n):
        ang = rotation + 2 * math.pi * i / n
        pts.append((radius * math.cos(ang), radius * math.sin(ang)))
    goto(p, *pts[0])
    for pt in pts[1:]:
        p.goto(*pt)
    p.goto(*pts[0])

def draw_starburst(p, rays, inner_r, outer_r, rotation=0, color=(255, 255, 255), pensize=1):
    p.pensize(pensize)
    p.pencolor(color)
    for i in range(rays):
        ang = rotation + 2 * math.pi * i / rays
        x1, y1 = inner_r * math.cos(ang), inner_r * math.sin(ang)
        x2, y2 = outer_r * math.cos(ang), outer_r * math.sin(ang)
        goto(p, x1, y1)
        p.goto(x2, y2)

def draw_ring_dots(p, count, radius, dot_size, colors, rotation=0):
    for i in range(count):
        ang = rotation + 2 * math.pi * i / count
        x = radius * math.cos(ang)
        y = radius * math.sin(ang)
        p.penup()
        p.goto(x, y - dot_size / 2)
        p.dot(dot_size, colors[i % len(colors)])

def draw_parametric(p, fn, t0, t1, steps, color, pensize=1):
    p.pencolor(color)
    p.pensize(pensize)
    x0, y0 = fn(t0)
    goto(p, x0, y0)
    for i in range(1, steps + 1):
        tt = t0 + (t1 - t0) * i / steps
        x, y = fn(tt)
        p.goto(x, y)

def rose_curve(k, scale):
    def f(theta):
        r = scale * math.cos(k * theta)
        return r * math.cos(theta), r * math.sin(theta)
    return f

def hypotrochoid(R, r, d, scale=1.0):
    def f(theta):
        x = (R - r) * math.cos(theta) + d * math.cos(((R - r) / r) * theta)
        y = (R - r) * math.sin(theta) - d * math.sin(((R - r) / r) * theta)
        return scale * x, scale * y
    return f

def draw_glow_curve(p, fn, t0, t1, steps, base_color, pensize=1, glow_levels=6):
    dark = rgb("#05060b")
    for i in range(glow_levels, 0, -1):
        a = i / glow_levels
        c = mix(dark, base_color, a)
        draw_parametric(p, fn, t0, t1, steps, c, pensize + i * 2)
    draw_parametric(p, fn, t0, t1, steps, base_color, pensize)

def draw_lotus_layer(p, petals, inner_r, outer_r, fill_color, edge_color, rotation=0):
    p.pensize(2)
    p.pencolor(edge_color)
    for i in range(petals):
        ang = rotation + 2 * math.pi * i / petals
        c = math.cos(ang)
        s = math.sin(ang)
        p.penup()
        p.goto(inner_r * c, inner_r * s)
        p.pendown()
        p.setheading(math.degrees(ang))
        p.fillcolor(fill_color)
        p.begin_fill()
        p.circle(outer_r, 58)
        p.left(122)
        p.circle(outer_r, 58)
        p.end_fill()

def draw_inner_filigree(p):
    gold = rgb("#d9c27c")
    teal = rgb("#7de7d9")
    rose = rgb("#ff8fb1")

    draw_polygon(p, 6, 52, rotation=math.pi / 6, color=gold, pensize=2)
    draw_polygon(p, 12, 92, rotation=math.pi / 12, color=teal, pensize=1)
    draw_starburst(p, 24, 18, 115, rotation=math.pi / 24, color=rose, pensize=1)

    draw_ring_dots(p, 48, 135, 4, [gold, teal, rose, rgb("#f6f1d1")], rotation=math.pi / 48)

    draw_glow_curve(
        p,
        rose_curve(5, 70),
        0,
        2 * math.pi,
        1200,
        rgb("#f7d86b"),
        pensize=2,
        glow_levels=4,
    )

def draw_orbit_arches(p):
    colors = [rgb("#73d7ff"), rgb("#86ffcf"), rgb("#ff9ad5")]
    for idx, r in enumerate([180, 235, 290, 345]):
        c = colors[idx % len(colors)]
        fn = hypotrochoid(R=r, r=r / 3.0, d=r / 1.6, scale=0.42)
        draw_glow_curve(p, fn, 0, 2 * math.pi * 6, 2200, c, pensize=1, glow_levels=3)

def draw_outer_mandala(p):
    layers = [
        (8, 145, 255, rgb("#1c6a78"), rgb("#79f3e4"), 0.0),
        (12, 220, 345, rgb("#143d68"), rgb("#83b7ff"), math.pi / 24),
        (16, 300, 430, rgb("#1f234f"), rgb("#b992ff"), math.pi / 32),
    ]
    for petals, inner_r, outer_r, fill, edge, rot in layers:
        draw_lotus_layer(p, petals, inner_r, outer_r, fill, edge, rot)

    draw_ring_dots(p, 96, 470, 3, [rgb("#f7f1da"), rgb("#a8f3ff"), rgb("#ffadc7")], rotation=math.pi / 96)
    draw_starburst(p, 96, 430, 510, rotation=math.pi / 96, color=rgb("#355d8f"), pensize=1)

def draw_background_sparks(p):
    for _ in range(240):
        ang = rng.random() * 2 * math.pi
        rad = rng.uniform(300, 560)
        x = rad * math.cos(ang)
        y = rad * math.sin(ang)
        size = rng.choice([1, 2, 2, 3, 4])
        col = rng.choice([rgb("#f7f1da"), rgb("#8ef6ff"), rgb("#ffb0d8"), rgb("#9a9fff")])
        p.penup()
        p.goto(x, y)
        p.dot(size, col)

def draw_center_flower(p):
    for petals, ir, or_, fill, edge, rot in [
        (5, 0, 55, rgb("#f0c15a"), rgb("#fff2bc"), math.pi / 10),
        (7, 28, 92, rgb("#f26c8a"), rgb("#ffd1db"), math.pi / 14),
        (9, 62, 128, rgb("#58d6c7"), rgb("#bafff6"), math.pi / 18),
    ]:
        draw_lotus_layer(p, petals, ir, or_, fill, edge, rot)

def draw_frost_filaments(p):
    colors = [rgb("#9be9ff"), rgb("#ffd6f1"), rgb("#d5ffb8")]
    for idx, scale in enumerate([0.55, 0.68, 0.81]):
        c = colors[idx]
        def filament(theta, k=idx):
            r = 320 * scale * (0.6 + 0.4 * math.cos(6 * theta + k))
            return r * math.cos(theta), r * math.sin(theta)
        draw_glow_curve(p, filament, 0, 2 * math.pi, 1600, c, pensize=1, glow_levels=2)

def draw_art():
    draw_background_sparks(pen)
    draw_outer_mandala(pen)
    draw_frost_filaments(pen)
    draw_orbit_arches(pen)
    draw_inner_filigree(pen)
    draw_center_flower(pen)

    pen.penup()
    pen.goto(0, -3)
    pen.dot(16, rgb("#fff6d6"))
    pen.goto(0, 0)
    pen.dot(8, rgb("#ffffff"))

draw_art()
screen.update()