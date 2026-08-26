"""Drab scanned supplier-document renderer."""

import html
import re

RULE = "-" * 36
AMOUNT = re.compile(r"^(.*?)\s{2,}(-?[\d,]+\.\d{2})$")
LEFT = 145
RIGHT = 755
TITLE = 205
FIELD_TOP = 242
FIELD_STEP = 25
STEP = 30
FLOOR = 1040


def _split(text: str) -> tuple[str, list[str], list[str]]:
    """Split a document into its title, header fields, and table body."""
    lines = [line.rstrip() for line in text.splitlines()[1:]]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    if not lines:
        raise ValueError("Document is empty")
    if RULE not in lines:
        raise ValueError(f"Document has no ruled table: {lines[0]!r}")
    split = lines.index(RULE)
    return lines[0], lines[1:split], lines[split:]


def _row(line: str, y: int, ruled: int) -> str:
    """Draw one body line as a rule, an amount row, or a closing note."""
    if line == RULE:
        return f'<line x1="{LEFT}" y1="{y - 9}" x2="{RIGHT}" y2="{y - 9}" stroke="#c4c4c4"/>'
    match = AMOUNT.match(line)
    if match is None:
        return f'<text x="{LEFT}" y="{y}" class="note">{html.escape(line)}</text>'
    label, amount = match.groups()
    css = "total" if ruled >= 2 else "item"
    row = (
        f'<text x="{LEFT}" y="{y}" class="{css}">{html.escape(label)}</text>'
        f'<text x="{RIGHT}" y="{y}" text-anchor="end" class="{css}">'
        f"{html.escape(amount)}</text>"
    )
    return row


def render(text: str, _seed: str) -> str:
    title, fields, body = _split(text)
    field_nodes = "".join(
        f'<text x="{LEFT}" y="{FIELD_TOP + i * FIELD_STEP}" class="field">'
        f"{html.escape(line)}</text>"
        for i, line in enumerate(fields)
    )
    body_top = FIELD_TOP + max(len(fields) - 1, 0) * FIELD_STEP + 40
    nodes = []
    y = body_top
    ruled = 0
    noted = False
    for line in body:
        if line == RULE:
            ruled += 1
        elif AMOUNT.match(line) is None and not noted:
            noted = True
            y += 14
        nodes.append(_row(line, y, ruled))
        y += STEP - 6 if line == RULE else STEP
    if y > FLOOR:
        raise ValueError(f"Document is {y - FLOOR}px too tall for the page")
    style = (
        ".ui{font-family:DejaVu Sans,sans-serif;fill:#e5e5e5}"
        ".field{font-family:DejaVu Sans,sans-serif;font-size:13px;fill:#4d4d4d}"
        ".item{font-family:DejaVu Sans Mono,monospace;font-size:15px;fill:#242424}"
        ".total{font-family:DejaVu Sans Mono,monospace;font-size:15px;"
        "font-weight:bold;fill:#111}"
        ".note{font-family:DejaVu Sans,sans-serif;font-size:13px;fill:#5a5a5a}"
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1200">
<defs><filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dy="5" stdDeviation="8" flood-color="#555" flood-opacity=".35"/></filter>
<style>{style}</style></defs>
<rect width="900" height="1200" fill="#c9c9c9"/><rect width="900" height="72" fill="#4b4b4b"/>
<circle cx="30" cy="36" r="6" fill="#8e8e8e"/><circle cx="52" cy="36" r="6" fill="#8e8e8e"/><circle cx="74" cy="36" r="6" fill="#8e8e8e"/>
<text x="112" y="42" class="ui" font-size="16">Supplier document.pdf</text><rect x="397" y="20" width="106" height="34" rx="3" fill="#3b3b3b"/><text x="425" y="42" class="ui" font-size="13">1 / 1</text>
<path d="M810 27v20m-10-10h20M842 27v20m-10-10h20" stroke="#d2d2d2" stroke-width="2" opacity=".8"/>
<rect x="95" y="102" width="710" height="1010" fill="#fff" filter="url(#shadow)"/>
<text x="{LEFT}" y="154" font-family="DejaVu Sans" font-size="10" letter-spacing="2" fill="#888">SCANNED DOCUMENT</text>
<text x="{LEFT}" y="{TITLE}" font-family="DejaVu Sans" font-size="19" font-weight="700" fill="#222">{html.escape(title)}</text>{field_nodes}
{"".join(nodes)}
<line x1="{LEFT}" y1="1064" x2="{RIGHT}" y2="1064" stroke="#ddd"/><text x="{LEFT}" y="1087" font-family="DejaVu Sans" font-size="9" fill="#999">Scanned by Harbour Digital</text><text x="744" y="1087" text-anchor="end" font-family="DejaVu Sans" font-size="9" fill="#999">1</text>
</svg>"""
