#!/usr/bin/env python3
"""Regenerate the dataset and confirm it matches the committed files."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / ".instructor" / "generate" / "build.py"
CHECK = ROOT / "check.py"
DATASET = ROOT / "dataset"
GENERATE = ROOT / ".instructor" / "generate"

TRACKED = (
    "source_01.txt",
    "source_02.txt",
    "source_03.txt",
    "claim.reference.csv",
    ".generate/ground_truth.csv",
    ".generate/checksums.csv",
)


def _run_check(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECK), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_gst_inclusive() -> None:
    sys.path.insert(0, str(GENERATE))
    from generate import GST_INCL_DEN, GST_INCL_NUM, money

    assert money(money("18.50") * GST_INCL_NUM / GST_INCL_DEN) == money("1.53")
    assert money(money("42.00") * money("0.09")) == money("3.78")


def test_regenerate() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "dataset"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(BUILD), "--dataset", str(out)],
            cwd=ROOT,
            check=True,
        )
        for rel in TRACKED:
            committed = (DATASET / rel).read_bytes()
            generated = (out / rel).read_bytes()
            assert committed == generated, f"drift in {rel}"


def test_handwritten_sources() -> None:
    """Sources 04 and 05 are hand-authored, so nothing regenerates their text."""
    sys.path.insert(0, str(ROOT))
    from check import source_of

    text = (DATASET / "source_04.txt").read_text()
    for row in csv.DictReader((DATASET / "claim.reference.csv").open()):
        rid = row["receipt_id"]
        if source_of(rid) != 4:
            continue
        assert rid in text, f"{rid} is in the CSVs but not in source_04.txt"
        assert row["vendor"] in text, f"vendor for {rid} is not in source_04.txt"


def test_reference_checks() -> None:
    proc = _run_check("--csv-file", str(DATASET / "claim.reference.csv"), "--verbose")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "ALL CHECKS PASSED" in proc.stdout


def test_missing_csv() -> None:
    proc = _run_check("--csv-file", str(ROOT / "no-such-claim.csv"))
    assert proc.returncode == 2
    assert "Check Extracted Data" in proc.stdout
    assert "ground_truth" not in proc.stdout
    assert ".generate" not in proc.stdout


def test_wrong_date_hints() -> None:
    rows = list(csv.DictReader((DATASET / "claim.reference.csv").open()))
    for row in rows:
        if row["receipt_id"] == "SUB-002":
            row["date"] = "2026-03-04"
            break
    with tempfile.NamedTemporaryFile(
        "w", newline="", suffix=".csv", delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        path = handle.name
    proc = _run_check("--csv-file", path)
    assert proc.returncode == 1, proc.stdout
    assert "03/04/2026" in proc.stdout
    assert "DD/MM" in proc.stdout


def test_filled_gst_without_reg_hints() -> None:
    rows = list(csv.DictReader((DATASET / "claim.reference.csv").open()))
    for row in rows:
        if row["receipt_id"] == "TXN88201":
            row["gst"] = "3.78"
            break
    with tempfile.NamedTemporaryFile(
        "w", newline="", suffix=".csv", delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        path = handle.name
    proc = _run_check("--csv-file", path)
    assert proc.returncode == 1, proc.stdout
    assert "source_02" in proc.stdout
    assert "GST Reg" in proc.stdout


if __name__ == "__main__":
    test_gst_inclusive()
    test_regenerate()
    test_handwritten_sources()
    test_reference_checks()
    test_missing_csv()
    test_wrong_date_hints()
    test_filled_gst_without_reg_hints()
    print("ok")
