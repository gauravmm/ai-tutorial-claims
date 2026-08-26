"""Mobile messaging-app screenshot renderer."""

import html


def render(text: str, _seed: str) -> str:
    lines = [line.strip() for line in text.splitlines()[1:] if line.strip()]
    width = min(700, max(390, max(len(line) for line in lines) * 11 + 70))
    x = 830 - width
    height = 76 + (len(lines) - 1) * 36
    message_nodes = "".join(
        f'<text x="{x + 30}" y="{310 + i * 36}" class="message">{html.escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1200">
<defs><pattern id="doodle" width="120" height="120" patternUnits="userSpaceOnUse"><path d="M18 25q18-18 35 0M82 18l18 18-18 18M22 82q20-16 40 0t40 0" fill="none" stroke="#8ba09a" stroke-width="2" opacity=".12"/></pattern></defs>
<style>.sans{{font-family:DejaVu Sans,sans-serif}}.message{{font-family:DejaVu Sans,sans-serif;font-size:20px;fill:#172125}}</style>
<rect width="900" height="1200" fill="#e8eeeb"/><rect width="900" height="1200" fill="url(#doodle)"/>
<rect width="900" height="182" fill="#193d46"/><text x="42" y="48" class="sans" font-size="16" fill="#fff">9:41</text><circle cx="819" cy="43" r="5" fill="#fff"/><rect x="834" y="37" width="18" height="11" rx="2" fill="#fff"/>
<path d="M48 116l18-18m-18 18l18 18" fill="none" stroke="#fff" stroke-width="5"/><circle cx="118" cy="116" r="35" fill="#f2b35f"/><text x="118" y="126" text-anchor="middle" class="sans" font-size="27" font-weight="700" fill="#193d46">E</text>
<text x="172" y="110" class="sans" font-size="24" font-weight="700" fill="#fff">Expense notes</text><text x="172" y="138" class="sans" font-size="14" fill="#b8ccc9">Messages</text>
<circle cx="789" cy="116" r="5" fill="#fff"/><circle cx="812" cy="116" r="5" fill="#fff"/><circle cx="835" cy="116" r="5" fill="#fff"/>
<rect x="373" y="214" width="154" height="34" rx="17" fill="#d6dfdc"/><text x="450" y="237" text-anchor="middle" class="sans" font-size="13" font-weight="700" fill="#63736f">TODAY</text>
<rect x="{x}" y="268" width="{width}" height="{height}" rx="24" fill="#d8f7c8"/><path d="M830 {268 + height - 30}l28 24-28-3z" fill="#d8f7c8"/>{message_nodes}
<text x="{x + width - 24}" y="{268 + height - 16}" text-anchor="end" class="sans" font-size="12" fill="#69806f">10:42  sent</text>
<rect x="24" y="1090" width="852" height="82" rx="41" fill="#fff"/><circle cx="67" cy="1131" r="24" fill="#e7ecea"/><path d="M57 1131h20m-10-10v20" stroke="#667672" stroke-width="3"/><text x="112" y="1139" class="sans" font-size="19" fill="#9aa5a2">Message</text><circle cx="827" cy="1131" r="30" fill="#27867e"/><path d="M813 1132l24-13-7 28-6-10z" fill="#fff"/>
</svg>'''
