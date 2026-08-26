"""Drab email-client PDF printout renderer."""

import html


def render(text: str, _seed: str) -> str:
    lines = text.splitlines()[1:]
    while lines and not lines[0]:
        lines.pop(0)
    split = lines.index("")
    metadata, body = lines[:split], lines[split + 1 :]
    subject = next(line for line in metadata if line.startswith("Subject:"))
    fields = [line for line in metadata if line != subject]
    field_nodes = "".join(
        f'<text x="145" y="{242 + i * 25}" class="field">{html.escape(line)}</text>'
        for i, line in enumerate(fields)
    )
    body_nodes = []
    y = 355
    for line in body:
        if line == "-" * 36:
            body_nodes.append(
                f'<line x1="145" y1="{y - 7}" x2="755" y2="{y - 7}" stroke="#b8b8b8"/>'
            )
        elif line.startswith(">"):
            body_nodes.append(
                f'<rect x="145" y="{y - 17}" width="3" height="22" fill="#b5b5b5"/>'
                f'<text x="160" y="{y}" class="quote">{html.escape(line[1:].lstrip())}</text>'
            )
        else:
            css = (
                "fine"
                if line.startswith("Unsubscribe:")
                else "total"
                if line.startswith("Total ")
                else "body"
            )
            body_nodes.append(
                f'<text x="145" y="{y}" class="{css}">{html.escape(line)}</text>'
            )
        y += 24
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1200">
<defs><filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dy="5" stdDeviation="8" flood-color="#555" flood-opacity=".35"/></filter>
<style>.ui{{font-family:DejaVu Sans,sans-serif;fill:#e5e5e5}}.field{{font-family:DejaVu Sans,sans-serif;font-size:13px;fill:#4d4d4d}}.body{{font-family:DejaVu Sans Mono,monospace;font-size:14px;fill:#242424}}.total{{font-family:DejaVu Sans Mono,monospace;font-size:14px;font-weight:bold;fill:#111}}.quote{{font-family:DejaVu Sans,sans-serif;font-size:12px;fill:#777}}.fine{{font-family:DejaVu Sans,sans-serif;font-size:10px;fill:#777}}</style></defs>
<rect width="900" height="1200" fill="#c9c9c9"/><rect width="900" height="72" fill="#4b4b4b"/>
<circle cx="30" cy="36" r="6" fill="#8e8e8e"/><circle cx="52" cy="36" r="6" fill="#8e8e8e"/><circle cx="74" cy="36" r="6" fill="#8e8e8e"/>
<text x="112" y="42" class="ui" font-size="16">Email receipt.pdf</text><rect x="397" y="20" width="106" height="34" rx="3" fill="#3b3b3b"/><text x="425" y="42" class="ui" font-size="13">1 / 1</text>
<path d="M810 27v20m-10-10h20M842 27v20m-10-10h20" stroke="#d2d2d2" stroke-width="2" opacity=".8"/>
<rect x="95" y="102" width="710" height="1010" fill="#fff" filter="url(#shadow)"/>
<text x="145" y="154" font-family="DejaVu Sans" font-size="10" letter-spacing="2" fill="#888">PRINTED MESSAGE</text>
<text x="145" y="205" font-family="DejaVu Sans" font-size="19" font-weight="700" fill="#222">{html.escape(subject)}</text>{field_nodes}
<line x1="145" y1="326" x2="755" y2="326" stroke="#d0d0d0"/>{"".join(body_nodes)}
<line x1="145" y1="1064" x2="755" y2="1064" stroke="#ddd"/><text x="145" y="1087" font-family="DejaVu Sans" font-size="9" fill="#999">Printed from Mail</text><text x="744" y="1087" text-anchor="end" font-family="DejaVu Sans" font-size="9" fill="#999">1</text>
</svg>"""
