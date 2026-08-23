# -*- coding: utf-8 -*-
"""共通規制種別コードごとのアイコン SVG を icons/ に書き出す。

  python tools/gen_icons.py

コードの一覧は data/codes.csv（JARTIC 拡張版標準フォーマット k_2.1 の表4 の写し）が
情報源で、そこに載る「有効」な73コードすべてに1つずつアイコンを作る。
ファイル名はコードそのもの（例 icons/63.svg）。MapLibre では

  'icon-image': ['concat', 'reg:', ['get', 'code']]

で引ける。意匠の考え方は docs/design-spec.md。
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from icons_lib import (  # noqa: E402
    BLUE, RED, WHITE, YELLOW,
    arrow, arrow_ring, arrow_turn, arrow_uturn, arrows_lane, arrows_pass,
    arrows_two_step, bar_h, blue_circle, blue_circle_red_ring, blue_pentagon,
    blue_rect, blue_square, centered, cross, disc, mark_box_cross, mark_crosswalk,
    mark_arrows_lane, mark_line, mark_lines, mark_parking_bay, mark_platform,
    mark_roadside,
    mark_shift, mark_stopline, mark_zebra, picto_ahead_priority, picto_bike,
    picto_bus, picto_car, picto_cart, picto_clock, picto_clover, picto_height,
    picto_horn, picto_moto, picto_p, picto_ped, picto_ped_child,
    picto_priority_road, picto_railcross, picto_signal, picto_tram, picto_truck,
    picto_weight, place, road, ring, slash, svg, tri_down, white_square_red_border,
)

from import_signs import import_signs, refs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "icons"
CODES = ROOT / "data" / "codes.csv"


# ---- 家族ごとの組み立て ----------------------------------------------------

def prohibit(picto: str | None = None, mark: str | None = None, scale: float = 0.40) -> list[str]:
    """禁止。白地に赤の縁。中に青のピクトグラムと赤の斜線。"""
    parts = [disc(WHITE), ring(RED)]
    if picto:
        parts.append(centered(picto, scale))
    parts.append(mark if mark is not None else slash())
    return parts


def limit(picto: str) -> list[str]:
    """制限（重量・高さ・速度）。白地に赤の縁。斜線は付かない。"""
    return [disc(WHITE), ring(RED), centered(picto, 0.40)]


def designate(picto: str, scale: float = 0.32) -> list[str]:
    """指定・専用。青地に白。"""
    return blue_circle() + [centered(picto, scale)]


def instruct(picto: str, scale: float = 0.34) -> list[str]:
    """指示。青の正方形に白。"""
    return blue_square() + [centered(picto, scale)]


def prohibit_square(picto: str, scale: float = 0.5) -> list[str]:
    """歩行者向けの禁止。白地・赤枠の正方形に青のピクトと赤の斜線（331・332）。"""
    return white_square_red_border() + [centered(picto, scale), slash()]


def no_parking(mark: str) -> list[str]:
    """駐車・駐停車禁止。青地に赤の縁と赤の斜線／×。"""
    return blue_circle_red_ring() + [mark]


def marking(*parts: str) -> list[str]:
    """路面標示。灰の路面に白（または黄）の線。"""
    out = road()
    for p in parts:
        out.extend(p if isinstance(p, list) else [p])
    return out


# ---- コードごとの意匠 ------------------------------------------------------
# (参考にした標識・標示, 意匠の説明, 組み立て)
# 参考番号は道路標識、区画線及び道路標示に関する命令の番号。文字だけで種別を
# 表す標識は、文字を使えないため幾何図形に置き換えている（説明に理由を書く）。

DESIGNS: dict[str, tuple[str, str, list[str]]] = {
    # ---- 通行止め・通行禁止 ----
    "1": ("325の4", "青地に大人と子ども（歩行者専用）", designate(picto_ped_child(), 0.42)),
    "2": ("325の2", "青地に自転車", designate(picto_bike())),
    "3": ("325の3", "青地に歩行者と自転車（左に歩行者、右下に自転車）",
          blue_circle() + [place(picto_ped(), 10, 16, 0.28),
                           place(picto_bike(), 20, 28, 0.26)]),
    "4": ("301", "白地・赤縁に赤の×（すべて通行止め）", prohibit(mark=cross())),
    "5": ("302", "白地・赤縁に赤の斜線（車両通行止め）", prohibit()),
    "6": ("310の2", "二輪車に赤の斜線（二人乗り禁止）", prohibit(picto_moto(BLUE), scale=0.42)),
    "7": ("302＋踏切", "白地・赤縁に踏切の記号と赤の斜線（車両通行止め・踏切）",
          prohibit(picto_railcross(BLUE), scale=0.34)),
    "8": ("331", "白地・赤枠の四角に歩行者と赤の斜線（歩行者通行止め）",
          prohibit_square(picto_ped(BLUE), 0.46)),
    "9": ("320", "白地・赤縁に荷重の記号（重量制限。実物は「5.5t」の文字）",
          limit(picto_weight(BLUE))),
    "10": ("321", "白地・赤縁に高さの記号（高さ制限。実物は「3.3m」の文字）",
           limit(picto_height(BLUE))),
    "13": ("303", "赤地に白の横棒（車両進入禁止）", [disc(RED), bar_h()]),
    "14": ("332", "白地・赤枠の四角に横断する歩行者と赤の斜線（歩行者横断禁止）",
           white_square_red_border()
           + [place(picto_ped(BLUE), -4, 4, 0.42),
              f'<g opacity="0.9"><rect x="14" y="46" width="5" height="8" fill="{BLUE}"/>'
              f'<rect x="24" y="46" width="5" height="8" fill="{BLUE}"/>'
              f'<rect x="34" y="46" width="5" height="8" fill="{BLUE}"/>'
              f'<rect x="44" y="46" width="5" height="8" fill="{BLUE}"/></g>',
              slash()]),
    "19": ("路面標示", "白枠の中に斜縞（立入り禁止部分）", marking(mark_zebra(frame=True))),
    "76": ("路面標示", "白枠に×（停止禁止部分）", marking(mark_box_cross())),
    "90": ("路面標示", "斜縞（導流帯）", marking(mark_zebra())),

    # ---- 一方通行・方向 ----
    "11": ("326-A", "横長の青地に白の矢印（一方通行）",
           blue_rect() + [place(arrow("right"), 12, 12, 0.4)]),
    "12": ("311", "青地に白の直進矢印（指定方向外進行禁止）", designate(arrow("up"), 0.34)),
    "60": ("路面標示", "路面に白の矢印（進行方向）", marking(mark_arrows_lane(1))),
    "50": ("312", "右折矢印に赤の斜線（車両横断禁止）", prohibit(arrow_turn("right", BLUE), scale=0.40)),
    "51": ("313", "転回矢印に赤の斜線（転回禁止）", prohibit(arrow_uturn(BLUE), scale=0.40)),
    "53": ("314", "2本の矢印に赤の斜線（追越し禁止）", prohibit(arrows_pass(BLUE), scale=0.42)),
    "55": ("327の8", "青の円に二段階の軌跡（原付の右折方法・二段階）",
           designate(arrows_two_step(), 0.34)),
    "56": ("327の9", "白地・赤縁に右折矢印（原付の右折方法・小回り）",
           [disc(WHITE), ring(RED), centered(arrow_turn("right", BLUE), 0.34)]),
    "57": ("路面標示", "青の四角に左折と右折の矢印（右左折の方法）",
           blue_square() + [place(arrow_turn("left"), -4, 14, 0.36),
                            place(arrow_turn("right"), 30, 14, 0.36)]),
    "58": ("路面標示", "路面に左折・直進・右折の矢印（進行方向別通行区分）",
           marking(mark_arrows_lane())),
    "94": ("路面標示", "青地に左向きの矢印（左折可）",
           blue_square() + [place(arrow("left"), 12, 12, 0.4)]),
    "106": ("327の10", "青地に右回りの環状矢印（環状交差点における右回り通行）",
            designate(arrow_ring(), 0.34)),

    # ---- 速度 ----
    "49": ("324", "白地・赤縁に上向き矢印（最低速度。実物は数字と下線）",
           limit(arrow("up", BLUE))),
    "61": ("329", "白地・赤縁の逆三角形（徐行）",
           tri_down(WHITE, RED) + [place(arrow("down", RED), 18, 20, 0.3)]),
    "112": ("323", "白地・赤縁のみ（最高速度。実物は数字）", [disc(WHITE), ring(RED)]),
    "113": ("323", "白地・赤縁に可変を示す小さな四角（最高速度可変）",
            [disc(WHITE), ring(RED),
             f'<rect x="24" y="24" width="16" height="16" rx="2" fill="{BLUE}"/>']),
    "114": ("323（区域）", "白地・赤縁を破線の枠で囲む（最高速度・区域）",
            [f'<rect x="4" y="4" width="56" height="56" rx="4" fill="none" stroke="{BLUE}" '
             f'stroke-width="3" stroke-dasharray="6 5"/>',
             disc(WHITE, r=21), ring(RED, r=18, w=5.5)]),

    # ---- 一時停止・信号 ----
    "63": ("330", "赤地の逆三角形（一時停止）", tri_down(RED, WHITE, 4)),
    "98": ("信号機", "3灯の信号機",
           [f'<g transform="translate(2 0) scale(0.9)">{picto_signal()}</g>']),
    "92": ("路面標示", "路面に太い白線（停止線）", marking(mark_stopline(1))),
    "93": ("路面標示", "路面に白線2本（二段停止線）", marking(mark_stopline(2))),

    # ---- 駐車・停車 ----
    "65": ("315", "青地・赤縁に赤の×（駐停車禁止）", no_parking(cross())),
    "115": ("316", "青地・赤縁に赤の斜線（駐車禁止）", no_parking(slash())),
    "69": ("316＋504", "駐車禁止に白の余地の帯（駐車余地）",
           no_parking(slash()) + [f'<rect x="18" y="46" width="28" height="6" rx="2" '
                                  f'fill="{WHITE}"/>']),
    "70": ("403", "青の四角に P（駐車可）", instruct(picto_p(), 0.42)),
    "71": ("404", "青の四角に P と下線（停車可。実物は「停」の文字）",
           instruct(picto_p(), 0.36) + [f'<rect x="20" y="48" width="24" height="5" rx="2" '
                                        f'fill="{WHITE}"/>']),
    "72": ("318", "青地に P と時計（時間制限駐車区間）",
           blue_circle() + [place(picto_p(), 6, 12, 0.3), place(picto_clock(), 30, 26, 0.2)]),
    "100": ("403の2", "P と標章の菱形（高齢運転者等標章自動車駐車可）",
            instruct(picto_p(), 0.38) + [place(picto_clover(), 34, 30, 0.26)]),
    "101": ("404の2", "P と標章の菱形と下線（高齢運転者等標章自動車停車可）",
            instruct(picto_p(), 0.34) + [place(picto_clover(), 34, 26, 0.24),
                                         f'<rect x="16" y="50" width="22" height="4" rx="2" '
                                         f'fill="{WHITE}"/>']),
    "102": ("318", "P と時計と標章の菱形（高齢運転者等専用時間制限駐車区間）",
            blue_circle() + [place(picto_p(), 6, 8, 0.3), place(picto_clock(), 30, 22, 0.2),
                             place(picto_clover(), 8, 34, 0.2)]),
    "116": ("路面標示", "路面に駐車枠（駐車方法の指定）", marking(mark_parking_bay())),
    "117": ("路面標示", "路面の端に白線（路側帯）", marking(mark_roadside())),

    # ---- 通行帯・中央線 ----
    "15": ("路面標示", "路面に黄の中央線", marking([mark_line(YELLOW)])),
    "16": ("路面標示", "折れた黄の中央線（中央線の変移）", marking(mark_shift())),
    "17": ("路面標示", "黄の実線（追越しのための右側部分はみ出し通行禁止）",
           marking([mark_line(YELLOW), mark_line(YELLOW, x=38)])),
    "20": ("路面標示", "路面に白の破線2本（車両通行帯）", marking(mark_lines([22, 42]))),
    "21": ("路面標示", "通行帯の線と矢印（車両通行区分）",
           marking(mark_lines([18, 46]), mark_arrows_lane(1))),
    "24": ("路面標示", "通行帯にバス（路線バス等優先通行帯）",
           marking(mark_lines([16, 48]), [f'<g transform="translate(14 18) scale(0.34)">'
                                          f'{picto_bus()}</g>'])),
    "52": ("路面標示", "白の実線をまたぐ矢印に赤の斜線（進路変更禁止）",
           marking([mark_line(WHITE, dashed=False)],
                   [f'<g transform="translate(4 14) scale(0.46)">{arrow("right")}</g>'],
                   [slash()])),
    "107": ("路面標示", "通行帯の線と複数の矢印（車両通行帯及び車両通行区分）",
            marking(mark_lines([10, 54]), mark_arrows_lane())),
    "110": ("路面標示", "通行帯に自転車（普通自転車専用通行帯）",
            marking(mark_lines([16, 48]), [f'<g transform="translate(14 18) scale(0.34)">'
                                           f'{picto_bike()}</g>'])),
    "111": ("路面標示", "通行帯に自動車（専用通行帯）",
            marking(mark_lines([16, 48]), [f'<g transform="translate(14 18) scale(0.34)">'
                                           f'{picto_car()}</g>'])),
    "118": ("路面標示", "通行帯の線と矢印（車両通行帯及び進行方向別通行区分）",
            marking(mark_lines([10, 54]), mark_arrows_lane())),
    "119": ("路面標示", "白の実線と矢印（通行帯・進行方向別通行区分・進路変更禁止）",
            marking([mark_line(WHITE, dashed=False, x=10), mark_line(WHITE, dashed=False, x=54)],
                    mark_arrows_lane())),

    # ---- 自転車・歩行者 ----
    "81": ("325の3", "青の円に自転車と歩道の線（普通自転車歩道通行可）",
           blue_circle() + [place(picto_bike(), 12, 16, 0.28),
                            f'<line x1="18" y1="46" x2="46" y2="46" stroke="{WHITE}" '
                            f'stroke-width="3"/>']),
    "82": ("路面標示", "路面に自転車と区分線（普通自転車の歩道通行部分）",
           marking([mark_line(WHITE, dashed=False, x=44)],
                   [f'<g transform="translate(2 20) scale(0.3)">{picto_bike()}</g>'])),
    "83": ("路面標示", "自転車に赤の斜線（普通自転車の交差点進入禁止）",
           blue_square() + [place(picto_bike(), 8, 16, 0.3)] + [slash()]),
    "84": ("401", "青の四角に自転車2台（並進可）",
           blue_square() + [place(picto_bike(), 4, 12, 0.24), place(picto_bike(), 30, 30, 0.24)]),
    "85": ("407", "青の五角形に歩行者と横断の縞（横断歩道）",
           blue_pentagon() + [place(picto_ped(), 0, 6, 0.44),
                              f'<g opacity="0.95"><rect x="14" y="48" width="4" height="8" '
                              f'fill="{WHITE}"/><rect x="22" y="48" width="4" height="8" '
                              f'fill="{WHITE}"/><rect x="30" y="48" width="4" height="8" '
                              f'fill="{WHITE}"/><rect x="38" y="48" width="4" height="8" '
                              f'fill="{WHITE}"/><rect x="46" y="48" width="4" height="8" '
                              f'fill="{WHITE}"/></g>']),
    "86": ("路面標示", "斜めの横断の縞（斜め横断可）", marking(mark_crosswalk(diagonal=True))),
    "87": ("407の2", "青の五角形に自転車（自転車横断帯）",
           blue_pentagon() + [place(picto_bike(), 8, 14, 0.3)]),
    "27": ("402", "青の四角に自動車と軌道（軌道敷内通行可）",
           blue_square() + [place(picto_car(), 8, 12, 0.28),
                            f'<line x1="10" y1="48" x2="54" y2="48" stroke="{WHITE}" '
                            f'stroke-width="4"/>']),
    "91": ("路面標示", "路面電車とホーム（路面電車停留場）", marking(mark_platform())),

    # ---- 優先・その他 ----
    "54": ("405", "青の四角に太い縦の道（優先道路）",
           instruct(picto_priority_road(), 0.66)),
    "62": ("405", "青の四角に前方で交わる道（前方優先道路）",
           instruct(picto_ahead_priority(), 0.56)),
    "64": ("路面標示", "青の四角に本線と合流（優先本線車道）",
           blue_square() + [f'<rect x="28" y="8" width="8" height="48" fill="{WHITE}"/>',
                            f'<path d="M46 52 L36 34" stroke="{WHITE}" stroke-width="6"/>']),
    "77": ("328", "青地に警笛の山形（警笛鳴らせ及び警笛区間）", designate(picto_horn(), 0.3)),
    "88": ("408", "青の四角に白の山形（安全地帯）",
           blue_square() + [f'<path d="M16 22 L48 22 L32 46 Z" fill="{WHITE}"/>']),
}

# 表4 の名称だけでは意匠を決められないコードは無い（すべて上で定義する）。


def main() -> None:
    with CODES.open(encoding="utf-8") as f:
        codes = [r for r in csv.DictReader(f)]
    valid = {r["code"] for r in codes if r["status"] == "valid"}

    missing = sorted(valid - set(DESIGNS) - {r["code"] for r in refs()}, key=int)
    extra = sorted(set(DESIGNS) - valid, key=int)
    if missing or extra:
        raise SystemExit(f"意匠が未定義: {missing} / 有効コードに無い定義: {extra}")

    ICONS.mkdir(exist_ok=True)
    for stale in ICONS.glob("*.svg"):
        stale.unlink()

    # 対応する道路標識があるものは、その図案(signs/)を使う。DESIGNS より優先する。
    from_signs = import_signs()

    hand = [c for c in sorted(DESIGNS, key=int) if c not in from_signs]
    for code in hand:
        _ref, _desc, parts = DESIGNS[code]
        # 斜縞は路面の外にはみ出すのでクリップを付ける
        needs_clip = 'clip-path="url(#c)"' in "".join(parts)
        (ICONS / f"{code}.svg").write_text(svg(parts, clip=needs_clip), encoding="utf-8")

    made = from_signs | set(hand)
    if made != valid:
        raise SystemExit(f"作れていないコード: {sorted(valid - made, key=int)}")
    print(f"アイコン {len(made)} 個: 標識の図案 {len(from_signs)} / 自作 {len(hand)}")
    print(f"自作のコード: {' '.join(hand)}")


if __name__ == "__main__":
    main()
