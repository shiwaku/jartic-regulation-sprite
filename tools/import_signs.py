# -*- coding: utf-8 -*-
"""公式意匠（official/*.svg）を 64×64 のアイコンに正規化して icons/ に置く。

対応は data/official_refs.csv（コード → Commons のファイル名 → 標識令の番号）。

**パスには手を入れません。** ルート要素の width / height を 64 にし、viewBox が
無ければ元の寸法から補うだけです。中の文字はすでにパス化されているので、
ラスタライズ時にフォントを要りません（`<text>` が混ざっていたら止めます）。

official/ に置いた SVG は Wikimedia Commons の道路標識SVGで、意匠は
「道路標識、区画線及び道路標示に関する命令」別表第二にもとづきます。
法令の図案は著作権法13条により著作権の対象外です（Commons の表記は
PD-Japan-exempt）。取得元は data/official_refs.csv から辿れます。
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIGNS = ROOT / "signs"
ICONS = ROOT / "icons"
REFS = ROOT / "data" / "sign_refs.csv"
SIZE = 64
COMMONS = "https://commons.wikimedia.org/wiki/File:Japan_road_sign_{}.svg"

_SVG_TAG = re.compile(r"<svg\b[^>]*>", re.S)
_ATTR = re.compile(r'\s(width|height|viewBox)\s*=\s*"([^"]*)"', re.I)


def refs() -> list[dict]:
    with REFS.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _length(v: str) -> float | None:
    m = re.match(r"\s*([0-9.]+)", v or "")
    return float(m.group(1)) if m else None


def normalize(svg: str, source: str) -> str:
    """ルート要素だけを書き換えて 64×64 にする。"""
    m = _SVG_TAG.search(svg)
    if not m:
        raise ValueError("svg 要素が見つからない")
    tag = m.group(0)
    attrs = {k.lower(): v for k, v in _ATTR.findall(tag)}

    view_box = attrs.get("viewbox")
    if not view_box:
        w, h = _length(attrs.get("width", "")), _length(attrs.get("height", ""))
        if not w or not h:
            raise ValueError("viewBox も width/height も無い")
        view_box = f"0 0 {w:g} {h:g}"

    new_tag = _ATTR.sub("", tag)  # width/height/viewBox を消してから付け直す
    new_tag = new_tag.replace(
        "<svg", f'<svg width="{SIZE}" height="{SIZE}" viewBox="{view_box}"', 1
    )
    body = svg[m.end():]
    note = f"<!-- 出典: {source} / 意匠は標識令別表第二にもとづき著作権の対象外 -->"
    return f"{note}\n{new_tag}{body}"


def import_signs() -> set[str]:
    """icons/ に書き出したコードを返す。"""
    ICONS.mkdir(exist_ok=True)
    done: set[str] = set()
    for r in refs():
        code, name = r["code"], r["commons_file"]
        src = SIGNS / f"{name}.svg"
        if not src.exists():
            raise SystemExit(f"{src} が無い。data/official_refs.csv と official/ が合っていない。")
        svg = src.read_text(encoding="utf-8")
        if "<text" in svg:
            raise SystemExit(
                f"{src.name} が文字要素を含む。ラスタライズがフォントに依存するので使えない。"
            )
        (ICONS / f"{code}.svg").write_text(
            normalize(svg, COMMONS.format(name)), encoding="utf-8"
        )
        done.add(code)
    return done


if __name__ == "__main__":
    codes = import_signs()
    print(f"公式意匠から {len(codes)} 個のアイコンを作った")
