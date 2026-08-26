"""Colorful GoRide mobile trip-screen renderer."""

import html


def render(text: str, _seed: str) -> str:
    lines = [line for line in text.splitlines()[1:] if line]
    trip, pickup, dropoff = lines[1:4]
    details = [line for line in lines[5:] if line != "-" * 32]
    paid = next(line for line in details if line.startswith("You paid"))
    payment = next(line for line in details if line.startswith("Charged to"))
    ride_id = next(line for line in details if line.startswith("Trip ID"))
    charges = details[: details.index(paid)]
    paid_label, paid_amount = paid.rsplit(None, 1)
    charge_nodes = []
    y = 680
    for line in charges:
        label, amount = line.rsplit(None, 1)
        charge_nodes.append(
            f'<text x="105" y="{y}" class="label">{html.escape(label)}</text>'
            f'<text x="795" y="{y}" text-anchor="end" class="value">{html.escape(amount)}</text>'
        )
        y += 48
    total_y = max(910, y + 28)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1200">
<style>.sans{{font-family:DejaVu Sans,sans-serif}}.label{{font-family:DejaVu Sans,sans-serif;font-size:20px;fill:#55606f}}.value{{font-family:DejaVu Sans,sans-serif;font-size:20px;font-weight:bold;fill:#202936}}</style>
<rect width="900" height="1200" fill="#eef3f4"/><rect width="900" height="410" fill="#0b8b83"/>
<circle cx="785" cy="125" r="175" fill="#ffb764" opacity=".95"/><circle cx="850" cy="55" r="92" fill="#ff6b68" opacity=".9"/>
<path d="M0 315 Q185 210 350 290 T690 250 T900 280" fill="none" stroke="#91ddd2" stroke-width="22" opacity=".45"/><path d="M40 145 Q260 230 450 115 T825 220" fill="none" stroke="#fff" stroke-width="5" opacity=".28"/>
<text x="62" y="52" class="sans" font-size="16" fill="#fff">9:41</text><circle cx="815" cy="46" r="5" fill="#fff"/><rect x="829" y="40" width="18" height="11" rx="2" fill="#fff"/>
<text x="62" y="118" class="sans" font-size="39" font-weight="800" fill="#fff">GoRide</text><rect x="62" y="145" width="176" height="40" rx="20" fill="#0a736c"/><path d="M78 164l5 5 9-11" fill="none" stroke="#fff" stroke-width="3"/><text x="101" y="171" class="sans" font-size="16" font-weight="700" fill="#fff">TRIP COMPLETE</text>
<circle cx="210" cy="273" r="16" fill="#fff"/><circle cx="210" cy="273" r="7" fill="#ff6b68"/><circle cx="650" cy="245" r="18" fill="#fff"/><rect x="644" y="239" width="12" height="12" rx="2" fill="#25324a"/><path d="M226 271 C350 190 490 330 632 248" fill="none" stroke="#25324a" stroke-width="5" stroke-dasharray="9 10"/>
<path d="M0 395 Q0 365 30 365 H870 Q900 365 900 395 V1200 H0Z" fill="#fff"/>
<text x="62" y="445" class="sans" font-size="13" font-weight="700" letter-spacing="2" fill="#0b8b83">TRIP RECEIPT</text><text x="838" y="445" text-anchor="end" class="sans" font-size="15" font-weight="700" letter-spacing="1" fill="#8c9aa6">{html.escape(ride_id.upper())}</text><text x="62" y="490" class="sans" font-size="22" font-weight="700" fill="#202936">{html.escape(trip)}</text>
<line x1="85" y1="535" x2="85" y2="625" stroke="#bed1d0" stroke-width="4"/><circle cx="85" cy="535" r="10" fill="#ff6b68"/><circle cx="85" cy="625" r="10" fill="#0b8b83"/>
<text x="115" y="542" class="sans" font-size="19" fill="#202936">{html.escape(pickup)}</text><text x="115" y="632" class="sans" font-size="19" fill="#202936">{html.escape(dropoff)}</text>
<line x1="62" y1="660" x2="838" y2="660" stroke="#e4e8eb"/>{"".join(charge_nodes)}
<rect x="62" y="{total_y - 45}" width="776" height="112" rx="22" fill="#25324a"/><text x="92" y="{total_y}" class="sans" font-size="18" font-weight="700" fill="#9be2d8">{html.escape(paid_label.upper())}</text><text x="808" y="{total_y + 10}" text-anchor="end" class="sans" font-size="42" font-weight="800" fill="#fff">${html.escape(paid_amount)}</text>
<rect x="62" y="{total_y + 88}" width="776" height="72" rx="18" fill="#eef3f4"/><text x="92" y="{total_y + 133}" class="sans" font-size="18" fill="#55606f">{html.escape(payment)}</text><circle cx="800" cy="{total_y + 124}" r="18" fill="#0b8b83"/><path d="M792 {total_y + 124}l6 6 11-14" fill="none" stroke="#fff" stroke-width="4"/>
</svg>'''
