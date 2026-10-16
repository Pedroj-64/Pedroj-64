"""Genera dark.svg y light.svg: neofetch animado. El retrato (puntos) se fractura en partículas
que viajan formando los logos del stack y vuelven al retrato. Uso: python3 gen.py <imagen>"""
import sys, html, random, os, io, subprocess
import numpy as np
from PIL import Image, ImageOps

W, H = 1180, 610
PX, PY, PW, PH = 30, 84, 420, 472  # panel del retrato
CELL = 4
N = 1100  # partículas
HERE = os.path.dirname(os.path.abspath(__file__))

# (nombre, nivel 1-3). Ajusta aquí: 3=diario, 2=cómodo, 1=aprendiendo/noob
LANGS = [("Java", 3), ("Python", 3), ("JavaScript", 3), ("Elixir", 2), ("Kotlin", 2), ("C#", 2),
         ("Dart", 2), ("Rust", 1), ("C", 1), ("C++", 1), ("TypeScript (noob)", 1), ("Shell", 2)]
FWS = [("Spring (noob)", 1), ("React", 2), ("Angular (noob)", 1), ("Flutter", 2),
       ("Jetpack Compose", 2), ("JavaFX", 3), ("QML/Quickshell", 1)]
INFO = [("OS", "Linux · CachyOS"), ("Shell", "fish"), ("Theme", "Tokyo Night"),
        ("Role", "Software Eng. @ UQ · Jr Cybersecurity"), ("Focus", "Arquitectura · Wayland · sistemas"),
        ("Where", "Armenia, Quindío, CO")]
TOOLS = "Git · Gradle · IntelliJ · VS Code · Linux"
# logos que forman las partículas: (archivo en logos/, etiqueta, índice de color en t["sw"])
LOGOS = [("rust", "Rust", 1), ("cplusplus", "C++", 6), ("python", "Python", 2), ("openjdk", "Java", 0),
         ("kotlin", "Kotlin", 7), ("typescript", "TypeScript", 5), ("angular", "Angular", 0), ("flutter", "Flutter", 4)]

THEMES = {
    "dark": dict(bg="#1a1b26", bar="#16161e", panel="#1f2335", fg="#c0caf5", dim="#565f89", key="#7aa2f7",
                 grad=["#7dcfff", "#7aa2f7", "#bb9af7", "#f7768e"], pip_off="#292e42",
                 sw=["#f7768e", "#ff9e64", "#e0af68", "#9ece6a", "#73daca", "#7dcfff", "#7aa2f7", "#bb9af7"]),
    "light": dict(bg="#e1e2e7", bar="#d0d5e3", panel="#e9e9ed", fg="#3760bf", dim="#848cb5", key="#2e7de9",
                  grad=["#007197", "#2e7de9", "#9854f1", "#f52a65"], pip_off="#c4c8da",
                  sw=["#f52a65", "#b15c00", "#8c6c3e", "#587539", "#118c74", "#007197", "#2e7de9", "#9854f1"]),
}

# --- línea de tiempo (segundos) ---
MOVE, HOLD = 0.9, 1.8          # viaje de partículas y pausa en cada logo
T_REVEAL, T_FRACT, T_PART = 3.3, 3.4, 4.0
S0 = 4.6                       # primer viaje hacia un logo
STEP = MOVE + HOLD
T_BACK = S0 + STEP * len(LOGOS)  # empiezan a volver al retrato
T_DONE = T_BACK + MOVE
D = round(T_DONE + 2.0, 1)     # ciclo total (se repite siempre)
EASE, FLAT = ".45 0 .25 1", "0 0 1 1"


def kt(*sec):
    return ";".join(f"{x/D:.4f}" for x in sec)


def dots(path):
    im = Image.open(path).convert("L")
    im.paste(int(np.median(np.asarray(im)[:60, :60])), (620, 10, 730, 115))  # quita el botón '...' de WhatsApp
    im = ImageOps.autocontrast(im, cutoff=2)
    w, h = im.size
    ch = int(w * PH / PW)  # recorte superior con la proporción del panel
    im = im.crop((0, 0, w, min(ch, h))).resize((PW // CELL, PH // CELL), Image.LANCZOS)
    ink = 1 - np.asarray(im) / 255.0
    out = []
    for r, row in enumerate(ink):
        for c, v in enumerate(row):
            if v > 0.38:
                out.append((c * CELL + CELL / 2, r * CELL + CELL / 2, round(0.3 + 1.7 * v ** 1.5, 2)))
    return out


def logo_points(slug, rnd):
    """N puntos en retícula dentro de la silueta del logo (coordenadas del panel)."""
    svg = open(f"{HERE}/logos/{slug}.svg").read()
    png = subprocess.run(["rsvg-convert", "-w", "300", "-h", "300"], input=svg.encode(), capture_output=True, check=True).stdout
    a = np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"))[:, :, 3] > 100
    pitch, best = 3.0, None
    while pitch < 14:  # retícula más gruesa que aún da >= N puntos
        pts = [(x, y) for y in np.arange(pitch / 2, 300, pitch) for x in np.arange(pitch / 2, 300, pitch) if a[int(y), int(x)]]
        if len(pts) < N:
            break
        best, pitch = pts, pitch + 0.25
    rnd.shuffle(best)
    return [(x + (PW - 300) / 2, y + (PH - 300) / 2) for x, y in best[:N]]


def by_row(pts):
    """Orden por (fila, x): emparejar por rango da viajes fluidos y sin cruces largos."""
    return sorted(pts, key=lambda p: (round(p[1] / 14), p[0]))


def disc(intervals):
    """opacity discreta: 1 dentro de cualquiera de los intervalos (s, e)."""
    edges = sorted({0, D} | {x for iv in intervals for x in iv})
    vals = ["1" if any(s <= t < e for s, e in intervals) else "0" for t in edges[:-1]]
    return (f'<animate attributeName="opacity" calcMode="discrete" values="{";".join(vals)}" '
            f'keyTimes="{kt(*edges[:-1])}" dur="{D}s" repeatCount="indefinite"/>')


def build(name, t, pts):
    e = html.escape
    g = t["grad"]
    rnd = random.Random(7)
    # --- partículas: posición de cada una en el retrato y en cada logo ---
    base = [(x, y) for x, y, _ in pts]
    rnd.shuffle(base)
    home = by_row((base * (N // len(base) + 1))[:N])
    stages = [by_row(logo_points(slug, random.Random(slug))) for slug, _, _ in LOGOS]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="ui-monospace,SFMono-Regular,\'SF Mono\',Menlo,Consolas,\'Liberation Mono\',\'DejaVu Sans Mono\',monospace" '
         f'role="img" aria-label="pedro@Pedroj-64 — neofetch">',
         '<title>pedro@Pedroj-64 · Developer · Jr Cybersecurity Analyst</title><defs>',
         f'<linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{g[1]}"/><stop offset=".5" stop-color="{g[2]}"/><stop offset="1" stop-color="{g[0]}"/>'
         '<animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" dur="10s" repeatCount="indefinite"/></linearGradient>',
         f'<linearGradient id="pg" gradientUnits="userSpaceOnUse" x1="0" y1="{PY}" x2="0" y2="{PY+PH}">'
         + "".join(f'<stop offset="{i/3:.2f}" stop-color="{c}"/>' for i, c in enumerate(g)) + '</linearGradient>',
         '<filter id="gl" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="7"/></filter>',
         f'<clipPath id="win"><rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18"/></clipPath>',
         f'<clipPath id="pc"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="10"/></clipPath>',
         f'<mask id="rv"><rect x="{PX}" y="{PY}" width="{PW}" height="0" fill="#fff">'
         f'<animate attributeName="height" values="0;0;{PH};{PH};0" keyTimes="{kt(0, .3, T_REVEAL, D - .6, D)}" dur="{D}s" repeatCount="indefinite"/></rect></mask>']
    # cuadrado compartido por todas las partículas: pulsa mientras viajan; su color es currentColor
    tk, size = [0], [3.4]
    for a in [S0 + k * STEP for k in range(len(LOGOS))] + [T_BACK]:
        tk += [a, a + MOVE / 2, a + MOVE]
        size += [3.4, 5.6, 3.4]
    tk.append(D)
    size.append(3.4)

    def anim(attr, f):
        return (f'<animate attributeName="{attr}" values="{";".join(f"{f(v):.2f}" for v in size)}" keyTimes="{kt(*tk)}" '
                f'dur="{D}s" repeatCount="indefinite"/>')
    s.append(f'<rect id="pt" x="-1.7" y="-1.7" width="3.4" height="3.4" rx=".6" fill="currentColor">'
             f'{anim("width", lambda v: v)}{anim("height", lambda v: v)}{anim("x", lambda v: -v / 2)}{anim("y", lambda v: -v / 2)}</rect>')
    s.append('</defs>')
    s.append(f'<g clip-path="url(#win)"><rect width="{W}" height="{H}" fill="{t["bg"]}"/>'
             f'<rect width="{W}" height="46" fill="{t["bar"]}"/></g>')
    s.append(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18" fill="none" stroke="url(#bd)" stroke-width="2.5"/>')
    for i, c in enumerate([g[3], g[1], g[2]]):
        s.append(f'<circle cx="{26+i*20}" cy="24" r="6" fill="{c}"/>')
    s.append(f'<text x="{W/2}" y="29" text-anchor="middle" font-size="13" fill="{t["key"]}">pedro@Pedroj-64: ~ — neofetch</text>')
    s.append(f'<text x="32" y="68" font-size="10" letter-spacing="3" fill="{t["dim"]}">VISUAL.MAP</text>'
             f'<text x="490" y="68" font-size="10" letter-spacing="3" fill="{t["dim"]}">SYSTEM.INFO</text>')
    s.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="10" fill="{t["panel"]}" stroke="{t["dim"]}" stroke-opacity=".4"/>')

    # --- retrato: se construye, tiembla, parpadea y desaparece en partículas ---
    cx, cy = PX + PW / 2, PY + PH / 2
    s.append('<g clip-path="url(#pc)">')
    s.append(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;-4 2;4 -3;-3 -1;2 3;0 0;0 0" '
             f'keyTimes="{kt(0, T_FRACT, T_FRACT+.05, T_FRACT+.1, T_FRACT+.15, T_FRACT+.2, T_FRACT+.3, D)}" dur="{D}s" repeatCount="indefinite"/>')
    s.append(f'<g mask="url(#rv)"><g><animate attributeName="opacity" values="1;1;.35;1;.3;0;0;1;1" '
             f'keyTimes="{kt(0, T_FRACT, T_FRACT+.15, T_FRACT+.3, T_FRACT+.45, T_PART, T_DONE, T_DONE+.3, D)}" dur="{D}s" repeatCount="indefinite"/>')
    s.append('<g fill="url(#pg)"><animate attributeName="opacity" values="1;.8;1" dur="3s" repeatCount="indefinite"/>')
    s.append("".join(f'<circle cx="{x+PX:g}" cy="{y+PY:g}" r="{r}"/>' for x, y, r in pts))
    s.append('</g><g fill="#fff">')  # destellos
    for x, y, r in rnd.sample(pts, 70):
        s.append(f'<circle cx="{x+PX:g}" cy="{y+PY:g}" r="{r*1.5:.2f}" opacity="0"><animate attributeName="opacity" values="0;1;0" '
                 f'dur="{rnd.uniform(1.2,3.5):.1f}s" begin="{rnd.uniform(0,6):.1f}s" repeatCount="indefinite"/></circle>')
    s.append('</g></g></g></g></g>')
    # barrido de luz mientras se construye
    s.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="2" fill="{g[0]}" opacity="0">'
             f'<animate attributeName="y" values="{PY};{PY};{PY+PH};{PY+PH}" keyTimes="{kt(0, .3, T_REVEAL, D)}" dur="{D}s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;0;.9;0;0" keyTimes="{kt(0, .3, .5, T_REVEAL, D)}" dur="{D}s" repeatCount="indefinite"/></rect>')
    # anillo punteado + destello al fracturarse
    s.append(f'<circle cx="{cx}" cy="{cy}" r="0" fill="none" stroke="{g[2]}" stroke-width="3" stroke-dasharray="2 5" opacity="0">'
             f'<animate attributeName="r" values="0;0;330;330" keyTimes="{kt(0, T_FRACT, T_FRACT+1.6, D)}" dur="{D}s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;0;.9;0;0" keyTimes="{kt(0, T_FRACT, T_FRACT+.02, T_FRACT+1.6, D)}" dur="{D}s" repeatCount="indefinite"/></circle>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="40" fill="{g[2]}" filter="url(#gl)" opacity="0">'
             f'<animate attributeName="opacity" values="0;0;.6;0;0" keyTimes="{kt(0, T_FRACT, T_FRACT+.05, T_FRACT+.4, D)}" dur="{D}s" repeatCount="indefinite"/></circle>')

    # --- partículas: cada una con su ruta y un pequeño retraso propio ---
    cs = [(0, g[2]), (S0, g[2])]
    for k, (_, _, ci) in enumerate(LOGOS):
        cs += [(S0 + k * STEP + MOVE, t["sw"][ci]), (S0 + (k + 1) * STEP if k < len(LOGOS) - 1 else T_BACK, t["sw"][ci])]
    cs += [(T_DONE, g[2]), (D, g[2])]
    color_anim = (f'<animate attributeName="color" values="{";".join(c for _, c in cs)}" keyTimes="{kt(*[x for x, _ in cs])}" '
                  f'dur="{D}s" repeatCount="indefinite"/>')
    for gi, op in enumerate((1, .6)):
        s.append(f'<g opacity="0" color="{g[2]}" clip-path="url(#pc)"><animate attributeName="opacity" values="0;0;{op};{op};0;0" '
                 f'keyTimes="{kt(0, T_PART, T_PART+.3, T_DONE, T_DONE+.3, D)}" dur="{D}s" repeatCount="indefinite"/>{color_anim}')
        for i in range(gi, N, 2):
            dl = rnd.uniform(0, .35)
            cur = home[i]
            times, vals, spl = [0, S0 + dl], [cur, cur], [FLAT]
            for k, st in enumerate(stages):
                a = S0 + k * STEP + dl
                if k:  # sale del logo anterior
                    times.append(a); vals.append(cur); spl.append(FLAT)
                cur = st[i]
                times.append(a + MOVE); vals.append(cur); spl.append(EASE)
            times += [T_BACK + dl, T_DONE + dl, D]
            vals += [cur, home[i], home[i]]
            spl += [FLAT, EASE, FLAT]
            s.append(f'<use href="#pt"><animateTransform attributeName="transform" type="translate" '
                     f'values="{";".join(f"{x+PX:.0f} {y+PY:.0f}" for x, y in vals)}" keyTimes="{kt(*times)}" '
                     f'calcMode="spline" keySplines="{";".join(spl)}" dur="{D}s" repeatCount="indefinite"/></use>')
        s.append('</g>')
    for ox, oy, dx, dy in [(PX, PY, 1, 1), (PX+PW, PY, -1, 1), (PX, PY+PH, 1, -1), (PX+PW, PY+PH, -1, -1)]:
        s.append(f'<path d="M{ox+dx*14} {oy} H{ox} V{oy+dy*14}" fill="none" stroke="{g[2]}" stroke-width="2"/>')

    # --- status que sigue la coreografía ---
    s.append(f'<text x="32" y="582" font-size="12" fill="{t["dim"]}">status:</text>')
    states = [("stable", [(0, T_FRACT), (T_DONE, D)], g[1]), ("fractured", [(T_FRACT, T_PART)], g[3]),
              ("dissolving → particles", [(T_PART, S0)], g[2])]
    states += [(f"assembling → {lb}", [(S0 + k * STEP, S0 + (k + 1) * STEP)], t["sw"][ci]) for k, (_, lb, ci) in enumerate(LOGOS)]
    states.append(("reforming → portrait", [(T_BACK, T_DONE)], g[0]))
    for txt, iv, col in states:
        s.append(f'<text x="86" y="582" font-size="12" fill="{col}" opacity="0">{e(txt)}{disc(iv)}</text>')

    # --- panel de info, aparece línea a línea ---
    n = [0]

    def line(inner):
        n[0] += 1
        b = 0.6 + n[0] * 0.12
        return (f'<g opacity="0">{inner}<animate attributeName="opacity" values="0;0;1;1;0;0" '
                f'keyTimes="{kt(0, b, b + .35, D - 1.2, D - .6, D)}" dur="{D}s" repeatCount="indefinite"/></g>')

    s.append(line(f'<text x="490" y="102" font-size="20" font-weight="700" fill="url(#pg)">pedro<tspan fill="{t["dim"]}">@</tspan>Pedroj-64</text>'
                  f'<rect x="490" y="110" width="300" height="2" fill="{g[2]}" opacity=".6"/>'))
    for i, (k, v) in enumerate(INFO):
        y = 138 + i * 20
        s.append(line(f'<text x="490" y="{y}" font-size="14" fill="{t["key"]}" font-weight="700">{k}</text>'
                      f'<text x="560" y="{y}" font-size="14" fill="{t["fg"]}">{e(v)}</text>'))

    def block(label, y0, items, cols=3):
        s.append(line(f'<text x="490" y="{y0}" font-size="11" letter-spacing="3" fill="{g[2]}">{label}</text>'))
        for i, (nm, lv) in enumerate(items):
            x = 490 + (i % cols) * 215
            y = y0 + 24 + (i // cols) * 26
            base_, _, tag = nm.partition(" (")
            txt = f'{e(base_)}' + (f'<tspan fill="{t["dim"]}" xml:space="preserve"> ({e(tag)}</tspan>' if tag else "")
            pips = "".join(f'<rect x="{x+158+j*11}" y="{y-9}" width="8" height="10" rx="2" fill="{g[j] if j < lv else t["pip_off"]}"/>' for j in range(3))
            s.append(line(f'<text x="{x}" y="{y}" font-size="14" fill="{t["fg"]}">{txt}</text>{pips}'))
        return y0 + 24 + ((len(items) - 1) // cols) * 26

    y = block("LANGUAGES", 268, LANGS)
    y = block("FRAMEWORKS", y + 34, FWS)
    s.append(line(f'<text x="490" y="{y+34}" font-size="11" letter-spacing="3" fill="{g[2]}">TOOLS</text>'
                  f'<text x="490" y="{y+54}" font-size="14" fill="{t["fg"]}">{e(TOOLS)}</text>'))
    s.append(line("".join(f'<rect x="{490+i*26}" y="{y+68}" width="22" height="12" rx="3" fill="{c}"/>' for i, c in enumerate(t["sw"]))))
    s.append(f'<rect x="{490+8*26+6}" y="{y+66}" width="9" height="16" fill="{g[0]}" opacity="0"><animate attributeName="opacity" calcMode="discrete" values="1;0" dur="1s" repeatCount="indefinite"/></rect>')
    s.append(f'<text x="1150" y="582" text-anchor="end" font-size="11" fill="{t["dim"]}">3 pips = daily · 2 = comfortable · 1 = learning</text>')
    s.append('</svg>')
    open(f"{HERE}/{name}.svg", "w").write("\n".join(s))


if __name__ == "__main__":
    pts = dots(sys.argv[1])
    for k, t in THEMES.items():
        build(k, t, pts)
        print(k, len(pts), "dots", os.path.getsize(f"{HERE}/{k}.svg") // 1024, "KB, ciclo", D, "s")
