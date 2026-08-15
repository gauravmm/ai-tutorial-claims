# ai-tutorial-claims — spec / wishlist

**Status: spec only. Nothing here is built yet.** This document is written for the
agent (or human) who picks the task up next. Read it end to end before creating files.

Candidate replacement for the workshop's *first* hands-on task, currently
[ai-tutorial-scraping-prescriptions](https://github.com/gauravmm/ai-tutorial-scraping-prescriptions).
Same mechanics — messy text in, one clean CSV out, deterministic checker — but a domain
every attendee has suffered through personally, plus a second stage that introduces
*policy as a file the agent reads* rather than rules buried in a prompt.

---

## 1. The workshop constraints this must satisfy

Written down because every design decision below is downstream of them. This is the
make-or-break exercise: an attendee who gets frustrated here may not touch agentic tools
again for a year.

**Form.** Zero programming background. Free/cheap tier on *any* provider (Copilot Free,
AI Studio, OpenRouter). Runs entirely in-browser (GitHub Codespaces). Not a workflow that
is already solved by a product. The whole agent interaction is visible — no hidden server.
Must involve human-agent interaction.

**Scope.** Change the prompt, see the outcome in seconds. Small fixed knowledge base, no
information management during the session, no proprietary data. Short reasoning steps.
A toy of a real workflow. Not so simple that a spreadsheet would do it. Success and
failure both obvious and immediate.

**Difficulty.** Modular from first-time user to hobbyist programmer. Room for adversarial
constraints once someone finishes early. Some agent-agent "wow" to tease task 4.

---

## 2. Shape: two stages, two checkers

```
dataset/receipts/*.txt  ──[stage 1: extract]──▶  claim.csv  ──[stage 2: review]──▶  review.csv
                                                     ▲                                  ▲
                             policy/*.md ────────────┘──────────────────────────────────┘
```

**Stage 1 — Extract.** Point the agent at a folder of receipts in four different formats
and get one clean `claim.csv`. This is the warm-up: identical in spirit to the
prescriptions task, and it is where 80% of the room will spend the session.

**Stage 2 — Review.** Feed `claim.csv` plus a folder of short policy documents to a
second agent run, and get `review.csv` saying which lines are claimable, for how much, and
under which clause. This is where the interesting conversations live: the rules are in a
file, not the prompt; two policies disagree and one supersedes; a cap applies per *day*,
not per receipt.

**Each stage has its own checker and its own pass/fail.** A group that never gets stage 1
green must still be able to do stage 2 — see §6.

---

## 3. Stage 1 — Extraction

### 3.1 Output contract

`claim.csv`, one row per completed transaction, columns in this order:

| Column | Type | Notes |
|---|---|---|
| `receipt_id` | string | As printed on the receipt (`R-1042`, `TXN88213`, `HN-03`). Unique. |
| `date` | `YYYY-MM-DD` | Transaction date, not print date. |
| `vendor` | string | As printed, whitespace-trimmed, no trailing `PTE LTD` normalisation required. |
| `category` | enum | One of `meals`, `transport`, `equipment`, `accommodation`, `other`. |
| `currency` | ISO-4217 | `SGD`, `MYR`, `USD`. |
| `total` | 2dp | Total actually paid, in `currency`. |
| `gst` | 2dp or empty | GST amount in `currency`; empty when none was charged or the receipt is not a tax invoice. |
| `total_sgd` | 2dp | `total` converted using `dataset/fx-rates.md`. Equal to `total` for SGD. |

Excluded from the output: voided transactions and duplicate reprints (§3.3). The row
count therefore catches both over- and under-extraction, which is the single most useful
signal the checker can give.

### 3.2 Source formats

Four files under `dataset/receipts/`, each holding many records separated by a delimiter
line, mirroring the prescriptions layout:

- `source_01.txt` — thermal POS printouts. Itemised lines, `AMOUNT TENDERED` / `CHANGE`,
  loyalty points, GST-inclusive totals with a `GST @9% (incl)` line.
- `source_02.txt` — e-receipt emails rendered to text. Header/footer boilerplate,
  quoted-reply cruft, subtotal + GST added *on top*, an unsubscribe link.
- `source_03.txt` — ride-hailing / taxi app receipts. Pickup and drop-off, surge line,
  platform fee, tip, a promo discount, and no GST breakdown.
- `source_04.txt` — a hand-typed expenses note. Inconsistent spacing, some amounts
  written `12.5`, one written `S$12.50`, a couple of entries with a scrawled reference
  instead of a receipt number.

Target ~30–35 claimable records total. **Do not scale to 120 like the prescriptions
task** — on a free tier that becomes minutes per iteration, which breaks "see the outcome
in seconds".

### 3.3 Required complications

All of these ship in v1. Each one exists to punish a specific vague-prompt failure. The
starter prompt (§7) should hit at least three of them.

1. **Duplicate reprint.** The same transaction appears twice in `source_01` — same
   `receipt_id`, marked `*** REPRINT — DUPLICATE COPY ***`. Claim it once.
2. **Near-duplicate that is not a duplicate.** Same vendor, same amount, different date
   and different `receipt_id` (the attendee who eats the same lunch twice). An agent told
   simply to "remove duplicates" will drop a legitimate row here.
3. **Cross-source duplicate.** One taxi ride appears in both `source_03` (app receipt)
   and `source_04` (hand-typed note, no receipt number, slightly different amount because
   the note rounded). Resolving this requires matching on date + vendor + amount, not id
   — the fuzzy-identity problem that non-AI tools cannot do.
4. **GST-inclusive vs GST-exclusive.** `source_01` totals include GST; `source_02` adds
   it on top. A single arithmetic rule applied to both gets one of them wrong.
5. **Missing GST registration number.** Two receipts in `source_02` are not valid tax
   invoices (no GST reg. no.). `gst` must be empty even though a GST line is printed.
   Sets up the stage 2 rule about reclaiming GST.
6. **Foreign currency.** Two receipts in `MYR`, one in `USD`. Rates live in
   `dataset/fx-rates.md` — never fetched from the internet, so the exercise stays offline
   and reproducible.
7. **Service charge and tip.** `source_01` has 10% service charge before GST;
   `source_03` has a tip. Both are part of `total`; the stage 2 policy will disallow the
   tip, which is why they must survive extraction rather than being silently dropped.
8. **Voided transaction.** One record in `source_01` is marked `VOID` with a matching
   reversal line. It must not appear in the output.
9. **Ambiguous date.** One `source_04` entry reads `03/04/2026`. Elsewhere in the same
   file a `27/03/2026` establishes DD/MM. A good agent infers it; a better one says so.
   **This is the deliberate human-agent hook** — a prompt that tells the agent to ask
   about ambiguity rather than guess is the "right" answer, and the checker accepts only
   the DD/MM reading.
10. **Clinical-noise equivalent.** Loyalty points balances, `AMOUNT TENDERED`, and a
    "you saved $4.20" promo line all look like money and are not.
11. **Rounding.** One `source_01` receipt has a `ROUNDING ADJ -0.02` line; `total` is the
    rounded figure actually charged.

### 3.4 Checker

`check.py`, stdlib only, offline, run as `python check.py`. Four levels, following the
prescriptions checker so the two tasks feel the same:

1. **Structure** — columns present and in order, valid CSV, row count, `receipt_id`
   uniqueness, no literal `N/A`/`-` where a cell should be empty.
2. **Value sanity** — dates parse and fall inside the claim period, `category` in the
   enum, `currency` in the enum, amounts positive and 2dp, `total_sgd` consistent with
   `total` and the published rate.
3. **Aggregate checksums** — sum of `total_sgd`, sum of `gst`, count per category. Catches
   systematic errors (every GST computed the inclusive way) without leaking row answers.
4. **Per-source breakdown with hints** — on failure, name the source and the trap:
   *"source_03: your total is 12.00 low across 3 rows — is the tip part of what was paid?"*

Hints matter more than coverage. The prescriptions checker's per-source hints are the
reason attendees recover instead of stalling.

---

## 4. Stage 2 — Policy review

### 4.1 Output contract

`review.csv`, one row per row of `claim.csv`:

| Column | Type | Notes |
|---|---|---|
| `receipt_id` | string | Matches `claim.csv`. |
| `verdict` | enum | `covered`, `partial`, `not_covered`, `needs_approval`. |
| `amount_allowed` | 2dp SGD | What the company pays. `0.00` when `not_covered`. |
| `policy_ref` | string | `meals.md#3.2` — file plus clause number. |
| `reason` | free text | One line. **Not graded** — it exists so a human can audit, and so the discussion has something to point at. |

### 4.2 The policy corpus

Four short markdown files in `policy/`, each with numbered clauses so `policy_ref` is
exact. Keep the whole corpus under ~2 pages; this is a small, fixed knowledge base by
design.

- `general.md` — claim period, receipt required above $20, GST reclaimable only from a
  valid tax invoice, no claiming the same expense twice.
- `meals.md` — $35/person/day cap on meals, alcohol never claimable, service charge
  claimable, tips not.
- `transport.md` — economy public transport and taxis claimable, surge claimable, tips
  not, no claims for the daily home-office commute.
- `equipment.md` — under $200 claimable outright, $200–$1000 needs manager approval,
  above $1000 goes to procurement (i.e. `not_covered` on an expense claim).

### 4.3 Required complications

1. **A dated amendment.** `policy/2026-07-amendment.md` raises the meal cap from $35 to
   $40 effective 1 Jul 2026, and the claim period straddles that date. Whichever document
   the agent read *last* is not the answer; the dated one wins for dates after it. Same
   source-precedence lesson as the timetable idea, in a setting where it obviously matters.
2. **Per-day cap, not per-receipt.** Two meal receipts on the same day exceed $35
   together but neither does alone. The agent must group rows — the only step in the whole
   exercise that requires looking across rows, and the one that separates a careful prompt
   from a lucky one.
3. **Partial coverage.** One restaurant receipt has a wine line. The claim is `partial`,
   with `amount_allowed` equal to the total minus the alcohol (and minus the GST on it, if
   you want a stretch tier).
4. **The GST hook.** The two non-tax-invoice receipts from §3.3(5) are still claimable
   for the gross amount; only the GST reclaim is denied. Attendees consistently get this
   backwards, which makes it a good discussion.
5. **Approval band.** One equipment purchase lands in $200–$1000 → `needs_approval`, one
   above $1000 → `not_covered`.
6. **The duplicate again.** The cross-source duplicate from §3.3(3), if it survived stage 1,
   must be denied here under `general.md` "no double claiming" — so a stage 1 mistake
   surfaces a second time with a different error message.
7. **A genuine gap.** One receipt (a co-working day pass, say) is covered by no clause at
   all. The correct verdict is `needs_approval` with a `policy_ref` of `general.md#1`
   *and* a reason saying the policy is silent. Agents will happily invent a clause here;
   the checker catches the invented reference, which is the cheapest hallucination demo
   in the whole workshop.

### 4.4 Checker

`check_review.py`. Grades `verdict`, `amount_allowed`, and `policy_ref` exactly; ignores
`reason`. `policy_ref` is validated against the clause headings actually present in
`policy/`, so a made-up clause is reported as *"policy_ref meals.md#7.4 does not exist"*
rather than merely wrong.

---

## 5. Difficulty ladder

- **Tier 0 (everyone).** Stage 1, SGD-only receipts, `check.py` structure + sanity green.
- **Tier 1.** Full stage 1 green, all four sources, FX and duplicates handled.
- **Tier 2.** Stage 2 green on the straightforward verdicts.
- **Tier 3 (adversarial).** Add constraints once someone finishes early:
  - the finance team now wants amounts with no `+`/`-` signs and vendors upper-cased;
  - a fifth source arrives mid-exercise with a format nobody has seen (ship it as
    `dataset/extra/source_05.txt`, unmentioned in the README);
  - make the prompt robust: a malformed record must still produce a row with a sentinel,
    never a silent omission;
  - hand the agent a policy question it cannot answer from the corpus and see whether it
    says so.
- **Tier 4 (agent-agent, the tease for task 4).** The stage 1 agent writes the *prompt
  file* that the stage 2 agent will run — `prompts/review.md` becomes an artefact one agent
  authors and another consumes, graded by the same `check_review.py`. This is the "wow"
  moment; it costs nothing extra to build because both halves already exist.

---

## 6. Design decisions the next agent should not relitigate

- **Stage 2 ships its own known-good `claim.csv`** (`dataset/claim.reference.csv`).
  Anyone stuck on stage 1 copies it and continues. Never make stage 2 depend on stage 1
  succeeding; a room where half the attendees are locked out of the second half is the
  failure mode this whole task exists to avoid.
- **Everything is offline and in-repo.** FX rates, policies, receipts. No fetching, no
  accounts, no proprietary data — all fictitious vendors and synthetic amounts.
- **No student writes code.** The agent may write whatever code it likes; the attendee
  writes prompts and reads checker output. `check.py` must run on a bare Python 3.12
  devcontainer with no `pip install`.
- **The checkers are the ground truth.** Generate the dataset *from* a ground-truth table
  under `dataset/.generate/` (see the prescriptions repo for the pattern), never by
  hand-writing receipts and back-filling answers.
- **Categories are assigned by the source, not inferred.** Every receipt makes its
  category derivable without judgement — `category` should never be the thing that fails
  a run, because it is the one column where reasonable people disagree.

---

## 7. Repo layout to build

```
README.md                     # attendee-facing brief (rewrite this file into it)
AGENTS.md                     # ground rules for the coding agent, per repo convention
check.py                      # stage 1 checker
check_review.py               # stage 2 checker
.devcontainer/devcontainer.json   # python:3.12 image, ms-python.python — copy from prescriptions
dataset/
  README.md                   # what each source is, no answers
  receipts/source_01..04.txt
  extra/source_05.txt         # tier-3 surprise, undocumented
  fx-rates.md
  claim.reference.csv         # stage 2 entry point
  .generate/                  # generator, ground truth, checksums — the real source of truth
policy/
  general.md meals.md transport.md equipment.md 2026-07-amendment.md
prompts/
  starter.md                  # the deliberately flawed first prompt
  review.md                   # empty; tier-4 agent-agent artefact lands here
```

The attendee-facing README should follow the prescriptions one closely: background, the
output contract as a table, "watch out for these traps" (naming them without giving away
the fix), how to run the checker, and a starter prompt that is *plausible and wrong* —
e.g. one that says "sum every dollar amount you find and add 9% GST", which walks straight
into the inclusive/exclusive trap and the loyalty-points noise.

Consider shipping stage 1 **75% working**: a starter prompt that already passes sources 1–3
and fails source 4, so nobody's first five minutes are a blank page. This is the strongest
anti-frustration device available and costs one extra file.

---

## 8. Definition of done

- [ ] `python check.py` on the reference solution: green, and on a plausibly-vague prompt:
      red with a hint that names the source and the trap.
- [ ] `python check_review.py` likewise for stage 2, including a made-up `policy_ref`.
- [ ] A full stage 1 run completes in well under a minute on a free tier — time it on
      GitHub Copilot Free with a small model before committing to the record count.
- [ ] Codespaces boot → first checker run with no `pip install`, no auth beyond Copilot.
- [ ] Every complication in §3.3 and §4.3 is present and is caught by a checker level.
- [ ] Someone with no programming background finishes tier 1 in 25 minutes. Watch a real
      person do it before this replaces the prescriptions task in the workshop.

## 9. Open questions

1. **Record count.** 30–35 is the guess; the binding constraint is wall-clock per
   iteration on a free tier. Measure, then decide.
2. **How much arithmetic is too much?** GST, FX, service charge and a per-day cap is a
   lot of small-model arithmetic. If cheap tiers prove flaky, move FX to a stretch tier and
   ship SGD-only in the base dataset — the duplicates and the policy work are the parts
   that carry the lesson.
3. **Does the ambiguous date (§3.3(9)) belong in v1?** It is the only true human-agent
   interaction in stage 1 and the only trap with a defensible "the agent should ask"
   answer. It also risks reading as unfair. Suggest keeping it and calling it out in the
   attendee README as a question rather than a trap.
4. **Singapore-specific framing?** GST at 9%, `PTE LTD`, NETS, ride-hailing — good for the
   A\*STAR and NTU/NUS audiences, mildly parochial elsewhere. The generator should make the
   locale a single switch.
5. **Should stage 2 be conversational instead of batch?** A version where the agent walks
   the human through the borderline claims one at a time would satisfy the human-agent
   criterion far better, at the cost of the deterministic checker. Worth prototyping after
   v1 lands.
