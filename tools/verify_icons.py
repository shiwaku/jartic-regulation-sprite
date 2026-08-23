# -*- coding: utf-8 -*-
"""アイコンと配信物の整合を確かめる。

  python tools/verify_icons.py

見るのは次のとおり。

- data/codes.csv の「有効」なコードすべてに icons/<code>.svg があるか
- 逆に、コード表に無い SVG が混ざっていないか
- SVG が 64×64 で、文字要素（<text>）を含まないか
  ラスタライズ時のフォントに依存すると再現しなくなるため文字は禁止
- _site/sprite.json（ビルド済みなら）にすべてのコードが載っているか
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "icons"
CODES = ROOT / "data" / "codes.csv"
SPRITE = ROOT / "_site" / "sprite.json"
SIZE = 64


def main() -> int:
    with CODES.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    valid = {r["code"] for r in rows if r["status"] == "valid"}
    names = {r["code"]: r["name"] for r in rows}

    problems: list[str] = []

    svgs = {p.stem for p in ICONS.glob("*.svg")}
    for code in sorted(valid - svgs, key=int):
        problems.append(f"アイコンが無い: {code} {names[code]}")
    for code in sorted(svgs - valid, key=int):
        problems.append(f"コード表に無いアイコン: {code}.svg")

    for p in sorted(ICONS.glob("*.svg"), key=lambda q: int(q.stem)):
        text = p.read_text(encoding="utf-8")
        if "<text" in text:
            problems.append(f"{p.name}: 文字要素を含む（ラスタライズがフォントに依存する）")
        m = re.search(r'width="(\d+)"\s+height="(\d+)"', text)
        if not m or (int(m.group(1)), int(m.group(2))) != (SIZE, SIZE):
            problems.append(f"{p.name}: 描画サイズが {SIZE}×{SIZE} でない")
        # 公式意匠は元の座標系（例 0 0 435 435）を保つので、値は問わず有無だけ見る
        if "viewBox=" not in text:
            problems.append(f"{p.name}: viewBox が無い")

    if SPRITE.exists():
        sprite = json.loads(SPRITE.read_text(encoding="utf-8"))
        for code in sorted(valid - set(sprite), key=int):
            problems.append(f"sprite.json に無い: {code}")
        print(f"sprite.json: {len(sprite)} 個")
    else:
        print("sprite.json はまだ無い（npm run build で作る）")

    print(f"コード表: 有効 {len(valid)} / アイコン: {len(svgs)}")
    if problems:
        print("\n不整合:", file=sys.stderr)
        for p_ in problems:
            print(f"  - {p_}", file=sys.stderr)
        return 1
    print("整合している")
    return 0


if __name__ == "__main__":
    sys.exit(main())
