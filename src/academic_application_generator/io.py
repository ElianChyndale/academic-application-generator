"""Deterministic JSON, JSONL, CSV, Markdown, and hash helpers."""

from __future__ import annotations

import csv
import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


class DataError(ValueError):
    """Raised for unreadable or malformed input."""


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataError(f"cannot read JSON {path}: {exc}") from exc


def read_jsonl(path: Path) -> list[Any]:
    rows: list[Any] = []
    try:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise DataError(f"malformed JSONL at {path}:{line_number}: {exc}") from exc
    except OSError as exc:
        raise DataError(f"cannot read JSONL {path}: {exc}") from exc
    return rows


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    write_text(path, "".join(canonical_json(dict(row)) + "\n" for row in rows))


def write_csv(path: Path, rows: Sequence[Mapping[str, object]], fieldnames: list[str]) -> None:
    if not rows:
        raise ValueError("CSV output must contain at least one record")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
