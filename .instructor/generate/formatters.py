"""One formatter per source. Prints items and the GST line. Does not re-derive paid."""

from __future__ import annotations

from datetime import date

from generate import Receipt, fmt_money, money


def _dmy(day: date) -> str:
    return day.strftime("%d/%m/%Y")


def _width(label: str, amount: str, width: int = 32) -> str:
    pad = width - len(label) - len(amount)
    if pad < 1:
        return f"{label} {amount}"
    return f"{label}{' ' * pad}{amount}"


def format_thermal(receipt: Receipt) -> str:
    lines: list[str] = []
    lines.append(receipt.vendor.center(32).rstrip())
    if receipt.address:
        lines.append(receipt.address.center(32).rstrip())
    if receipt.gst_reg:
        lines.append(f"GST REG: {receipt.gst_reg}".center(32).rstrip())
    lines.append("=" * 32)
    day = _dmy(receipt.date)
    left = f"Rcpt {receipt.receipt_id}"
    lines.append(_width(left, day))
    if receipt.time:
        lines.append(_width("", receipt.time))
    lines.append("-" * 32)
    for item in receipt.items:
        lines.append(_width(item.desc, fmt_money(item.amount)))
    lines.append("-" * 32)
    if receipt.gst_mode == "inclusive" and receipt.gst is not None:
        lines.append(_width("SUBTOTAL", fmt_money(receipt.paid)))
        lines.append(_width("GST @9% (incl)", fmt_money(receipt.gst)))
    elif receipt.gst_mode == "none":
        lines.append(_width("SUBTOTAL", fmt_money(receipt.paid)))
    lines.append("=" * 32)
    lines.append(_width("TOTAL", fmt_money(receipt.paid)))
    if receipt.tendered is not None:
        lines.append(_width("AMOUNT TENDERED", fmt_money(receipt.tendered)))
        change = money(receipt.tendered - receipt.paid)
        lines.append(_width("CHANGE", fmt_money(change)))
    if receipt.loyalty_pts is not None:
        lines.append(_width("LOYALTY PTS BAL", str(receipt.loyalty_pts)))
    if receipt.you_saved is not None:
        lines.append(_width("YOU SAVED", fmt_money(receipt.you_saved)))
    if receipt.payment:
        lines.append(receipt.payment)
    if "reprint" in receipt.flags:
        lines.append("*** REPRINT - DUPLICATE COPY ***")
    if "void" in receipt.flags:
        lines.append("*** VOID ***")
        lines.append(_width("REVERSAL", f"-{fmt_money(receipt.paid)}"))
    lines.append("=" * 32)
    return "\n".join(lines)


def format_email(receipt: Receipt) -> str:
    domain = "harbourview.sg"
    if "Riverview" in receipt.vendor:
        domain = "riverviewinn.sg"
    elif "Orchard" in receipt.vendor:
        domain = "orchardstay.sg"
    elif "Studio" in receipt.vendor:
        domain = "studiokit.sg"
    elif "Byte" in receipt.vendor:
        domain = "bytebazaar.sg"
    sent = receipt.print_date or receipt.date
    lines = [
        f"From: receipts@{domain}",
        "To: staff@harbourdigital.sg",
        f"Subject: Your e-receipt {receipt.receipt_id}",
        f"Date: {sent.strftime('%d %b %Y')} {receipt.time or '09:00'}",
        "",
        f"Thank you for your purchase at {receipt.vendor}",
        f"Transaction date: {receipt.date.strftime('%d %B %Y')}",
    ]
    if receipt.address:
        lines.append(receipt.address)
    if receipt.gst_reg:
        lines.append(f"GST Reg. No.: {receipt.gst_reg}")
    lines.append("")
    for item in receipt.items:
        lines.append(_width(item.desc, fmt_money(item.amount), 36))
    lines.append("-" * 36)
    lines.append(_width("Subtotal", fmt_money(receipt.subtotal), 36))
    if receipt.gst_mode == "exclusive":
        printed_gst = (
            receipt.gst
            if receipt.gst is not None
            else money(receipt.subtotal * money("0.09"))
        )
        # Exclusive no-reg still prints a GST line. The CSV gst cell stays empty.
        lines.append(_width("GST 9%", fmt_money(printed_gst), 36))
    lines.append(_width("Total", fmt_money(receipt.paid), 36))
    lines.append("")
    lines.append(f"Paid by {receipt.payment}")
    if receipt.quoted_reply:
        lines.extend(
            [
                "",
                f"> On {receipt.date.strftime('%d %b %Y')}, at {receipt.time or '12:00'}, you wrote:",
                "> please send receipt",
            ]
        )
    lines.extend(
        [
            "",
            f"Unsubscribe: https://{domain}/unsub?id={receipt.receipt_id}",
        ]
    )
    return "\n".join(lines)


def format_ride(receipt: Receipt) -> str:
    lines = [
        receipt.vendor,
        f"Trip completed  {receipt.date.strftime('%d %b %Y')}  {receipt.time}",
    ]
    if receipt.pickup:
        lines.append(f"Pickup:  {receipt.pickup}")
    if receipt.dropoff:
        lines.append(f"Dropoff: {receipt.dropoff}")
    lines.append("-" * 32)
    for item in receipt.items:
        lines.append(_width(item.desc, fmt_money(item.amount)))
    lines.append("-" * 32)
    lines.append(_width("You paid", fmt_money(receipt.paid)))
    lines.append(f"Charged to {receipt.payment}")
    lines.append(f"Trip ID {receipt.receipt_id}")
    return "\n".join(lines)


FORMATTERS = {
    1: format_thermal,
    2: format_email,
    3: format_ride,
}
