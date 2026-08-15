# Expense claim dataset

This dataset holds synthetic staff receipts for Harbour Digital Pte Ltd. Receipts come from four sources. Each source has its own text format.

Each source is a top-level file such as `source_01.txt`. A delimiter line of `=` characters splits the records.

`claim.reference.csv` is a known-good stage 1 file. Use it if you skip extraction and start the policy conversation.

## Sources

| File | Format | Notes |
| --- | --- | --- |
| `source_01.txt` | Thermal POS | Itemized lines, tender and change, loyalty points, GST inclusive |
| `source_02.txt` | E-receipt email as text | Header and footer, quoted reply, GST exclusive, GST Reg. No. present or absent |
| `source_03.txt` | Ride-hailing | Pickup and drop-off, surge, platform fee, tip, promo. No GST breakdown. |
| `source_04.txt` | Handwritten expenses note | Inconsistent spacing and amount formats. Mixed categories. |

Ignore `extra/` unless someone asks you to use it.

## Tips

Open each source file before you write an extraction prompt. A prompt written for one format will likely misread another.

One productive approach: ask the AI to describe what it sees in each source file. Then extract one format at a time.
