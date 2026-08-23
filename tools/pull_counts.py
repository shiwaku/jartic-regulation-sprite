# -*- coding: utf-8 -*-
"""実データでのコードごとの件数を data/counts.csv に取り込む。

  python tools/pull_counts.py [../jartic-traffic-regulation-converter/data/parse_report.json]

どのアイコンが実際に多く使われるかを一覧（docs/icon-list.md）に出すためのもの。
無くてもビルドは通る。
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT.parent / "jartic-traffic-regulation-converter" / "data" / "parse_report.json"
OUT = ROOT / "data" / "counts.csv"


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not src.exists():
        raise SystemExit(f"{src} が無い")
    rep = json.loads(src.read_text(encoding="utf-8"))
    n = Counter()
    for key, count in rep.get("by_kind", {}).items():
        n[key.split("|", 1)[0]] += count
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["code", "n", "source"])
        for code, count in sorted(n.items(), key=lambda kv: -kv[1]):
            w.writerow([code, count, src.name])
    print(f"{OUT} に {len(n)} コード分を書いた（{sum(n.values()):,} 件）")


if __name__ == "__main__":
    main()
