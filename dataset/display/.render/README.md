# Receipt image renderer

`render.py` reads `dataset/source_??.txt` and `dataset/extra/source_??.txt`, splits each document into receipt blocks, and turns them into reproducible PNGs.

`render.py` dispatches each receipt to a source-specific SVG renderer:

- `source_01.py`: distressed physical thermal receipts on wood, with perforations, tears, rotation, creases, splotches, tape, speckles, burn lines, and uneven monospace ink.
- `source_02.py`: uniform email printouts in a drab PDF viewer, with fixed white pages, message metadata, and a monospace receipt body.
- `source_03.py`: colorful GoRide app screenshots with a route map, pickup/drop-off timeline, fare breakdown, total, and payment status.
- `source_04.py`: messaging-app screenshots of a claim thread. Lines marked
  `(Agent)` render as incoming bubbles and `(User)` as outgoing ones, so a note
  can span several turns. An unmarked line continues the bubble above it.
- `source_05.py`: scanned supplier documents (guest folios, quotations, credit
  notes, tax invoices) in the same drab PDF viewer as source 02. The first line
  is the heading, the lines before the first `-` rule are header fields, and the
  ruled table below splits each `label   amount` row into a left label and a
  right-aligned amount. Rows after the second rule are the bold totals, and any
  line without an amount becomes a closing note.

The dispatcher reads the selected source file, splits it at receipt boundaries, passes each block to its renderer, and rasterizes the returned SVG to a 900 x 1200 PNG with ImageMagick. Source 01's seed is derived from the source and receipt number, so its wear remains reproducible.

Run all matching sources:

```sh
python3 dataset/display/.render/render.py
```

Run one source:

```sh
python3 dataset/display/.render/render.py source_01
```

Requirements: Python 3.10+ and ImageMagick's `convert` command.
