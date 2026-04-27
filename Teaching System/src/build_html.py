#!/usr/bin/env python3
"""Inject latest teaching data into the dist HTML (dist-as-source pattern).

This script treats dist/tang-strategy-interactive.html as BOTH the source
template AND the output target.  It:
  1. Reads the existing dist HTML.
  2. Loads the latest data/processed/teaching_segments.json.
  3. Replaces the inline TEACHING_DATA assignment with the fresh JSON.
  4. Writes the result back to the same dist file.

Because the dist file IS the source, Git serves as the undo mechanism:
    git checkout -- dist/tang-strategy-interactive.html
"""

import json
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent  # 
DIST_CANDIDATES = [
    PROJECT_DIR / "dist" / "tang-strategy-interactive v0.5.html",
    PROJECT_DIR / "dist" / "tang-strategy-interactive v0.4.html",
    PROJECT_DIR / "dist" / "tang-strategy-interactive v0.2.html",
    PROJECT_DIR / "dist" / "tang-strategy-interactive.html",
]
DATA_FILE = PROJECT_DIR / "data" / "processed" / "teaching_segments.json"

# Regex: match  const TEACHING_DATA = <any JSON>;
# The data sits on a single line (output of previous builds), so `.*` is safe.
TEACHING_DATA_RE = re.compile(
    r"(const\s+TEACHING_DATA\s*=\s*)(\{.*\})(;\s*$)",
    re.MULTILINE,
)


def main() -> None:
    dist_html = next((path for path in DIST_CANDIDATES if path.exists()), DIST_CANDIDATES[0])

    # ── 1. Validate inputs ───────────────────────────────────────────
    if not dist_html.exists():
        sys.exit(f"ERROR: Dist file not found: {dist_html}")
    if not DATA_FILE.exists():
        sys.exit(f"ERROR: Data file not found: {DATA_FILE}")

    # ── 2. Load & compact the teaching data ──────────────────────────
    data_raw = DATA_FILE.read_text(encoding="utf-8")
    data = json.loads(data_raw)
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    print(f"Data: {data['meta']['total_segments']} segments, {len(compact):,} bytes (compact)")

    # ── 3. Read the dist HTML ────────────────────────────────────────
    html = dist_html.read_text(encoding="utf-8")

    # ── 4. Locate and replace the TEACHING_DATA variable ─────────────
    match = TEACHING_DATA_RE.search(html)
    if not match:
        sys.exit("ERROR: Could not locate 'const TEACHING_DATA = {...};' in dist HTML")

    old_size = len(match.group(2))
    new_html = TEACHING_DATA_RE.sub(
        lambda m: f"{m.group(1)}{compact}{m.group(3)}",
        html,
        count=1,
    )
    print(f"Replaced TEACHING_DATA: {old_size:,} → {len(compact):,} bytes")

    # ── 5. Write back ────────────────────────────────────────────────
    dist_html.write_text(new_html, encoding="utf-8")
    size_kb = dist_html.stat().st_size / 1024
    print(f"Output: {dist_html.name} ({size_kb:,.0f} KB)")
    if size_kb > 2048:
        print(f"WARNING: File exceeds 2 MB target ({size_kb:,.0f} KB)")
    else:
        print("OK: Within 2 MB target")


if __name__ == "__main__":
    main()
