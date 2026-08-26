#!/usr/bin/env python3
"""Validate claim.csv. Four levels, stop at the first failure.

Students launch this from Run and Debug (Check Extracted Data).
--verbose compares rows to ground truth and is for instructors.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKSUMS_PATH = HERE / "dataset" / ".generate" / "checksums.csv"
GROUND_TRUTH_PATH = HERE / "dataset" / ".generate" / "ground_truth.csv"

COLUMNS = ["receipt_id", "date", "vendor", "category", "total", "gst"]
CATEGORIES = {"meals", "transport", "equipment", "accommodation", "other"}
CLAIM_START = date(2026, 3, 1)
CLAIM_END = date(2026, 7, 31)
EMPTY_TOKENS = {"n/a", "na", "-", "--", "none", "null", "nil"}
MONEY_RE = re.compile(r"^\d+\.\d{2}$")
PREFIXES = (
    ("R-", 1),
    ("TXN", 2),
    ("HN-", 3),
    ("SUB-", 4),
    ("FOLIO", 5),
    ("QT-", 5),
    ("CN-", 5),
    ("INV-", 5),
)
UNKNOWN_SOURCE = 0
# Real documents that are deliberately out of scope for this claim.
EXTRA_SOURCES = {5: "dataset/extra/source_05.txt"}


class CheckError(Exception):
    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.code = code


def source_of(receipt_id: str) -> int:
    """Source file a receipt_id came from, or UNKNOWN_SOURCE if nothing matches."""
    for prefix, source in PREFIXES:
        if receipt_id.startswith(prefix):
            return source
    return UNKNOWN_SOURCE


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def load_checksums(path: Path) -> dict[str, str]:
    with path.open(newline="") as handle:
        return {row["metric"]: row["value"] for row in csv.DictReader(handle)}


def money_ok(value: str) -> bool:
    return bool(MONEY_RE.match(value))


def parse_day(value: str) -> date:
    return date.fromisoformat(value)


def _count_breakdown(rows: list[dict[str, str]], checksums: dict[str, str]) -> str:
    """Name the sources whose row count is off, with the claim.csv lines in each.

    Level 1 only has aggregate checksums, so it can point at the bucket that is
    wrong but not at the individual bad row.
    """
    groups: dict[int, list[int]] = {}
    for index, row in enumerate(rows, start=2):
        rid = (row.get("receipt_id") or "").strip()
        groups.setdefault(source_of(rid), []).append(index)
    detail = ["  Grouped by the prefix on each receipt_id."]
    for src in (1, 2, 3, 4):
        lines = groups.get(src, [])
        expected = int(checksums[f"count_source_{src:02d}"])
        if len(lines) == expected:
            continue
        where = f" - lines {', '.join(str(n) for n in lines)}" if lines else ""
        detail.append(
            f"    source_{src:02d}: {len(lines)} rows, expected {expected}{where}"
        )
    return "\n".join(detail)


def level_structure(rows: list[dict[str, str]], checksums: dict[str, str]) -> None:
    print("Level 1  structure")
    if not rows:
        raise CheckError("claim.csv has no data rows.")
    actual_cols = list(rows[0].keys())
    if actual_cols != COLUMNS:
        raise CheckError(f"Columns must be {COLUMNS} in that order. Got {actual_cols}.")

    extra: list[str] = []
    unknown: list[str] = []
    for index, row in enumerate(rows, start=2):
        rid = (row.get("receipt_id") or "").strip()
        if not rid:
            continue
        source = source_of(rid)
        if source in EXTRA_SOURCES:
            extra.append(f"    line {index}: {rid} ({EXTRA_SOURCES[source]})")
        elif source == UNKNOWN_SOURCE:
            unknown.append(f"    line {index}: {rid}")
    if extra:
        raise CheckError(
            f"{len(extra)} row(s) come from a document outside this claim.\n"
            "  Only the source files directly in dataset/ are in scope. "
            "A document in dataset/extra/ is not, however well it reads.\n"
            + "\n".join(extra)
        )
    if unknown:
        raise CheckError(
            f"{len(unknown)} receipt_id value(s) match no known prefix.\n"
            "  Copy the id printed on the document: R- (source_01), "
            "TXN (source_02), HN- (source_03), SUB- (source_04).\n"
            "  Do not build an id out of the date or the vendor name.\n"
            + "\n".join(unknown)
        )

    expected_n = int(checksums["row_count"])
    if len(rows) != expected_n:
        direction = "high" if len(rows) > expected_n else "low"
        raise CheckError(
            f"Row count is {len(rows)}, expected {expected_n} ({direction}).\n"
            "  Voided sales and reprint copies are not rows. "
            "A second lunch at the same stall on a different day is a row.\n"
            + _count_breakdown(rows, checksums)
        )

    seen: dict[str, int] = {}
    for index, row in enumerate(rows, start=2):
        rid = (row.get("receipt_id") or "").strip()
        if not rid:
            raise CheckError(f"Line {index}: receipt_id is empty.")
        if rid in seen:
            raise CheckError(
                f"receipt_id {rid!r} appears more than once. "
                "A reprint is the same sale, not a second claim."
            )
        seen[rid] = index
        for col in COLUMNS:
            cell = (row.get(col) or "").strip()
            if col == "gst":
                continue
            if not cell:
                raise CheckError(f"Line {index}: {col} is empty.")
            if cell.lower() in EMPTY_TOKENS:
                raise CheckError(
                    f"Line {index}: {col} is {cell!r}. "
                    "Use an empty cell, not a placeholder."
                )
        gst = (row.get("gst") or "").strip()
        if gst.lower() in EMPTY_TOKENS:
            raise CheckError(
                f"Line {index}: gst is {gst!r}. "
                "Leave the cell empty when there is no GST to reclaim."
            )
    print(f"  {len(rows)} rows, columns ok, receipt_id unique")


def level_sanity(rows: list[dict[str, str]]) -> None:
    print("Level 2  value sanity")
    for index, row in enumerate(rows, start=2):
        raw_date = row["date"].strip()
        try:
            day = parse_day(raw_date)
        except ValueError as err:
            raise CheckError(
                f"Line {index}: date {raw_date!r} is not YYYY-MM-DD."
            ) from err
        if day < CLAIM_START or day > CLAIM_END:
            raise CheckError(
                f"Line {index}: {raw_date} is outside the claim period "
                f"({CLAIM_START.isoformat()} to {CLAIM_END.isoformat()})."
            )
        if row["category"].strip() not in CATEGORIES:
            raise CheckError(
                f"Line {index}: category {row['category']!r} is not one of "
                f"{sorted(CATEGORIES)}."
            )
        total = row["total"].strip()
        if not money_ok(total) or float(total) <= 0:
            raise CheckError(
                f"Line {index}: total {total!r} must be a positive amount "
                "with two decimal places (example: 12.50)."
            )
        gst = row["gst"].strip()
        if gst and (not money_ok(gst) or float(gst) < 0):
            raise CheckError(
                f"Line {index}: gst {gst!r} must be empty or a two-decimal amount."
            )
    print("  dates, categories, and amounts ok")


def _sum_total(rows: list[dict[str, str]]) -> float:
    return round(sum(float(r["total"]) for r in rows), 2)


def _sum_gst(rows: list[dict[str, str]]) -> float:
    return round(sum(float(r["gst"] or 0) for r in rows), 2)


def level_checksums(rows: list[dict[str, str]], checksums: dict[str, str]) -> None:
    print("Level 3  aggregate checksums")
    failures: list[str] = []
    got_total = _sum_total(rows)
    exp_total = float(checksums["sum_total"])
    if got_total != exp_total:
        failures.append("sum of total")
    got_gst = _sum_gst(rows)
    exp_gst = float(checksums["sum_gst"])
    if got_gst != exp_gst:
        failures.append("sum of gst")
    counts = Counter(r["category"].strip() for r in rows)
    for category in ("meals", "transport", "equipment", "accommodation", "other"):
        if counts[category] != int(checksums[f"count_{category}"]):
            failures.append(f"count of {category}")
    got_dates = sum(int(r["date"].replace("-", "")) for r in rows)
    if str(got_dates) != checksums["sum_date_yyyymmdd"]:
        failures.append("dates")
    prefixes: Counter[str] = Counter()
    for row in rows:
        rid = row["receipt_id"].strip()
        if rid.startswith("R-"):
            prefixes["R"] += 1
        elif rid.startswith("TXN"):
            prefixes["TXN"] += 1
        elif rid.startswith("HN-"):
            prefixes["HN"] += 1
    for prefix in ("R", "TXN", "HN"):
        key = f"count_prefix_{prefix}"
        if key in checksums and prefixes[prefix] != int(checksums[key]):
            failures.append(f"printed {prefix} ids")
    if failures:
        raise CheckError(
            "Checksums failed: "
            + ", ".join(failures)
            + ". Level 4 names the source and the trap."
        )
    print("  sums and category counts match")


def _hint_for(source: int, metric: str, delta: float) -> str:
    name = f"source_{source:02d}"
    if source == 1 and metric == "count" and delta > 0:
        return f"{name}: extra row - did a reprint or a VOID sale get kept?"
    if source == 1 and metric == "count" and delta < 0:
        return (
            f"{name}: one row short - same vendor and amount on two dates "
            "is two lunches, not a duplicate."
        )
    if source == 1 and metric == "total" and delta > 5:
        return (
            f"{name}: totals are high - AMOUNT TENDERED and loyalty points "
            "are not what was paid."
        )
    if source == 1 and metric == "total" and -0.05 <= delta < 0:
        return (
            f"{name}: off by a few cents - the total is the amount after "
            "ROUNDING ADJ, not the figure before it."
        )
    if source == 1 and metric == "total" and delta < 0:
        return (
            f"{name}: totals are low - is the 10% service charge part of what was paid?"
        )
    if source == 2 and metric == "gst" and delta > 0:
        return (
            f"{name}: GST sum is high - a printed GST line is not enough. "
            "Look for a GST Reg. No. If it is missing, leave gst empty."
        )
    if source == 2 and metric == "total" and delta != 0:
        return (
            f"{name}: totals are off - source 02 adds GST on top of the "
            "subtotal. Do not apply the source 01 inclusive rule here."
        )
    if source == 3 and metric == "total" and delta < 0:
        return (
            f"{name}: your total is {abs(delta):.2f} low - is the tip part "
            "of what was paid?"
        )
    if source == 3 and metric == "count" and delta < 0:
        return (
            f"{name}: missing printed ids - ride receipts show HN-03, HN-07, "
            "and so on. Do not use the trip date or invent a GORIDE- id."
        )
    if source == 4 and metric == "count" and delta > 0:
        return (
            f"{name}: extra row - one taxi also appears in source_03 with a "
            "slightly rounded amount. Claim it once. "
            "If you renamed ride ids, put the printed HN- value back."
        )
    if source == 4 and metric == "date":
        return (
            f"{name}: a date is off - 03/04/2026 is ambiguous. "
            "The rest of the file uses DD/MM."
        )
    if metric == "gst":
        return f"{name}: GST sum is off by {delta:.2f}."
    if metric == "total":
        return f"{name}: total sum is off by {delta:.2f}."
    if metric == "count":
        return f"{name}: row count is off by {int(delta)}."
    return f"{name}: {metric} does not match."


def level_hints(rows: list[dict[str, str]], checksums: dict[str, str]) -> None:
    print("Level 4  per-source hints")
    prefixes: Counter[str] = Counter()
    for row in rows:
        rid = row["receipt_id"].strip()
        if rid.startswith("R-"):
            prefixes["R"] += 1
        elif rid.startswith("TXN"):
            prefixes["TXN"] += 1
        elif rid.startswith("HN-"):
            prefixes["HN"] += 1
    prefix_problems: list[str] = []
    hn_exp = int(checksums.get("count_prefix_HN", "0"))
    if prefixes["HN"] != hn_exp:
        prefix_problems.append(_hint_for(3, "count", float(prefixes["HN"] - hn_exp)))
    if prefixes["R"] != int(checksums.get("count_prefix_R", "0")):
        prefix_problems.append(
            "source_01: receipt_id values must be the printed R- numbers."
        )
    if prefixes["TXN"] != int(checksums.get("count_prefix_TXN", "0")):
        prefix_problems.append(
            "source_02: receipt_id values must be the printed TXN numbers."
        )
    if prefix_problems:
        raise CheckError("\n".join(prefix_problems))
    problems: list[str] = []
    for src in (1, 2, 3, 4):
        src_rows = [r for r in rows if source_of(r["receipt_id"]) == src]
        tag = f"{src:02d}"
        got_n = len(src_rows)
        exp_n = int(checksums[f"count_source_{tag}"])
        if got_n != exp_n:
            problems.append(_hint_for(src, "count", got_n - exp_n))
        got_t = _sum_total(src_rows)
        exp_t = float(checksums[f"sum_total_source_{tag}"])
        if got_t != exp_t:
            problems.append(_hint_for(src, "total", round(got_t - exp_t, 2)))
        got_g = _sum_gst(src_rows)
        exp_g = float(checksums[f"sum_gst_source_{tag}"])
        if got_g != exp_g:
            problems.append(_hint_for(src, "gst", round(got_g - exp_g, 2)))
        got_d = sum(int(r["date"].replace("-", "")) for r in src_rows)
        exp_d = int(checksums[f"sum_date_source_{tag}"])
        if got_d != exp_d:
            problems.append(_hint_for(src, "date", float(got_d - exp_d)))
    if problems:
        raise CheckError("\n".join(problems))
    print("  per-source sums match")


def level_verbose(rows: list[dict[str, str]], expected: list[dict[str, str]]) -> None:
    print("Level V  row-by-row (instructor)")
    actual_by_id = {r["receipt_id"].strip(): r for r in rows}
    expected_by_id = {r["receipt_id"].strip(): r for r in expected}
    missing = sorted(set(expected_by_id) - set(actual_by_id))
    extra = sorted(set(actual_by_id) - set(expected_by_id))
    lines: list[str] = []
    if missing:
        lines.append(f"  missing: {', '.join(missing)}")
    if extra:
        lines.append(f"  extra: {', '.join(extra)}")
    mismatches = 0
    for rid in sorted(set(actual_by_id) & set(expected_by_id)):
        actual = actual_by_id[rid]
        want = expected_by_id[rid]
        for col in COLUMNS:
            got = (actual.get(col) or "").strip()
            exp = (want.get(col) or "").strip()
            if col in {"total", "gst"}:
                same = (got or "0") == (exp or "0") or (
                    got != "" and exp != "" and abs(float(got) - float(exp)) < 0.001
                )
                if got == "" or exp == "":
                    same = got == exp
            else:
                same = got == exp
            if not same:
                mismatches += 1
                lines.append(f"  {rid} {col}: expected {exp!r}, got {got!r}")
    if lines:
        print("\n".join(lines))
        raise CheckError(f"{mismatches} field(s) differ from ground truth.")
    print("  every field matches ground truth")


def run(csv_path: Path, verbose: bool) -> None:
    if not csv_path.is_file():
        raise CheckError(
            f"{csv_path} is missing.\n"
            "  Produce claim.csv first, then run Check Extracted Data "
            "from Run and Debug (Ctrl+Shift+D).",
            code=2,
        )
    try:
        rows = load_csv(csv_path)
    except csv.Error as err:
        raise CheckError(f"claim.csv is not valid CSV: {err}") from err

    try:
        checksums = load_checksums(CHECKSUMS_PATH)
    except FileNotFoundError as err:
        raise CheckError(
            "Internal checksum file is missing. "
            "Re-run python3 dataset/.generate/build.py.",
            code=2,
        ) from err

    level_structure(rows, checksums)
    level_sanity(rows)
    try:
        level_checksums(rows, checksums)
    except CheckError as err:
        print(f"  {err}")
        level_hints(rows, checksums)
        raise
    print("ALL CHECKS PASSED")
    if verbose:
        expected = load_csv(GROUND_TRUTH_PATH)
        level_verbose(rows, expected)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate claim.csv")
    parser.add_argument(
        "--csv-file",
        type=Path,
        default=HERE / "claim.csv",
        help="Student CSV (default: ./claim.csv)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Compare each row to ground truth (instructor)",
    )
    args = parser.parse_args()
    try:
        run(args.csv_file, verbose=args.verbose)
    except CheckError as err:
        print(f"ERROR: {err}")
        sys.exit(err.code)


if __name__ == "__main__":
    main()
