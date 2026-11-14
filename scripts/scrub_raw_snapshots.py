"""Remove spokesperson fields from raw OpenAPI snapshots saved before v1.3.1.

Since v1.3.1 `app/tarik.py` drops the fields in `PII_LABELS` before a raw snapshot is
written. Snapshots saved by older versions may still hold them. Run once per data folder:

    python3 scripts/scrub_raw_snapshots.py                 # uses SENTINEL_DATA_DIR or ./data
    docker exec <container> python scripts/scrub_raw_snapshots.py   # inside the Docker image

Files are rewritten in place only when they contain a dropped field; nothing else changes.
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import tarik  # noqa: E402


def scrub(raw_dir: str = tarik.RAW_DIR) -> tuple[int, int]:
    """Return (files checked, files rewritten)."""
    checked = rewritten = 0
    for path in sorted(glob.glob(os.path.join(raw_dir, "*.json"))):
        checked += 1
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        clean = tarik.tanpa_pii(data)
        if clean != data:
            tmp = f"{path}.tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(clean, f, ensure_ascii=False)
            os.replace(tmp, path)
            rewritten += 1
    return checked, rewritten


if __name__ == "__main__":
    n, m = scrub()
    print(f"Checked {n} raw snapshot(s) in {tarik.RAW_DIR}; removed personal fields from {m}.")
