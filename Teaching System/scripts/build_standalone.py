"""build_standalone.py — Tang 策略教学系统 单文件构建器

把 dist/ 下的多文件版本（HTML 模板 + 3 个 jsx + kline-engine.js + 4 个 JSON 数据）
打包成单文件 standalone HTML，让用户双击即可在 file:// 模式下使用。

读取：
  - dist/Tang 策略教学系统.html               (模板)
  - dist/shared.jsx · pages-1.jsx · pages-2.jsx
  - dist/kline-engine/kline-engine.js
  - rules/compiled/index.json
  - cases/index.json
  - data/processed/teaching_segments.json
  - training/checkpoints.json

输出：
  - dist/Tang 策略教学系统-standalone.html

shared.jsx 的 useAppData 已经做了双模式：
  优先读 <script type="application/json" id="inline-data-*">；找不到时 fallback 到 fetch。
所以同一份 jsx 既能在 dev 模式（HTTP server）下用，也能在 standalone 单文件模式下用。

注意：CDN 资源（React / ReactDOM / Babel-standalone / Tailwind / Google Fonts）仍走外网，
首次打开需要联网，浏览器缓存后后续可离线使用。
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # Teaching System/
DIST = ROOT / "dist"

DATA_FILES = {
    "rules": ROOT / "rules" / "compiled" / "index.json",
    "cases": ROOT / "cases" / "index.json",
    "segments": ROOT / "data" / "processed" / "teaching_segments.json",
    "training": ROOT / "training" / "checkpoints.json",
}

JSX_FILES = ["shared.jsx", "pages-1.jsx", "pages-2.jsx"]
ENGINE_FILE = DIST / "kline-engine" / "kline-engine.js"
TEMPLATE = DIST / "Tang 策略教学系统.html"
OUTPUT = DIST / "Tang 策略教学系统-standalone.html"


def safe_inline(text: str) -> str:
    """转义 </script>，防止内联文本提前关闭外层 script 标签。"""
    return text.replace("</script>", "<\\/script>")


def main() -> None:
    if not TEMPLATE.exists():
        sys.exit(f"template not found: {TEMPLATE}")

    html = TEMPLATE.read_text(encoding="utf-8")
    sources = []  # (name, kb)

    # 1) inline kline-engine.js
    engine_js = ENGINE_FILE.read_text(encoding="utf-8")
    engine_marker = '<script src="kline-engine/kline-engine.js"></script>'
    if engine_marker not in html:
        sys.exit("could not locate <script src=kline-engine/kline-engine.js> in template")
    html = html.replace(
        engine_marker,
        "<script>\n" + safe_inline(engine_js) + "\n</script>",
        1,
    )
    sources.append((ENGINE_FILE.name, len(engine_js) / 1024))

    # 2) inline 3 个 jsx 文件（替换 <script type="text/babel" src="...">）
    for name in JSX_FILES:
        path = DIST / name
        jsx = path.read_text(encoding="utf-8")
        pattern = re.compile(
            r'<script type="text/babel" src="' + re.escape(name) + r'(?:\?[^"]*)?"></script>'
        )
        repl = '<script type="text/babel">\n' + safe_inline(jsx) + "\n</script>"
        new_html, n = pattern.subn(lambda _m, r=repl: r, html, count=1)
        if n != 1:
            sys.exit(f"failed to find <script src={name}> tag in template (matches: {n})")
        html = new_html
        sources.append((name, len(jsx) / 1024))

    # 3) inline 4 个 JSON 数据块（插在 </head> 之前）
    blocks = []
    for key, path in DATA_FILES.items():
        text = path.read_text(encoding="utf-8")
        json.loads(text)  # 校验合法 JSON；不重新序列化以保留原始格式
        blocks.append(
            f'<script type="application/json" id="inline-data-{key}">\n'
            + safe_inline(text)
            + "\n</script>"
        )
        sources.append((path.name, len(text) / 1024))
    inline_block = "\n".join(blocks)
    if "</head>" not in html:
        sys.exit("template missing </head>")
    html = html.replace("</head>", inline_block + "\n</head>", 1)

    # 4) 输出
    OUTPUT.write_text(html, encoding="utf-8")
    size_kb = OUTPUT.stat().st_size / 1024

    print(f"[ok] {OUTPUT.relative_to(ROOT)} -> {size_kb:.1f} KB")
    print("inlined sources:")
    for name, kb in sources:
        print(f"  {kb:>8.1f} KB  {name}")


if __name__ == "__main__":
    main()
