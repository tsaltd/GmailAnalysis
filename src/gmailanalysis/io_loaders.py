from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import csv
import re

try:
    import openpyxl  # type: ignore
except Exception:
    openpyxl = None


REQUIRED_COLS = ["date", "from", "subject", "unique id"]


def _norm_col(s: str) -> str:
    # trim, collapse whitespace, lowercase
    return " ".join((s or "").strip().lower().split())


@dataclass(frozen=True)
class RawRow:
    date: str
    from_raw: str
    subject: str
    unique_id: str


def load_messages(path: str | Path, sheet_name: Optional[str] = None) -> List[RawRow]:
    """
    Stage A — Ingest
    Loads records from CSV/XLSX, normalizes required columns, returns RawRow list.
    No email parsing, no IDs, no classification (yet).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {p}")

    suf = p.suffix.lower()
    if suf == ".csv":
        return _load_csv(p)
    if suf in (".xlsx", ".xlsm"):
        return _load_xlsx(p, sheet_name=sheet_name)

    raise ValueError(f"Unsupported input type: {suf} (use .csv or .xlsx)")


def _require_columns(colmap: Dict[str, object]) -> None:
    missing = [c for c in REQUIRED_COLS if c not in colmap]
    if missing:
        raise ValueError(
            "Missing required column(s): "
            + ", ".join(missing)
            + ". Found: "
            + ", ".join(sorted(colmap.keys()))
        )


def _load_csv(p: Path) -> List[RawRow]:
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row")

        colmap = {_norm_col(h): h for h in reader.fieldnames}
        _require_columns(colmap)

        out: List[RawRow] = []
        for r in reader:
            out.append(
                RawRow(
                    date=(r.get(colmap["date"]) or "").strip(),
                    from_raw=(r.get(colmap["from"]) or "").strip(),
                    subject=(r.get(colmap["subject"]) or "").strip(),
                    unique_id=(r.get(colmap["unique id"]) or "").strip(),
                )
            )
        return out


def _load_xlsx(p: Path, sheet_name: Optional[str]) -> List[RawRow]:
    if openpyxl is None:
        raise RuntimeError("openpyxl not installed. Run: python -m pip install openpyxl")

    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active

    rows_iter = ws.iter_rows(values_only=True)
    header = next(rows_iter, None)
    if not header:
        raise ValueError("XLSX sheet is empty")

    headers = [str(h or "") for h in header]
    idxmap: Dict[str, int] = {_norm_col(h): i for i, h in enumerate(headers)}
    _require_columns(idxmap)

    def cell(row, key: str) -> str:
        v = row[idxmap[key]]
        return ("" if v is None else str(v)).strip()

    out: List[RawRow] = []
    for row in rows_iter:
        out.append(
            RawRow(
                date=cell(row, "date"),
                from_raw=cell(row, "from"),
                subject=cell(row, "subject"),
                unique_id=cell(row, "unique id"),
            )
        )
    return out
