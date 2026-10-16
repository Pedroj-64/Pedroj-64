"""Genera headers estilo prompt y tarjetas de proyecto en dark/light, mismo estilo que el neofetch. Uso: python3 sections.py"""
import html, os
from gen import THEMES, D as _D

OUT = os.path.join(os.path.dirname(__file__), "..")
FONT = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
HEADERS = [("about", "~/about $ cat README.md"), ("proyectos", "~/proyectos $ ls -la"), ("actividad", "~/actividad $ git log --graph")]
# nombre, repo, descripción (2 líneas), stack
CARDS = [
    ("inklus", "inklus", ["Handwriting & note-taking for stylus tablets.", "Pressure ink, PDF annotation, offline-first."], ["Flutter", "Dart", "Android", "Linux"]),
    ("gradify", "Gradify_App", ["Android academic manager: weighted GPA,", "'what grade do I need?', widgets, AI tips."], ["Kotlin", "Compose"]),
    ("feelingmark", "feelingmark", ["Self-hosted photo calendar & memory album.", "Bring your own storage: disk, S3/R2, Drive."], ["TypeScript", "Mobile", "Web"]),
    ("npu-lab", "npu-lab", ["AMD XDNA1 NPU experiments on Linux:", "mlir-aie matmul kernels, XRT, MiniLM."], ["Python", "MLIR", "XRT"]),
    ("downhill-port", "DownHill-Port-PC", ["Native PC port of Downhill Domination (PS2)", "for Linux/Windows. Engine reimplementation."], ["Python", "Reverse eng."]),
    ("desklets", "Desklets-LinuxMint-Cinnamon", ["Cinnamon desklets: audio visualizer, player,", "system monitor, clock & weather. Tokyo Night."], ["JavaScript", "Cinnamon"]),
]
e = html.escape


def head(w, h, t, label):
    g = t["grad"]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}" role="img" aria-label="{e(label)}">'
            f'<defs><linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{g[1]}"/><stop offset=".5" stop-color="{g[2]}"/><stop offset="1" stop-color="{g[0]}"/>'
            '<animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" dur="10s" repeatCount="indefinite"/></linearGradient>'
            f'<clipPath id="c"><rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="{12 if h > 60 else 10}"/></clipPath></defs>')


def header(slug, text, name, t):
    w, h, g = 1180, 52, t["grad"]
    n = len(text) * 10.6 + 8
    s = [head(w, h, t, text), f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{t["bg"]}"/><rect width="{w}" height="{h}" fill="{t["bar"]}" opacity=".5"/></g>',
         f'<rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="10" fill="none" stroke="url(#bd)" stroke-width="2"/>']
    for i, c in enumerate([g[3], g[1], g[2]]):
        s.append(f'<circle cx="{26+i*20}" cy="{h/2}" r="6" fill="{c}"/>')
    prompt, _, cmd = text.partition(" $ ")
    # escribe el comando en bucle; el cursor sigue al texto
    s.append(f'<clipPath id="t"><rect x="100" y="0" width="0" height="{h}"><animate attributeName="width" values="0;0;{n:.0f};{n:.0f};0" keyTimes="0;.05;.35;.9;1" dur="8s" repeatCount="indefinite"/></rect></clipPath>')
    s.append(f'<text x="100" y="{h/2+6}" font-size="17" fill="{t["key"]}" font-weight="700" clip-path="url(#t)" xml:space="preserve">'
             f'{e(prompt)} <tspan fill="{g[2]}">$</tspan> <tspan fill="{t["fg"]}">{e(cmd)}</tspan></text>')
    s.append(f'<rect x="100" y="{h/2-9}" width="9" height="18" fill="{g[0]}"><animate attributeName="x" values="100;100;{100+n:.0f};{100+n:.0f};100" keyTimes="0;.05;.35;.9;1" dur="8s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" calcMode="discrete" values="1;0" dur="1s" repeatCount="indefinite"/></rect>')
    s.append('</svg>')
    open(f"{OUT}/headers/{slug}-{name}.svg", "w").write("".join(s))


def card(slug, repo, desc, stack, name, t):
    w, h, g = 580, 176, t["grad"]
    s = [head(w, h, t, repo), f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{t["bg"]}"/><rect width="{w}" height="34" fill="{t["bar"]}"/></g>',
         f'<rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="12" fill="none" stroke="url(#bd)" stroke-width="2"/>']
    for i, c in enumerate([g[3], g[1], g[2]]):
        s.append(f'<circle cx="{22+i*17}" cy="17" r="5" fill="{c}"/>')
    s.append(f'<text x="{w/2}" y="21" text-anchor="middle" font-size="12" fill="{t["dim"]}">~/proyectos/{e(repo[:34])}</text>')
    s.append(f'<text x="24" y="70" font-size="21" font-weight="700" fill="{g[1]}">{e(slug)}'
             f'<animate attributeName="fill" values="{g[0]};{g[1]};{g[2]};{g[1]};{g[0]}" dur="6s" repeatCount="indefinite"/></text>')
    for i, ln in enumerate(desc):
        s.append(f'<text x="24" y="{98+i*20}" font-size="13.5" fill="{t["fg"]}">{e(ln)}</text>')
    x = 24
    for i, c in enumerate(stack):
        pw = len(c) * 8.2 + 20
        s.append(f'<rect x="{x}" y="132" width="{pw:.0f}" height="24" rx="6" fill="{t["panel"]}" stroke="{g[i % 4]}" stroke-opacity=".7"/>'
                 f'<text x="{x+pw/2:.0f}" y="148" text-anchor="middle" font-size="12" fill="{g[i % 4]}">{e(c)}</text>')
        x += pw + 8
    s.append('</svg>')
    open(f"{OUT}/cards/{slug}-{name}.svg", "w").write("".join(s))


if __name__ == "__main__":
    os.makedirs(f"{OUT}/headers", exist_ok=True)
    os.makedirs(f"{OUT}/cards", exist_ok=True)
    for name, t in THEMES.items():
        for slug, text in HEADERS:
            header(slug, text, name, t)
        for slug, repo, desc, stack in CARDS:
            card(slug, repo, desc, stack, name, t)
