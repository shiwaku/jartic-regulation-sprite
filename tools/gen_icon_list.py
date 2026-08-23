# -*- coding: utf-8 -*-
"""docs/icon-list.md を作り直す。

  python tools/gen_icon_list.py

コード表（data/codes.csv）と意匠の定義（tools/gen_icons.py の DESIGNS）を突き合わせて、
「どのコードにどんな絵を当てたか」「何を参考にしたか」を一覧にする。
実データでの件数は data/counts.csv があれば添える（無くても動く）。
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gen_icons import DESIGNS  # noqa: E402
from import_official import refs as official_refs  # noqa: E402

CODES = ROOT / "data" / "codes.csv"
COUNTS = ROOT / "data" / "counts.csv"
OUT = ROOT / "docs" / "icon-list.md"


def main() -> None:
    with CODES.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    counts: dict[str, str] = {}
    if COUNTS.exists():
        with COUNTS.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                counts[r["code"]] = r["n"]

    lines = [
        "# アイコン一覧",
        "",
        "`tools/gen_icon_list.py` が作り直します。手で書き換えないでください。",
        "",
        "コードは JARTIC 交通規制情報の共通規制種別コード。アイコンのキーはコードそのもので、",
        "MapLibre では `['concat', 'reg:', ['get', 'code']]` で引けます。",
        "",
        "「出所」が公式意匠のものは、標識令別表第二にもとづく Wikimedia Commons の",
        "標識SVG（`PD-Japan-exempt`）を 64×64 に正規化して使っています（`official/`）。",
        "対応する道路標識が無い路面標示などは自作です。詳しくは",
        "[design-spec.md](design-spec.md)。",
        "",
    ]

    official = {r["code"]: r for r in official_refs()}
    valid = [r for r in rows if r["status"] == "valid"]
    cols = ["コード", "交通規制種別", "出所", "参考", "意匠"]
    if counts:
        cols.append("実データの件数")
    lines += ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in valid:
        code = r["code"]
        o = official.get(code)
        if o:
            src = "公式意匠"
            ref = o["sign_no"]
            desc = o["note"] or "標識令別表第二の意匠をそのまま使う"
        else:
            src = "自作"
            ref, desc, _parts = DESIGNS[code]
        cells = [f"`{code}`", r["name"], src, ref, desc]
        if counts:
            n = counts.get(code)
            cells.append(f"{int(n):,}" if n else "－")
        lines.append("| " + " | ".join(cells) + " |")

    unused = [r for r in rows if r["status"] != "valid"]
    lines += [
        "",
        "## アイコンを作っていないコード",
        "",
        "仕様書の表4 で「未使用」とされているもの。データに現れないためアイコンも作りません。",
        "",
        "| コード | 交通規制種別 | 備考 |",
        "|---|---|---|",
    ]
    for r in unused:
        lines.append(f"| `{r['code']}` | {r['name']} | {r['spec_note']} |")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{OUT} を更新した（有効 {len(valid)} / 未使用 {len(unused)}）")


if __name__ == "__main__":
    main()
