"""Build a self-contained "reviewed" HTML snapshot.

Reads daily-review.html, injects a JSON market-data payload + strategy as
window.__EMBEDDED_*__ globals, and patches init() to consume them.

Usage:
    python build_reviewed_html.py --date 2026-04-27 \
        --strategy ../../strategies/json/tang_v4_4_slope.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]  # .../Tang strategy/Daily review

SRC_HTML = REPO / "daily-review.html"
LIVE_DIR = REPO / "market-data" / "live"
OUT_DIR = REPO / "reviewed"
DEFAULT_STRATEGY = REPO / "strategies" / "tang_v4_4_slope.json"

# Insertion anchors. Both must exist verbatim in daily-review.html.
STYLE_CLOSE = "</style>"
INIT_FALLBACK = "    await restoreSavedSession();\n  }"
INIT_PATCHED = """    if (window.__EMBEDDED_DATA__) {
      if (window.__EMBEDDED_STRATEGY__) {
        setCustomStrategy(window.__EMBEDDED_STRATEGY__, window.__EMBEDDED_STRATEGY_NAME__ || 'embedded-strategy.json');
      }
      loadData(window.__EMBEDDED_DATA__);
      setStorageStatus('Embedded snapshot · ' + (window.__EMBEDDED_DATE__ || ''), 'ok');
    } else {
      await restoreSavedSession();
    }
  }"""


def _safe_json(value: object) -> str:
    """Embed JSON inline as a JS literal. Escape `</script>` to keep parser happy."""
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return text.replace("</", "<\\/")


def build(date: str, strategy_path: Path, out: Path | None = None) -> Path:
    data_path = LIVE_DIR / date / f"SPY_{date}.json"
    if not data_path.exists():
        raise FileNotFoundError(f"Market data not found: {data_path}")
    if not strategy_path.exists():
        raise FileNotFoundError(f"Strategy not found: {strategy_path}")
    if not SRC_HTML.exists():
        raise FileNotFoundError(f"Source HTML not found: {SRC_HTML}")

    with data_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    with strategy_path.open("r", encoding="utf-8") as f:
        strategy = json.load(f)
    src = SRC_HTML.read_text(encoding="utf-8")

    if STYLE_CLOSE not in src:
        raise RuntimeError(f"Could not find {STYLE_CLOSE!r} in source HTML")
    if INIT_FALLBACK not in src:
        raise RuntimeError(f"Could not find init() fallback line in source HTML")

    embed_block = (
        f"{STYLE_CLOSE}\n"
        f"<script>"
        f"window.__EMBEDDED_DATE__={_safe_json(date)};"
        f"window.__EMBEDDED_STRATEGY_NAME__={_safe_json(strategy_path.name)};"
        f"window.__EMBEDDED_STRATEGY__={_safe_json(strategy)};"
        f"window.__EMBEDDED_DATA__={_safe_json(payload)};"
        f"</script>"
    )

    out_html = src.replace(STYLE_CLOSE, embed_block, 1)
    out_html = out_html.replace(INIT_FALLBACK, INIT_PATCHED, 1)

    out_path = out or (OUT_DIR / f"SPY_{date}_review.html")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_html, encoding="utf-8")
    return out_path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True, help="YYYY-MM-DD")
    p.add_argument("--strategy", default=str(DEFAULT_STRATEGY))
    p.add_argument("--out", default=None)
    args = p.parse_args()

    out = Path(args.out) if args.out else None
    result = build(args.date, Path(args.strategy), out)
    rel = result.relative_to(REPO.parent) if REPO.parent in result.parents else result
    print(f"wrote {rel}  ({result.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
