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
from gen_icons import BASIS_LABEL, DESIGNS, handdrawn_reasons  # noqa: E402
from import_signs import refs as sign_refs  # noqa: E402

CODES = ROOT / "data" / "codes.csv"
COUNTS = ROOT / "data" / "counts.csv"
REASONS = ROOT / "data" / "handdrawn_reasons.csv"
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
        "「出所」が標識の図案のものは、**標識令別表第二で定められた図案**を 64×64 に",
        "正規化して使っています（`signs/`）。SVGファイル自体は政府配布ではなく、",
        "Wikimedia Commons の利用者が図案を再現したもの（`PD-Japan-exempt`）です。",
        "",
        "手描き分の出所は3種類に分かれます。",
        "**道路標示の図にもとづく作図**は、別表第六（道路標示）の実物の図を e-Gov で",
        "確認して形を決めたもの。**標識の図案にもとづく作図**は、標識令に図案はあるが",
        "Commons に再現SVGが無いもの。**対応する標識・標示なし（独自）**だけが",
        "ゼロからの作図です。「参考」の列が根拠の標示・標識番号で、出典は",
        "[`../data/handdrawn_reasons.csv`](../data/handdrawn_reasons.csv)。詳しくは",
        "[design-spec.md](design-spec.md)。",
        "",
    ]

    signs = {r["code"]: r for r in sign_refs()}
    reasons = handdrawn_reasons() if REASONS.exists() else {}
    valid = [r for r in rows if r["status"] == "valid"]
    cols = ["コード", "交通規制種別", "出所", "参考", "意匠"]
    if counts:
        cols.append("実データの件数")
    lines += ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in valid:
        code = r["code"]
        o = signs.get(code)
        if o:
            src = "標識の図案"
            ref = o["sign_no"]
            desc = o["note"] or "標識令別表第二で定められた図案をそのまま使う"
        else:
            rs = reasons.get(code, {})
            src = BASIS_LABEL.get(rs.get("basis_kind"), "作図")
            ref = rs.get("basis") or "－"
            _r, desc, _parts = DESIGNS[code]
            if rs.get("note"):
                desc = rs["note"]
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
