"""Emit source files, ground truth, checksums, and the known-good claim.csv."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from formatters import FORMATTERS
from generate import COLUMNS, Receipt, fmt_money, planted

DELIM = "\n" + ("=" * 32) + "\n\n"


def source_path(dataset: Path, source: int) -> Path:
    if source == 5:
        return dataset / "extra" / "source_05.txt"
    return dataset / f"source_{source:02d}.txt"


def to_row(receipt: Receipt) -> dict[str, str]:
    return {
        "receipt_id": receipt.receipt_id,
        "date": receipt.date.isoformat(),
        "vendor": receipt.vendor,
        "category": receipt.category,
        "total": fmt_money(receipt.paid),
        "gst": fmt_money(receipt.gst) if receipt.gst is not None else "",
    }


def compute_checksums(rows: list[dict[str, str]]) -> dict[str, str]:
    checksums: dict[str, str] = {"row_count": str(len(rows))}
    checksums["sum_total"] = f"{sum(float(r['total']) for r in rows):.2f}"
    checksums["sum_gst"] = f"{sum(float(r['gst'] or 0) for r in rows):.2f}"
    counts = Counter(r["category"] for r in rows)
    for category in ("meals", "transport", "equipment", "accommodation", "other"):
        checksums[f"count_{category}"] = str(counts[category])
    checksums["sum_date_yyyymmdd"] = str(
        sum(int(r["date"].replace("-", "")) for r in rows)
    )
    for src in (1, 2, 3, 4):
        src_rows = [r for r in rows if source_of(r["receipt_id"]) == src]
        checksums[f"count_source_{src:02d}"] = str(len(src_rows))
        checksums[f"sum_total_source_{src:02d}"] = (
            f"{sum(float(r['total']) for r in src_rows):.2f}"
        )
        checksums[f"sum_gst_source_{src:02d}"] = (
            f"{sum(float(r['gst'] or 0) for r in src_rows):.2f}"
        )
        checksums[f"sum_date_source_{src:02d}"] = str(
            sum(int(r["date"].replace("-", "")) for r in src_rows)
        )
    return checksums


def source_of(receipt_id: str) -> int:
    if receipt_id.startswith("R-"):
        return 1
    if receipt_id.startswith("TXN"):
        return 2
    if receipt_id.startswith("HN-"):
        return 3
    if receipt_id.startswith("FOLIO"):
        return 5
    return 4


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(COLUMNS))
        writer.writeheader()
        writer.writerows(rows)


def build(dataset: Path) -> None:
    receipts = planted()
    by_source: dict[int, list[Receipt]] = {1: [], 2: [], 3: [], 4: [], 5: []}
    for receipt in receipts:
        by_source[receipt.source].append(receipt)

    for source, group in by_source.items():
        # Date order, with the reprint of R-1042 kept immediately after the original.
        if source == 1:
            original = [r for r in group if "reprint" not in r.flags]
            original.sort(key=lambda r: (r.date, r.receipt_id))
            ordered: list[Receipt] = []
            for receipt in original:
                ordered.append(receipt)
                if "reprint_original" in receipt.flags:
                    reprints = [
                        r
                        for r in group
                        if "reprint" in r.flags and r.receipt_id == receipt.receipt_id
                    ]
                    ordered.extend(reprints)
        else:
            ordered = sorted(group, key=lambda r: (r.date, r.receipt_id))
        formatter = FORMATTERS[source]
        chunks = [DELIM + formatter(r).rstrip() + "\n" for r in ordered]
        path = source_path(dataset, source)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(chunks).lstrip("\n"), encoding="ascii")
        print(f"{path}  ({len(ordered)} records)")

    gt_rows = [to_row(r) for r in receipts if r.claimable]
    gt_rows.sort(key=lambda r: (source_of(r["receipt_id"]), r["date"], r["receipt_id"]))
    generate_dir = dataset / ".generate"
    write_csv(generate_dir / "ground_truth.csv", gt_rows)
    write_csv(dataset / "claim.reference.csv", gt_rows)
    print(f"ground_truth  ({len(gt_rows)} rows)")

    checksums = compute_checksums(gt_rows)
    ck_path = generate_dir / "checksums.csv"
    with ck_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for key in sorted(checksums):
            writer.writerow([key, checksums[key]])
    print(f"checksums     ({len(checksums)} metrics)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=HERE.parent,
        help="Directory that receives source_0N.txt and claim.reference.csv",
    )
    args = parser.parse_args()
    build(args.dataset.resolve())


if __name__ == "__main__":
    main()
