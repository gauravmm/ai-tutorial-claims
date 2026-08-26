#!/usr/bin/env python3
"""Dispatch source receipts to their matching visual renderer."""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

from source_01 import render as render_01
from source_02 import render as render_02
from source_03 import render as render_03
from source_04 import render as render_04

DISPLAY = Path(__file__).resolve().parent.parent
DATASET = DISPLAY.parent
RENDERERS = {
    "source_01": render_01,
    "source_02": render_02,
    "source_03": render_03,
    "source_04": render_04,
}


def read_receipts(source: Path) -> list[str]:
    boundary = re.escape("=" * 32)
    receipts = re.split(
        rf"\n\n(?={boundary}\n\n)", source.read_text(encoding="utf-8").strip()
    )
    if not receipts or any(not receipt.startswith("=" * 32) for receipt in receipts):
        raise ValueError(f"Could not identify every receipt in {source}")
    return receipts


def render_source(source: Path) -> None:
    output = DISPLAY / source.stem
    output.mkdir(parents=True, exist_ok=True)
    renderer = RENDERERS[source.stem]
    with tempfile.TemporaryDirectory(prefix="receipt-render-") as temporary:
        temporary_path = Path(temporary)
        for index, text in enumerate(read_receipts(source), 1):
            svg = temporary_path / f"receipt_{index:02}.svg"
            png = output / f"receipt_{index:02}.png"
            svg.write_text(
                renderer(text, f"{source.stem}-{index:02}"), encoding="utf-8"
            )
            subprocess.run(["convert", str(svg), str(png)], check=True)
            print(png.relative_to(DATASET.parent))


def main() -> None:
    sources = {path.stem: path for path in sorted(DATASET.glob("source_??.txt"))}
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", nargs="*", choices=sorted(sources))
    args = parser.parse_args()
    for name in args.sources or sorted(sources):
        render_source(sources[name])


if __name__ == "__main__":
    main()
