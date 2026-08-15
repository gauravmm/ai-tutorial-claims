# Exercise: Expense Claims

## Background

Staff submitted mixed receipts. Finance needs one CSV.

In this exercise you will use an AI agent to extract those receipts and write `claim.csv`. The files come from four sources. Each source has its own layout. A vague prompt will get at least one source wrong.

## Your task

Produce a single CSV file, `claim.csv`, at the repo root. Write **one row per completed transaction**. Use these columns, in this order:

```csv
receipt_id,date,vendor,category,total,gst
R-1042,2026-03-12,Tanjong Kopi Pte Ltd,meals,18.50,1.53
TXN88213,2026-04-08,East Coast Hotel,accommodation,186.00,15.36
HN-03,2026-05-21,RideGo,transport,14.80,
```

Column definitions:

| Column | Description | Notes |
| --- | --- | --- |
| `receipt_id` | Receipt or transaction id | As printed. Unique. |
| `date` | Transaction date | `YYYY-MM-DD`. Use the transaction date, not the print date. |
| `vendor` | Merchant name | As printed. Trim whitespace. |
| `category` | Expense type | One of `meals`, `transport`, `equipment`, `accommodation`, `other`. |
| `total` | Amount actually paid | Two decimal places. SGD. Include service charge, tip, and rounding. |
| `gst` | GST in SGD | Two decimal places, or empty. Leave empty if the receipt charged no GST, or if it is not a tax invoice (no GST registration number). |

Currency is SGD only. GST is 9%. The claim period is 1 March 2026 through 31 July 2026 inclusive.

Do not write a row for a voided transaction. Do not write a row for a duplicate reprint.

## Source Data

The source data lives in `dataset/`. Each source file (`source_01.txt` through `source_04.txt`) holds many receipts. A delimiter line of `=` characters splits the records.

Open each source file before you write a prompt. The four layouts differ.

| File | Format | What you will see |
| --- | --- | --- |
| `source_01.txt` | Thermal POS printout | Itemized lines, `AMOUNT TENDERED` / `CHANGE`, loyalty points, `GST @9% (incl)`. Categories: meals, equipment, other. |
| `source_02.txt` | E-receipt email as text | Header and footer, quoted-reply cruft, subtotal plus GST on top, unsubscribe link. GST Reg. No. is present or absent. Categories: meals, accommodation, equipment. |
| `source_03.txt` | Ride-hailing app | Pickup and drop-off, surge, platform fee, tip, promo. No GST breakdown. Category: transport. |
| `source_04.txt` | Handwritten expenses note | Inconsistent spacing. Amounts such as `12.5` and `S$12.50`. Some entries have a scrawled reference instead of a receipt number. Mixed categories, including a co-working day pass. |

**Watch out for these traps.** A vague prompt will hit at least one:

- **Duplicate reprint in source 01.** Source 01 prints the same sale twice.
- **Near-duplicate that is a real second lunch.** Same vendor and same amount, but a different date and a different id.
- **Cross-source duplicate.** One ride appears as an app receipt and again as a handwritten note. There is no shared id. The handwritten note rounded the amount.
- **GST inclusive vs exclusive.** Source 01 prints GST inside the total. Source 02 adds GST on top of the subtotal.
- **Missing GST registration number.** The receipt prints a GST line, but it is not a tax invoice.
- **Service charge and tip.** Both are part of what was paid.
- **Voided sale.** The merchant voided the sale. It is not a claim.
- **Noise that looks like money.** Loyalty points, `AMOUNT TENDERED`, and a "you saved" line are not the total.
- **Rounding adjustment.** One receipt has a rounding line. The total is the amount charged after rounding.

## Getting started

Here is a first attempt at a prompt you could give the AI:

> Read every file in `dataset/`. Find every dollar amount. Sum them all and add 9% GST. Write `claim.csv` at the repo root with columns receipt_id, date, vendor, category, total, gst.

Try it. Look at the output. Is it correct? Is it even valid CSV?

A ready-to-paste copy of this prompt lives in [`prompts/starter.md`](prompts/starter.md).

One productive approach: ask the AI to describe what it sees in each source file. Then extract one source at a time. Getting each format right on its own is easier than debugging all four at once.

## What to think about

A good extraction prompt is precise. Vague instructions get interpreted in ways you did not intend. Consider:

- Which amount is the total? Receipts print many dollar figures. Which one is the amount actually paid?
- Is a reprint a second claim? Source 01 contains a reprint. What should the agent do with it?
- Source 01 includes GST in the total. Source 02 adds GST on top. Does your prompt treat both the same way?
- Some receipts print a GST line but have no GST registration number. What belongs in the `gst` cell?
- Service charge and tip appear on some receipts. Are they part of `total`?
- Loyalty points, tendered cash, and "you saved" lines look like money. Does your prompt exclude them?
- Source 04 writes dates and amounts in more than one style. Does your prompt cover that?
- Source 04 writes one date as `03/04/2026`. That date is ambiguous. What would you like the agent to do with an ambiguous date?
- Are all completed transactions in your output? Did you leave out voided sales and reprints?

## Checking your work

Open **Run and Debug** (`Ctrl+Shift+D`). Run **Check Extracted Data**.

The checker runs four levels of validation. It stops at the first failure.

1. **Structure.** Correct columns in the right order. Valid CSV. Correct row count. Unique `receipt_id` values.
2. **Value sanity.** Dates parse and sit in the claim period. `category` is one of the five values. Amounts are positive and two decimal places.
3. **Aggregate checksums.** Sums and counts must match expected totals. This catches systematic errors.
4. **Per-source hints.** If a checksum fails, the checker names the source and gives a hint about the trap.

## Stage 2: review the claim

After stage 1 is green, open [`prompts/review.md`](prompts/review.md). If you are stuck on stage 1, copy `dataset/claim.reference.csv` to `claim.csv` first.

That prompt starts a conversation over `claim.csv` (or the reference file) and the files in `policy/`. Walk through the talking points with the agent. There is no second checker. The point is the discussion.

## Stretch goals

These are outside the scope of the workshop. Come back to them on your own time once you have the basics working.

1. **Explain your prompt.** Annotate each sentence in your final prompt with a comment. Say what failure mode it guards against.
2. **Review skill.** There is a review skill in the repo. Decide whether you trust it.
3. **Extra source.** If you finish early, look in `dataset/extra/`.

<details>
<summary>Finance would like a word</summary>

![peace was never an option](.devcontainer/office-desk.jpg)

</details>
