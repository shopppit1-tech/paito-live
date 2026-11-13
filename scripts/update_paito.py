#!/usr/bin/env python3
"""Fetch and validate the public Sydney Paito table used by Angkanet."""
from __future__ import annotations

import json
import re
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from html.parser import HTMLParser

SOURCE_PAGE = "https://angkanet.college/paito-warna-sydney-pools/"
SOURCE_ENDPOINT = "https://angkanet.college/warna.php?mar=sydney"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "paito-sdy.json"
WEEKDAYS = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]


class PaitoTableParser(HTMLParser):
    """Extract digit cells from the source's #drawing-table tbody."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_table = False
        self.in_body = False
        self.in_row = False
        self.in_cell = False
        self.cell_text: list[str] = []
        self.row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "table" and attributes.get("id") == "drawing-table":
            self.in_table = True
        elif self.in_table and tag == "tbody":
            self.in_body = True
        elif self.in_body and tag == "tr":
            self.in_row = True
            self.row = []
        elif self.in_row and tag == "td":
            self.in_cell = True
            self.cell_text = []

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self.in_cell:
            self.row.append("".join(self.cell_text).strip())
            self.in_cell = False
        elif tag == "tr" and self.in_row:
            if self.row and any(self.row):
                self.rows.append(self.row)
            self.in_row = False
        elif tag == "tbody":
            self.in_body = False
        elif tag == "table" and self.in_table:
            self.in_table = False


def fetch_source() -> str:
    request = urllib.request.Request(
        SOURCE_ENDPOINT,
        headers={
            "User-Agent": "PaitoLiveRefresh/1.0 (+https://github.com/shopppit1-tech/paito-live)",
            "Referer": SOURCE_PAGE,
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status != 200:
                    raise RuntimeError(f"Source returned HTTP {response.status}")
                content_type = response.headers.get("Content-Type", "")
                if "html" not in content_type.lower():
                    raise RuntimeError(f"Unexpected source content type: {content_type}")
                content = response.read(2_000_000)
                return content.decode("utf-8", errors="replace")
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Could not download complete source response after 3 attempts: {last_error}")


def parse_rows(html: str) -> list[list[str]]:
    parser = PaitoTableParser()
    parser.feed(html)
    rows: list[list[str]] = []
    for raw_row in parser.rows:
        if not raw_row or not any(raw_row):
            continue
        if len(raw_row) != 35 or any(value != "" and not re.fullmatch(r"\d", value) for value in raw_row):
            raise RuntimeError(f"Unexpected Paito row shape: {len(raw_row)} cells")
        groups = [raw_row[offset : offset + 5] for offset in range(0, 35, 5)]
        results = []
        for group in groups:
            four_digits = group[:4]
            if any(not digit for digit in four_digits) and any(four_digits):
                raise RuntimeError("A source row contains a partially populated four-digit result")
            # The fifth source cell is the count field, not part of the 4D result.
            results.append("".join(four_digits) if all(four_digits) else "")
        rows.append(results)
    if not 10 <= len(rows) <= 600:
        raise RuntimeError(f"Unexpected Paito row count: {len(rows)}")
    return rows


def main() -> None:
    rows = parse_rows(fetch_source())
    payload = {
        "source_name": "Angkanet — Paito Warna Sydney",
        "source_page": SOURCE_PAGE,
        "source_endpoint": SOURCE_ENDPOINT,
        "fetched_at": datetime.now(ZoneInfo("Asia/Jakarta")).isoformat(timespec="seconds"),
        "weekdays": WEEKDAYS,
        "rows": rows,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(rows)} rows from {SOURCE_ENDPOINT} to {OUTPUT}")


if __name__ == "__main__":
    main()
