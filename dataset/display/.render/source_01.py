"""Distressed physical thermal-receipt renderer."""

import hashlib
import html
import math
import random


def receipt_path(x: int, y: int, width: int, height: int, rng: random.Random) -> str:
    tooth = 18
    top = [(x, y)]
    for xx in range(x + tooth, x + width, tooth):
        depth = rng.randint(10, 18) if rng.random() < 0.12 else 6
        top.append((xx, y + (depth if (xx // tooth) % 2 else 0)))
    top.append((x + width, y))
    bottom = [(x + width, y + height)]
    for xx in range(x + width - tooth, x, -tooth):
        depth = rng.randint(10, 18) if rng.random() < 0.12 else 6
        bottom.append((xx, y + height - (depth if (xx // tooth) % 2 else 0)))
    bottom.append((x, y + height))
    points = top + [(x + width, y + height)] + bottom + [(x, y)]
    return "M " + " L ".join(f"{px},{py}" for px, py in points) + " Z"


def render(text: str, seed: str) -> str:
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16], 16))
    lines = text.splitlines()
    line_height = 26
    paper_width = 590
    paper_height = len(lines) * line_height + 92
    paper_x = (900 - paper_width) // 2
    paper_y = (1200 - paper_height) // 2
    paper = receipt_path(paper_x, paper_y, paper_width, paper_height, rng)
    angle = rng.uniform(-3.2, 3.2)
    palettes = [("#865f3e", "#3e291c"), ("#6d7368", "#30352f"), ("#7e6157", "#352520"), ("#6e6252", "#30291f")]
    base, dark = palettes[int(seed[-2:]) % len(palettes)]
    text_nodes = []
    for index, line in enumerate(lines):
        y = paper_y + 58 + index * line_height
        ink = "#9f2d24" if line.startswith("***") else "#282521"
        weight = "700" if line.startswith(("TOTAL", "***")) else "500"
        text_nodes.append(f'<text x="{paper_x + 39}" y="{y}" fill="{ink}" fill-opacity="{rng.uniform(.78, .98):.2f}" font-weight="{weight}">{html.escape(line)}</text>')
    crease_y = paper_y + rng.randint(150, max(151, paper_height - 130))
    stain_x = paper_x + rng.randint(55, paper_width - 55)
    stain_y = paper_y + rng.randint(60, paper_height - 60)
    stain_points = []
    for point in range(18):
        theta = point * 2 * math.pi / 18
        radius = rng.uniform(15, 38)
        stain_points.append(f"{stain_x + math.cos(theta) * radius:.1f},{stain_y + math.sin(theta) * radius * .62:.1f}")
    splotch = "M " + " L ".join(stain_points) + " Z"
    tape_x = paper_x + rng.randint(70, paper_width - 220)
    wood_grain = "".join(f'<path d="M 0,{yy} Q 230,{yy + rng.randint(-22, 22)} 450,{yy + rng.randint(-12, 12)} T 900,{yy + rng.randint(-18, 18)}"/>' for yy in range(45, 1200, 72))
    speckles = "".join(f'<circle cx="{rng.randint(paper_x + 16, paper_x + paper_width - 16)}" cy="{rng.randint(paper_y + 14, paper_y + paper_height - 14)}" r="{rng.uniform(.4, 2.1):.1f}" opacity="{rng.uniform(.08, .32):.2f}"/>' for _ in range(115))
    burn_lines = "".join(f'<rect x="{paper_x + rng.randint(18, paper_width - 24)}" y="{paper_y}" width="{rng.randint(1, 5)}" height="{paper_height}" fill="#332d25" opacity="{rng.uniform(.025, .07):.3f}"/>' for _ in range(7))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1200">
<defs><filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="16" dy="22" stdDeviation="18" flood-color="#140e09" flood-opacity=".55"/></filter><filter id="paper"><feTurbulence type="fractalNoise" baseFrequency=".035 .5" numOctaves="2" seed="{rng.randint(1, 99)}" result="noise"/><feColorMatrix in="noise" values="1 0 0 0 .85 0 1 0 0 .82 0 0 1 0 .72 0 0 0 .12 0"/><feBlend in="SourceGraphic" mode="multiply"/></filter><clipPath id="clip"><path d="{paper}"/></clipPath></defs>
<rect width="900" height="1200" fill="{base}"/><g fill="none" stroke="{dark}" stroke-width="3" opacity=".13">{wood_grain}</g>
<g transform="rotate({angle:.2f} 450 600)"><path d="{paper}" fill="#f1ebd5" filter="url(#shadow)"/><path d="{paper}" fill="#f8f2dc" filter="url(#paper)"/><path d="{splotch}" fill="#79502e" opacity=".10"/><path d="{splotch}" fill="none" stroke="#5e3c24" stroke-width="3" opacity=".08"/>
<path d="M{paper_x + 18},{crease_y - 4}Q450,{crease_y + rng.randint(-10, 8)} {paper_x + paper_width - 18},{crease_y + rng.randint(-4, 5)}" fill="none" stroke="#fff" stroke-width="3" opacity=".34"/><path d="M{paper_x + 25},{crease_y + 2}Q450,{crease_y + rng.randint(-7, 12)} {paper_x + paper_width - 24},{crease_y + rng.randint(0, 8)}" fill="none" stroke="#fff" stroke-width="2" opacity=".50"/><path d="M{paper_x + 40},{crease_y + 8}Q450,{crease_y + rng.randint(-4, 15)} {paper_x + paper_width - 42},{crease_y + rng.randint(4, 13)}" fill="none" stroke="#fff" opacity=".28"/>
<g font-family="DejaVu Sans Mono,monospace" font-size="16.8px" xml:space="preserve">{''.join(text_nodes)}</g><g clip-path="url(#clip)" fill="#282521">{burn_lines}{speckles}</g><g transform="rotate({rng.uniform(-4, 4):.2f} {tape_x + 70} {paper_y + 3})"><rect x="{tape_x}" y="{paper_y - 20}" width="150" height="47" rx="4" fill="#dfd3a7" opacity=".48"/><path d="M{tape_x + 6},{paper_y - 7}L{tape_x + 143},{paper_y + 13}" stroke="#fff9d9" stroke-width="3" opacity=".24"/></g></g>
<rect x="18" y="18" width="864" height="1164" rx="22" fill="none" stroke="#fff" stroke-opacity=".12" stroke-width="2"/></svg>'''
