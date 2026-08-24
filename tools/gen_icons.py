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
    BLUE, RED, ROAD, WHITE, YELLOW,
    arrow, arrow_ring, arrow_turn, arrow_uturn, arrows_lane, arrows_pass,
    arrows_two_step, bar_h, blue_circle, blue_circle_red_ring, blue_pentagon,
    blue_rect, blue_square, centered, cross, disc, mark_box_cross, mark_crosswalk,
    mark_arrow_fan, mark_arrow_l, mark_bike_entry_bar, mark_diagonal_crossing,
    mark_keepout, mark_line, mark_lines, mark_no_stop_area, mark_parking_bay,
    mark_roadside, mark_tram_stop, mark_turn_path,
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
REASONS = ROOT / "data" / "handdrawn_reasons.csv"

# 手描き分の出所ラベル。handdrawn_reasons.csv の basis_kind から引く。
# 「独自作図」と一括りにすると、25コードが別表第六の実物の図を参照している
# 事実が伝わらないため、根拠の種類で呼び分ける。
BASIS_LABEL = {
    "marking": "道路標示の図にもとづく作図",
    "sign": "標識の図案にもとづく作図",
    "none": "対応する標識・標示なし（独自）",
}


def handdrawn_reasons() -> dict[str, dict[str, str]]:
    """handdrawn_reasons.csv を code → 行 の辞書で返す。"""
    with REASONS.open(encoding="utf-8") as f:
        return {r["code"]: r for r in csv.DictReader(f)}


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


def lane_vehicle(picto: str, dashed: bool = True) -> list[str]:
    """通行帯の線＋乗り物。

    線は端（x=9・55）に寄せ、乗り物は路面色の下敷きの上に大きく置く。
    線と乗り物が触れて別の形（Hなど）に見えるのを、下敷きの余白で防ぐ。
    破線/実線の区別が全高で見えるよう、下敷きは線に届かない幅にする。
    """
    return marking(
        mark_lines([9, 55], dashed=dashed),
        [f'<rect x="12.5" y="17" width="39" height="30" rx="4" fill="{ROAD}"/>',
         f'<g transform="translate(14 21.2) scale(0.36)">{picto}</g>'])


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
    "19": ("標示106", "角丸の輪郭の中を斜縞で埋める（立入り禁止部分）", marking(mark_keepout())),
    "76": ("標示107", "枠の内側に短い斜線を並べる（停止禁止部分）", marking(mark_no_stop_area())),
    "90": ("路面標示", "斜縞（導流帯）", marking(mark_zebra())),

    # ---- 一方通行・方向 ----
    "11": ("326-A", "横長の青地に白の矢印（一方通行）",
           blue_rect() + [place(arrow("right"), 12, 12, 0.4)]),
    "12": ("311", "青地に白の直進矢印（指定方向外進行禁止）", designate(arrow("up"), 0.34)),
    "60": ("標示204", "路面に白の矢印（進行方向）", marking(mark_arrow_l(("up",)))),
    "50": ("312", "右折矢印に赤の斜線（車両横断禁止）", prohibit(arrow_turn("right", BLUE), scale=0.40)),
    "51": ("313", "転回矢印に赤の斜線（転回禁止）", prohibit(arrow_uturn(BLUE), scale=0.40)),
    "53": ("314", "2本の矢印に赤の斜線（追越し禁止）", prohibit(arrows_pass(BLUE), scale=0.42)),
    "55": ("327の8", "青の円に二段階の軌跡（原付の右折方法・二段階）",
           designate(arrows_two_step(), 0.34)),
    "56": ("327の9", "白地・赤縁に右折矢印（原付の右折方法・小回り）",
           [disc(WHITE), ring(RED), centered(arrow_turn("right", BLUE), 0.34)]),
    "57": ("標示111", "交差点内を曲がる軌跡の矢印（右左折の方法）",
           marking(mark_turn_path())),
    "58": ("標示110", "軸にかえしが付いたL字の矢印（進行方向別通行区分）",
           marking(mark_arrow_l())),
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
    "98": ("信号機", "3灯の信号機", [centered(picto_signal(), 0.8)]),
    "92": ("標示203", "路面に太い白線1本（停止線）",
           marking([f'<rect x="9" y="34" width="46" height="8" rx="1" fill="{WHITE}"/>'])),
    "93": ("標示203の2", "路面に白線2本（二段停止線）",
           marking([f'<rect x="9" y="24" width="46" height="7" rx="1" fill="{WHITE}"/>',
                    f'<rect x="9" y="42" width="46" height="7" rx="1" fill="{WHITE}"/>'])),

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
            blue_circle() + [place(picto_p(), 10, 12, 0.28),
                             place(picto_clock(), 30, 22, 0.2),
                             place(picto_clover(), 9, 34, 0.19)]),
    "116": ("路面標示", "路面に駐車枠（駐車方法の指定）", marking(mark_parking_bay())),
    "117": ("路面標示", "路面の端に白線（路側帯）", marking(mark_roadside())),

    # ---- 通行帯・中央線 ----
    "15": ("標示205", "路面に白の中央線", marking([mark_line(WHITE, dashed=False)])),
    "16": ("標示205", "折れた白の中央線（中央線の変移）。折れが読めるよう太く・横ずれを大きく",
           marking([f'<path d="M18 4 L18 22 L46 36 L46 60" fill="none" stroke="{WHITE}" '
                    f'stroke-width="7"/>'])),
    "17": ("標示102", "中央に黄の実線1本（追越しのための右側部分はみ出し通行禁止）",
           marking([mark_line(YELLOW, dashed=False)])),
    "20": ("路面標示", "路面に白の破線2本（車両通行帯）", marking(mark_lines([22, 42]))),
    "21": ("路面標示", "通行帯の線と自動車（車両通行区分＝車種で分ける。実物は文字）",
           lane_vehicle(picto_car(bg=ROAD))),
    "24": ("路面標示", "破線の通行帯にバス（路線バス等優先通行帯。実物は文字）",
           lane_vehicle(picto_bus(bg=ROAD))),
    "52": ("標示102の2", "車線境界に黄の実線（進路変更禁止。道路標示に赤は使わない）",
           marking([mark_line(YELLOW, dashed=False, x=22),
                    mark_line(YELLOW, dashed=False, x=42)])),
    "107": ("路面標示", "通行帯の線と自動車と直進の矢印（車両通行帯及び車両通行区分）",
            marking(mark_lines([9, 55]),
                    [f'<rect x="14" y="4" width="36" height="22" rx="4" fill="{ROAD}"/>',
                     f'<g transform="translate(18 6) scale(0.28)">{picto_car(bg=ROAD)}</g>'],
                    mark_arrow_fan(("up",)))),
    "110": ("路面標示", "破線の通行帯に自転車（普通自転車専用通行帯。実物は文字）",
            lane_vehicle(picto_bike())),
    "111": ("路面標示", "実線の通行帯にバス（専用通行帯。専用は実線で区切る。実物は文字）",
            lane_vehicle(picto_bus(bg=ROAD), dashed=False)),
    "118": ("路面標示", "破線の通行帯と左右のL字矢印（車両通行帯及び進行方向別通行区分）",
            marking(mark_lines([9, 55]), mark_arrow_l(("left", "right")))),
    "119": ("路面標示", "実線の通行帯と左右のL字矢印（通行帯・進行方向別通行区分・進路変更禁止）",
            marking(mark_lines([9, 55], dashed=False), mark_arrow_l(("left", "right")))),

    # ---- 自転車・歩行者 ----
    "81": ("325の3", "青の円に自転車と歩道の線（普通自転車歩道通行可）",
           blue_circle() + [place(picto_bike(), 12, 16, 0.28),
                            f'<line x1="18" y1="46" x2="46" y2="46" stroke="{WHITE}" '
                            f'stroke-width="3"/>']),
    "82": ("路面標示", "路面に自転車と区分線（普通自転車の歩道通行部分）",
           marking([mark_line(WHITE, dashed=False, x=44)],
                   [f'<g transform="translate(4 20) scale(0.3)">{picto_bike()}</g>'])),
    "83": ("標示114の4", "自転車と進入を塞ぐ横棒（普通自転車の交差点進入禁止）",
           marking(mark_bike_entry_bar())),
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
    "86": ("標示201の2", "交差点の四隅を斜めに横断する縞（斜め横断可）",
           marking(mark_diagonal_crossing())),
    "87": ("407の2", "青の五角形に自転車（自転車横断帯）",
           blue_pentagon() + [place(picto_bike(), 8, 14, 0.3)]),
    "27": ("402", "青の四角に自動車と軌道（軌道敷内通行可）",
           blue_square() + [place(picto_car(), 8, 12, 0.28),
                            f'<line x1="10" y1="48" x2="54" y2="48" stroke="{WHITE}" '
                            f'stroke-width="4"/>']),
    "91": ("標示209", "軌道の脇に細長い島（路面電車停留場）", marking(mark_tram_stop())),

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
