"""Genera dark.svg y light.svg (neofetch animado, retrato de puntos). Uso: python3 gen.py <imagen>"""
import sys, html
import numpy as np
from PIL import Image, ImageOps

W, H = 1180, 610
PX, PY, PW, PH = 30, 84, 420, 472  # panel del retrato
CELL = 4

# (nombre, nivel 1-3). Ajusta aquí: 3=diario, 2=cómodo, 1=aprendiendo/noob
LANGS = [("Java", 3), ("Python", 3), ("JavaScript", 3), ("Elixir", 2), ("Kotlin", 2), ("C#", 2),
         ("Dart", 2), ("Rust", 1), ("C", 1), ("C++", 1), ("TypeScript (noob)", 1), ("Shell", 2)]
FWS = [("Spring (noob)", 1), ("React", 2), ("Angular (noob)", 1), ("Flutter", 2),
       ("Jetpack Compose", 2), ("JavaFX", 3), ("QML/Quickshell", 1)]
INFO = [("OS", "Linux · CachyOS"), ("Shell", "fish"), ("Theme", "Tokyo Night"),
        ("Role", "Software Eng. @ UQ · Jr Cybersecurity"), ("Focus", "Arquitectura · Wayland · sistemas"),
        ("Where", "Armenia, Quindío, CO")]
TOOLS = "Git · Gradle · IntelliJ · VS Code · Linux"

THEMES = {
    "dark": dict(bg="#1a1b26", bar="#16161e", panel="#1f2335", fg="#c0caf5", dim="#565f89", key="#7aa2f7",
                 grad=["#7dcfff", "#7aa2f7", "#bb9af7", "#f7768e"], pip_off="#292e42",
                 sw=["#f7768e", "#ff9e64", "#e0af68", "#9ece6a", "#73daca", "#7dcfff", "#7aa2f7", "#bb9af7"]),
    "light": dict(bg="#e1e2e7", bar="#d0d5e3", panel="#e9e9ed", fg="#3760bf", dim="#848cb5", key="#2e7de9",
                  grad=["#007197", "#2e7de9", "#9854f1", "#f52a65"], pip_off="#c4c8da",
                  sw=["#f52a65", "#b15c00", "#8c6c3e", "#587539", "#118c74", "#007197", "#2e7de9", "#9854f1"]),
}


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


def build(name, t, pts):
    e = html.escape
    g = t["grad"]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="ui-monospace,SFMono-Regular,\'SF Mono\',Menlo,Consolas,\'Liberation Mono\',\'DejaVu Sans Mono\',monospace" '
         f'role="img" aria-label="pedro@Pedroj-64 — neofetch">',
         '<title>pedro@Pedroj-64 · Developer · Jr Cybersecurity Analyst</title><defs>',
         f'<linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{g[1]}"/><stop offset=".5" stop-color="{g[2]}"/><stop offset="1" stop-color="{g[0]}"/>'
         '<animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" dur="10s" repeatCount="indefinite"/></linearGradient>',
         f'<linearGradient id="pg" gradientUnits="userSpaceOnUse" x1="0" y1="{PY}" x2="0" y2="{PY+PH}">'
         + "".join(f'<stop offset="{i/3:.2f}" stop-color="{c}"/>' for i, c in enumerate(g)) + '</linearGradient>',
         f'<clipPath id="win"><rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18"/></clipPath>',
         f'<clipPath id="pc"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="10"/></clipPath>',
         f'<mask id="rv"><rect x="{PX}" y="{PY}" width="{PW}" height="0" fill="#fff">'
         f'<animate attributeName="height" from="0" to="{PH}" begin="0.3s" dur="3.5s" fill="freeze"/></rect></mask>',
         '</defs>',
         f'<g clip-path="url(#win)"><rect width="{W}" height="{H}" fill="{t["bg"]}"/>',
         f'<rect width="{W}" height="46" fill="{t["bar"]}"/></g>',
         f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18" fill="none" stroke="url(#bd)" stroke-width="2.5"/>']
    for i, c in enumerate([g[3], g[1], g[2]]):
        s.append(f'<circle cx="{26+i*20}" cy="24" r="6" fill="{c}"/>')
    s.append(f'<text x="{W/2}" y="29" text-anchor="middle" font-size="13" fill="{t["key"]}">pedro@Pedroj-64: ~ — neofetch</text>')
    s.append(f'<text x="32" y="68" font-size="10" letter-spacing="3" fill="{t["dim"]}">VISUAL.MAP</text>'
             f'<text x="490" y="68" font-size="10" letter-spacing="3" fill="{t["dim"]}">SYSTEM.INFO</text>')
    s.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="10" fill="{t["panel"]}" stroke="{t["dim"]}" stroke-opacity=".4"/>')
    # retrato
    s.append('<g clip-path="url(#pc)"><g mask="url(#rv)" fill="url(#pg)">')
    s.append("".join(f'<circle cx="{x+PX:g}" cy="{y+PY:g}" r="{r}"/>' for x, y, r in pts))
    s.append('</g>')
    s.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="2" fill="{g[0]}" opacity="0">'
             f'<animate attributeName="y" from="{PY}" to="{PY+PH}" begin="0.3s" dur="3.5s" fill="freeze"/>'
             '<animate attributeName="opacity" values="0;.9;.9;0" keyTimes="0;.05;.95;1" begin="0.3s" dur="3.5s" fill="freeze"/></rect></g>')
    for cx, cy, dx, dy in [(PX, PY, 1, 1), (PX+PW, PY, -1, 1), (PX, PY+PH, 1, -1), (PX+PW, PY+PH, -1, -1)]:
        s.append(f'<path d="M{cx+dx*14} {cy} H{cx} V{cy+dy*14}" fill="none" stroke="{g[2]}" stroke-width="2"/>')
    s.append(f'<text x="32" y="582" font-size="12" fill="{t["dim"]}">status: <tspan fill="{t["key"]}">online</tspan></text>')

    # panel de info, aparece línea a línea
    n = [0]

    def line(inner):
        n[0] += 1
        return (f'<g opacity="0">{inner}<animate attributeName="opacity" from="0" to="1" '
                f'begin="{0.6+n[0]*0.12:.2f}s" dur=".35s" fill="freeze"/></g>')

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
            base, _, tag = nm.partition(" (")
            txt = f'{e(base)}' + (f'<tspan fill="{t["dim"]}" xml:space="preserve"> ({e(tag)}</tspan>' if tag else "")
            pips = "".join(f'<rect x="{x+158+j*11}" y="{y-9}" width="8" height="10" rx="2" fill="{g[j] if j < lv else t["pip_off"]}"/>' for j in range(3))
            s.append(line(f'<text x="{x}" y="{y}" font-size="14" fill="{t["fg"]}">{txt}</text>{pips}'))
        return y0 + 24 + ((len(items) - 1) // cols) * 26

    y = block("LANGUAGES", 268, LANGS)
    y = block("FRAMEWORKS", y + 34, FWS)
    s.append(line(f'<text x="490" y="{y+34}" font-size="11" letter-spacing="3" fill="{g[2]}">TOOLS</text>'
                  f'<text x="490" y="{y+54}" font-size="14" fill="{t["fg"]}">{e(TOOLS)}</text>'))
    s.append(line("".join(f'<rect x="{490+i*26}" y="{y+68}" width="22" height="12" rx="3" fill="{c}"/>' for i, c in enumerate(t["sw"]))))
    s.append(f'<text x="1150" y="582" text-anchor="end" font-size="12" fill="{t["dim"]}">● daily  ◐ comfortable  ○ learning</text>'
             if False else
             f'<text x="1150" y="582" text-anchor="end" font-size="11" fill="{t["dim"]}">3 pips = daily · 2 = comfortable · 1 = learning</text>')
    s.append('</svg>')
    open(f"{name}.svg", "w").write("\n".join(s))
    return y + 80


if __name__ == "__main__":
    pts = dots(sys.argv[1])
    for k, t in THEMES.items():
        print(k, len(pts), "dots, last y", build(k, t, pts))
