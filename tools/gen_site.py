# -*- coding: utf-8 -*-
"""配信サイト（_site）のトップページを作る。

  python tools/gen_site.py

`npm run build` のあとに走る（package.json の postbuild）。スプライトの4ファイルだけを
置くとルートが 404 になるため、次のものを用意する。

- `_site/index.html` … 配信URLと使い方、そして**アイコン73個の一覧**
- `_site/icons/*.svg` … 個別のアイコン（スプライトを使わず1枚だけ欲しいとき用）
"""
from __future__ import annotations

import csv
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gen_icons import BASIS_LABEL, handdrawn_reasons  # noqa: E402
from import_signs import refs as sign_refs  # noqa: E402

SITE = ROOT / "_site"
ICONS = ROOT / "icons"
CODES = ROOT / "data" / "codes.csv"
COUNTS = ROOT / "data" / "counts.csv"
BASE = "https://shiwaku.github.io/jartic-regulation-sprite"

CSS = """
:root {
  --ink: #14161a; --ink-2: #5a6069; --ink-3: #8b919b;
  --bg: #f6f7f9; --surface: #fff; --line: rgba(20,22,26,.12); --accent: #0066b3;
}
@media (prefers-color-scheme: dark) {
  :root {
    --ink: #f2f4f7; --ink-2: #b3b9c4; --ink-3: #7d838e;
    --bg: #15171b; --surface: #1c1f24; --line: rgba(255,255,255,.14); --accent: #4da3e0;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 32px 20px 64px; background: var(--bg); color: var(--ink);
  font-family: system-ui, -apple-system, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif;
  line-height: 1.7;
}
main { max-width: 1080px; margin: 0 auto; }
h1 { font-size: 22px; margin: 0 0 6px; }
h2 { font-size: 15px; margin: 32px 0 10px; padding-bottom: 6px; border-bottom: 1px solid var(--line); }
p, li { color: var(--ink-2); font-size: 13.5px; }
a { color: var(--accent); }
code, pre { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
pre {
  background: var(--surface); border: 1px solid var(--line); border-radius: 8px;
  padding: 12px 14px; overflow-x: auto; font-size: 12.5px; color: var(--ink);
}
code { font-size: 12.5px; }
.urls { list-style: none; padding: 0; }
.urls li { margin: 2px 0; }
.grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(148px, 1fr));
  gap: 10px; margin-top: 14px;
}
.item {
  background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
  padding: 10px; display: flex; gap: 10px; align-items: flex-start;
}
.item img { width: 40px; height: 40px; flex: none; }
.meta { min-width: 0; }
.code { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11px; color: var(--ink-3); }
.name { font-size: 12px; font-weight: 600; overflow-wrap: anywhere; }
.n { font-size: 10.5px; color: var(--ink-3); font-variant-numeric: tabular-nums; }
.note { font-size: 12px; color: var(--ink-3); }
footer { margin-top: 40px; font-size: 12px; color: var(--ink-3); }
"""


def main() -> None:
    if not SITE.exists():
        raise SystemExit(f"{SITE} が無い。先に npm run build を回す。")

    with CODES.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    valid = [r for r in rows if r["status"] == "valid"]

    counts: dict[str, int] = {}
    if COUNTS.exists():
        with COUNTS.open(encoding="utf-8") as f:
            counts = {r["code"]: int(r["n"]) for r in csv.DictReader(f)}

    # 個別のアイコンも置く（1枚だけ欲しいとき用）
    dest = SITE / "icons"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for svg in ICONS.glob("*.svg"):
        shutil.copy2(svg, dest / svg.name)

    sprite = json.loads((SITE / "sprite.json").read_text(encoding="utf-8"))

    signs = {r["code"] for r in sign_refs()}
    reasons = handdrawn_reasons()
    items = []
    for r in valid:
        code = r["code"]
        if code in signs:
            desc = "標識令の図案"
        else:
            desc = BASIS_LABEL.get(reasons.get(code, {}).get("basis_kind"), "作図")
        n = counts.get(code)
        items.append(
            f'<div class="item"><img src="icons/{code}.svg" alt="" loading="lazy" />'
            f'<div class="meta"><div class="code">{code}</div>'
            f'<div class="name">{html.escape(r["name"])}</div>'
            f'<div class="n">{f"{n:,} 件" if n else "実データに無し"}</div>'
            f'<div class="note">{html.escape(desc)}</div></div></div>'
        )

    usage = html.escape(
        "style.sprite = [\n"
        "  { id: 'default', url: '既存のスプライトのURL' },\n"
        f"  {{ id: 'reg', url: '{BASE}/sprite' }},\n"
        "]\n\n"
        "// 交通規制情報の属性 code からそのまま引ける\n"
        "'icon-image': ['concat', 'reg:', ['get', 'code']]"
    )

    doc = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>jartic-regulation-sprite</title>
<meta name="description" content="JARTIC 交通規制情報の共通規制種別コードごとのアイコンを MapLibre 向けスプライトとして配信します。" />
<style>{CSS}</style>
</head>
<body>
<main>
  <h1>jartic-regulation-sprite</h1>
  <p>日本道路交通情報センター（JARTIC）が公開している交通規制情報の
  <strong>共通規制種別コードごとのアイコン</strong>を、MapLibre 向けスプライトとして配信します。
  アイコン名はコードそのものです。</p>

  <h2>配信URL</h2>
  <ul class="urls">
    <li><a href="sprite.json">{BASE}/sprite.json</a></li>
    <li><a href="sprite.png">{BASE}/sprite.png</a></li>
    <li><a href="sprite@2x.json">{BASE}/sprite@2x.json</a></li>
    <li><a href="sprite@2x.png">{BASE}/sprite@2x.png</a></li>
  </ul>
  <p>個別のアイコンは <code>icons/&lt;コード&gt;.svg</code>（例
  <a href="icons/63.svg">icons/63.svg</a>）でも取得できます。</p>

  <h2>使い方</h2>
  <pre>{usage}</pre>
  <p><code>id</code> が <code>default</code> のスプライトはプレフィックス無しで参照できるため、
  背景地図のスタイルが持つ <code>icon-image</code> を書き換えずに足せます。</p>

  <h2>アイコン一覧（{len(valid)}種）</h2>
  <p>仕様書（拡張版標準フォーマット k_2.1）の表4 で有効な共通規制種別コードすべて。
  件数は2026年6月の全国データでの出現数です。
  「標識令の図案」は別表第二で定められた図案をそのまま使ったもの（SVGは Wikimedia Commons の
  再現物で、政府配布のファイルではありません）。「道路標示の図にもとづく作図」は
  対応する道路標識が無い路面標示などで、別表第六の実物の図を e-Gov で確認して
  描いたもの。ゼロから作図したのは「対応する標識・標示なし（独自）」の数個だけです。</p>
  <div class="grid">
    {"".join(items)}
  </div>

  <footer>
    標識の図案は標識令別表第二で定められたもの（著作権法13条により著作権の対象外）。
    手描きしたアイコンとツール類は MIT License です。
    <a href="https://github.com/shiwaku/jartic-regulation-sprite">GitHub</a> ／
    <a href="https://github.com/shiwaku/jartic-traffic-regulation-converter">変換器とビューワ</a>
  </footer>
</main>
</body>
</html>
"""
    (SITE / "index.html").write_text(doc, encoding="utf-8")
    print(f"{SITE / 'index.html'} を作った（アイコン {len(sprite)} / 一覧 {len(items)}）")
    print(f"{dest} に個別アイコンを {len(list(dest.glob('*.svg')))} 個置いた")


if __name__ == "__main__":
    main()
