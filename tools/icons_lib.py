# -*- coding: utf-8 -*-
"""アイコンを組み立てる部品。

64×64 の中に「標識・標示の家族」が読み取れる形を置く。地図上では 20〜24px で
描かれるため、実物の意匠をそのまま縮小しても潰れる。そこで

  形と色で家族を示し（禁止=赤リング / 指定・専用=青地 / 指示=青四角 /
  路面標示=灰の路面に白線）、中の図形で種別を分ける

という方針にしている。詳しくは docs/design-spec.md。

**文字は使わない。** ラスタライズ時のフォントに依存して再現しなくなるため、
実物が文字で表す種別（最高速度の数字、停車可の「停」など）は幾何図形で置き換える。
"""
from __future__ import annotations

# 標識令の色に近い値（Wikimedia Commons の標識SVGで使われている値に合わせた）
RED = "#ED1C23"
BLUE = "#0066B3"
WHITE = "#FFFFFF"
BLACK = "#1F2328"
YELLOW = "#F2C200"
ROAD = "#8A9199"
ROAD_DARK = "#6E757D"
GREEN = "#2E8B41"
AMBER = "#F5A623"

SIZE = 64
C = SIZE / 2  # 中心

# ---- 台紙 ------------------------------------------------------------------


def disc(fill: str, r: float = 27, cx: float = C, cy: float = C) -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'


def ring(color: str = RED, r: float = 23.5, w: float = 7) -> str:
    return f'<circle cx="{C}" cy="{C}" r="{r}" fill="none" stroke="{color}" stroke-width="{w}"/>'


def white_circle_red_ring() -> list[str]:
    """禁止標識の台紙。白地に赤の縁。"""
    return [disc(WHITE), ring(RED)]


def blue_circle() -> list[str]:
    """指定・専用の台紙。青地。"""
    return [disc(BLUE)]


def blue_circle_red_ring() -> list[str]:
    """駐車・駐停車禁止の台紙。青地に赤の縁。"""
    return [disc(BLUE), ring(RED)]


def blue_square() -> list[str]:
    """指示標識の台紙。角を丸めた青の正方形。"""
    return [f'<rect x="5" y="5" width="54" height="54" rx="5" fill="{BLUE}"/>']


def white_square_red_border() -> list[str]:
    """歩行者向けの禁止標識の台紙。白地・赤枠の正方形（331・332）。"""
    return [
        f'<rect x="4" y="4" width="56" height="56" rx="4" fill="{WHITE}"/>',
        f'<rect x="7.5" y="7.5" width="49" height="49" rx="3" fill="none" '
        f'stroke="{RED}" stroke-width="7"/>',
    ]


def blue_rect() -> list[str]:
    """一方通行の台紙。横長の青。"""
    return [f'<rect x="3" y="18" width="58" height="28" rx="3" fill="{BLUE}"/>']


def blue_pentagon() -> list[str]:
    """横断歩道の台紙。上が尖った五角形（実物は家型）。"""
    return [f'<path d="M32 3 L59 22 L52 60 L12 60 L5 22 Z" fill="{BLUE}"/>']


def tri_down(fill: str, stroke: str, w: float = 6) -> list[str]:
    """一時停止・徐行の台紙。逆三角形。"""
    return [
        f'<path d="M4 12 L60 12 L32 58 Z" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{w}" stroke-linejoin="round"/>'
    ]


def road(dark: bool = False) -> list[str]:
    """路面標示の台紙。アスファルト。"""
    return [f'<rect x="3" y="3" width="58" height="58" rx="4" fill="{ROAD_DARK if dark else ROAD}"/>']


# ---- 禁止の記号 ------------------------------------------------------------


def slash(color: str = RED, w: float = 6) -> str:
    """左上から右下への赤い斜線（1本）。"""
    return (
        f'<line x1="13" y1="13" x2="51" y2="51" stroke="{color}" '
        f'stroke-width="{w}" stroke-linecap="round"/>'
    )


def cross(color: str = RED, w: float = 6) -> str:
    """赤い×（通行止め・駐停車禁止）。"""
    return (
        f'<line x1="13" y1="13" x2="51" y2="51" stroke="{color}" stroke-width="{w}" '
        f'stroke-linecap="round"/>'
        f'<line x1="51" y1="13" x2="13" y2="51" stroke="{color}" stroke-width="{w}" '
        f'stroke-linecap="round"/>'
    )


def bar_h(fill: str = WHITE) -> str:
    """車両進入禁止の白い横棒。"""
    return f'<rect x="12" y="27" width="40" height="10" rx="1.5" fill="{fill}"/>'


# ---- 図形の配置 ------------------------------------------------------------


def place(body: str, tx: float, ty: float, scale: float) -> str:
    """100×60 の箱で描いた図形を、指定位置・倍率に置く。"""
    return f'<g transform="translate({tx} {ty}) scale({scale})">{body}</g>'


def centered(body: str, scale: float = 0.34, dy: float = 0) -> str:
    """100×60 の箱の図形を中央に置く。"""
    return place(body, C - 50 * scale, C - 30 * scale + dy, scale)


# ---- 乗り物・人（100×60 の箱で描く） --------------------------------------


def picto_car(fill: str = WHITE, bg: str | None = None) -> str:
    """乗用車の側面。bg を渡すと窓を抜いて、小さくてもキャビンの段が読めるようにする。"""
    out = (
        f'<path d="M4 46 L6 34 C7 30 10 28 14 28 L26 28 L38 12 C40 9 43 8 47 8 L64 8 '
        f'C68 8 71 10 73 13 L82 28 L90 28 C93 28 95 30 96 34 L96 46 Z" fill="{fill}"/>'
        f'<circle cx="26" cy="48" r="9" fill="{fill}"/>'
        f'<circle cx="76" cy="48" r="9" fill="{fill}"/>'
    )
    if bg:
        out += f'<path d="M44 14 L62 14 C64 14 66 15 67 17 L72 26 L40 26 Z" fill="{bg}"/>'
    return out


def picto_truck(fill: str = WHITE) -> str:
    return (
        f'<path d="M4 18 L58 18 L58 44 L4 44 Z" fill="{fill}"/>'
        f'<path d="M62 26 L80 26 L94 38 L94 44 L62 44 Z" fill="{fill}"/>'
        f'<circle cx="24" cy="46" r="8" fill="{fill}"/>'
        f'<circle cx="78" cy="46" r="8" fill="{fill}"/>'
    )


def picto_bus(fill: str = WHITE, bg: str | None = None) -> str:
    """バスの側面。bg を渡すと窓の列を抜いて、ただの長方形（棒）に見えないようにする。"""
    out = (
        f'<rect x="4" y="8" width="92" height="38" rx="5" fill="{fill}"/>'
        f'<circle cx="24" cy="50" r="9" fill="{fill}"/>'
        f'<circle cx="76" cy="50" r="9" fill="{fill}"/>'
    )
    if bg:
        out += (
            f'<rect x="12" y="15" width="16" height="12" rx="2" fill="{bg}"/>'
            f'<rect x="34" y="15" width="16" height="12" rx="2" fill="{bg}"/>'
            f'<rect x="56" y="15" width="16" height="12" rx="2" fill="{bg}"/>'
            f'<rect x="78" y="15" width="11" height="12" rx="2" fill="{bg}"/>'
        )
    return out


def picto_moto(fill: str = WHITE) -> str:
    return (
        f'<circle cx="20" cy="40" r="13" fill="none" stroke="{fill}" stroke-width="6"/>'
        f'<circle cx="80" cy="40" r="13" fill="none" stroke="{fill}" stroke-width="6"/>'
        f'<path d="M20 40 L44 22 L62 22 L80 40" fill="none" stroke="{fill}" '
        f'stroke-width="7" stroke-linejoin="round"/>'
        f'<circle cx="52" cy="10" r="8" fill="{fill}"/>'
    )


def picto_bike(fill: str = WHITE) -> str:
    """自転車の側面。小さくても「輪が2つ」で読めるよう、車輪を太いリングにする。"""
    return (
        f'<circle cx="21" cy="40" r="15" fill="none" stroke="{fill}" stroke-width="7"/>'
        f'<circle cx="79" cy="40" r="15" fill="none" stroke="{fill}" stroke-width="7"/>'
        f'<path d="M21 40 L40 14 L64 14 L79 40" fill="none" stroke="{fill}" '
        f'stroke-width="7" stroke-linejoin="round"/>'
        f'<path d="M40 14 L52 40" fill="none" stroke="{fill}" stroke-width="6"/>'
        f'<path d="M32 8 L46 8 M64 14 L70 4" fill="none" stroke="{fill}" '
        f'stroke-width="5" stroke-linecap="round"/>'
    )


def picto_ped(fill: str = WHITE, x: float = 0) -> str:
    """歩行者。100×60 の箱の中で x だけずらせる。"""
    return (
        f'<g transform="translate({x} 0)">'
        f'<circle cx="50" cy="10" r="8" fill="{fill}"/>'
        f'<path d="M50 20 C58 20 62 26 62 32 L62 40 L56 40 L56 58 L48 58 '
        f'L48 42 L44 58 L36 58 L42 34 L38 40 L34 34 C38 24 44 20 50 20 Z" fill="{fill}"/>'
        f'</g>'
    )


def picto_ped_child(fill: str = WHITE) -> str:
    """大人と子ども（歩行者専用）。"""
    return (
        f'<g transform="translate(-18 0)">{picto_ped(fill)}</g>'
        f'<g transform="translate(30 16) scale(0.62)">{picto_ped(fill)}</g>'
    )


def picto_cart(fill: str = WHITE) -> str:
    """荷車（自転車以外の軽車両）。"""
    return (
        f'<circle cx="34" cy="42" r="15" fill="none" stroke="{fill}" stroke-width="5"/>'
        f'<path d="M34 42 L34 27 L94 14" fill="none" stroke="{fill}" stroke-width="6"/>'
        f'<path d="M20 27 L70 27" stroke="{fill}" stroke-width="6"/>'
    )


def picto_tram(fill: str = WHITE) -> str:
    return (
        f'<path d="M16 12 L84 12 L84 46 L16 46 Z" fill="{fill}"/>'
        f'<path d="M50 12 L50 0" stroke="{fill}" stroke-width="4"/>'
        f'<path d="M6 54 L94 54" stroke="{fill}" stroke-width="5"/>'
    )


def picto_priority_road(fill: str = WHITE) -> str:
    """優先道路（405）。太い縦の道が交差点で広がる形。"""
    return (
        f'<path d="M40 0 L60 0 L60 18 L78 30 L60 42 L60 60 L40 60 L40 42 L22 30 '
        f'L40 18 Z" fill="{fill}"/>'
    )


def picto_ahead_priority(fill: str = WHITE) -> str:
    """前方優先道路。前方の道が優先であることを示す T 字。"""
    return (
        f'<rect x="14" y="10" width="72" height="14" rx="2" fill="{fill}"/>'
        f'<rect x="42" y="24" width="16" height="36" rx="2" fill="{fill}"/>'
    )


def picto_horn(fill: str = WHITE) -> str:
    """警笛。実物は二重の山形。"""
    return (
        f'<path d="M20 8 L44 30 L20 52" fill="none" stroke="{fill}" stroke-width="9" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'<path d="M52 8 L76 30 L52 52" fill="none" stroke="{fill}" stroke-width="9" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )


def picto_p(fill: str = WHITE) -> str:
    """駐車の P。文字ではなく図形として描く。"""
    return (
        f'<path d="M30 4 L58 4 C74 4 84 13 84 26 C84 39 74 47 58 47 L46 47 L46 58 '
        f'L30 58 Z M46 17 L46 34 L57 34 C63 34 67 31 67 26 C67 20 63 17 57 17 Z" '
        f'fill="{fill}" fill-rule="evenodd"/>'
    )


def picto_signal(body: str = BLACK) -> str:
    """信号機。3灯。"""
    return (
        f'<rect x="30" y="0" width="40" height="60" rx="7" fill="{body}"/>'
        f'<circle cx="50" cy="12" r="7" fill="{RED}"/>'
        f'<circle cx="50" cy="30" r="7" fill="{AMBER}"/>'
        f'<circle cx="50" cy="48" r="7" fill="{GREEN}"/>'
    )


def picto_railcross(fill: str = WHITE) -> str:
    """踏切。×と遮断機の棒。"""
    return (
        f'<path d="M22 4 L78 44 M78 4 L22 44" stroke="{fill}" stroke-width="8" '
        f'stroke-linecap="round"/>'
        f'<rect x="6" y="52" width="88" height="7" rx="3" fill="{fill}"/>'
    )


def picto_weight(fill: str = WHITE) -> str:
    """重量制限。上からの荷重。"""
    return (
        f'<path d="M50 2 L50 22 M40 14 L50 24 L60 14" fill="none" stroke="{fill}" '
        f'stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<rect x="18" y="30" width="64" height="14" rx="2" fill="{fill}"/>'
        f'<circle cx="34" cy="52" r="6" fill="{fill}"/>'
        f'<circle cx="66" cy="52" r="6" fill="{fill}"/>'
    )


def picto_height(fill: str = WHITE) -> str:
    """高さ制限。上下の矢印と天井。"""
    return (
        f'<rect x="14" y="2" width="72" height="8" rx="2" fill="{fill}"/>'
        f'<path d="M50 16 L50 54 M40 24 L50 14 L60 24 M40 46 L50 56 L60 46" fill="none" '
        f'stroke="{fill}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def picto_clock(fill: str = WHITE) -> str:
    """時間制限。時計。"""
    return (
        f'<circle cx="50" cy="30" r="26" fill="none" stroke="{fill}" stroke-width="6"/>'
        f'<path d="M50 14 L50 32 L64 40" fill="none" stroke="{fill}" stroke-width="6" '
        f'stroke-linecap="round"/>'
    )


def picto_clover(fill: str = WHITE) -> str:
    """高齢運転者標章の代わりの菱形。小さく置くので輪郭だけにする。"""
    return (
        f'<path d="M50 2 L74 30 L50 58 L26 30 Z" fill="none" stroke="{fill}" '
        f'stroke-width="9"/>'
    )


# ---- 矢印 ------------------------------------------------------------------


def arrow(direction: str = "up", fill: str = WHITE) -> str:
    """まっすぐな矢印。direction は up/down/left/right。"""
    body = (
        f'<path d="M50 2 L74 30 L60 30 L60 58 L40 58 L40 30 L26 30 Z" fill="{fill}"/>'
    )
    rot = {"up": 0, "right": 90, "down": 180, "left": 270}[direction]
    # transform-origin はラスタライザによって解釈が違うので、回転の中心を直接書く
    return f'<g transform="rotate({rot} 50 30)">{body}</g>'


def arrow_turn(side: str = "right", fill: str = WHITE) -> str:
    """右折・左折の矢印（根元から曲がる）。"""
    flip = -1 if side == "left" else 1
    return (
        f'<g transform="translate(50 0) scale({flip} 1) translate(-50 0)">'
        f'<path d="M40 58 L40 30 C40 20 48 14 58 14 L64 14 L64 2 L92 22 L64 42 '
        f'L64 30 L60 30 C58 30 58 32 58 34 L58 58 Z" fill="{fill}"/>'
        f'</g>'
    )


def arrow_uturn(fill: str = WHITE) -> str:
    return (
        f'<path d="M30 58 L30 24 C30 12 40 4 52 4 C64 4 74 12 74 24 L74 34 L86 34 '
        f'L66 56 L46 34 L58 34 L58 24 C58 20 56 18 52 18 C48 18 46 20 46 24 L46 58 Z" '
        f'fill="{fill}"/>'
    )


def arrow_ring(fill: str = WHITE) -> str:
    """環状交差点の右回り。実物は円を描く3本の矢印。"""
    out = []
    for a in (0, 120, 240):
        out.append(
            f'<g transform="rotate({a} 50 30)">'
            f'<path d="M50 4 A26 26 0 0 1 72 17" fill="none" stroke="{fill}" '
            f'stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M66 6 L80 20 L62 24 Z" fill="{fill}"/>'
            f'</g>'
        )
    return "".join(out)


def arrows_lane(fill: str = WHITE) -> str:
    """進行方向別通行区分。左折・直進・右折。"""
    return (
        f'<g transform="translate(-30 6) scale(0.52)">{arrow_turn("left", fill)}</g>'
        f'<g transform="translate(0 6) scale(0.52)">{arrow("up", fill)}</g>'
        f'<g transform="translate(30 6) scale(0.52)">{arrow_turn("right", fill)}</g>'
    )


def arrows_pass(fill: str = WHITE) -> str:
    """追越し。前の車を追い越す2本の軌跡。"""
    return (
        f'<path d="M26 58 L26 14 M16 24 L26 12 L36 24" fill="none" stroke="{fill}" '
        f'stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M74 58 L74 34 C74 22 64 14 52 14" fill="none" stroke="{fill}" '
        f'stroke-width="8" stroke-linecap="round"/>'
    )


def arrows_two_step(fill: str = WHITE) -> str:
    """原付の二段階右折。いったん直進して止まり、それから右へ。

    小回り(327の9)と見分けが付くよう、直進の矢印と右向きの矢印を離して置く。
    """
    return (
        f'<path d="M22 58 L22 26 M12 36 L22 24 L32 36" fill="none" stroke="{fill}" '
        f'stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M44 14 L74 14 M64 4 L78 14 L64 24" fill="none" stroke="{fill}" '
        f'stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'
    )


# ---- 路面標示 --------------------------------------------------------------


def mark_stopline(n: int = 1) -> list[str]:
    ys = [40] if n == 1 else [30, 46]
    out = [f'<rect x="9" y="{y}" width="46" height="7" rx="1" fill="{WHITE}"/>' for y in ys]
    return out + [f'<path d="M32 8 L32 24 M25 17 L32 24 L39 17" stroke="{WHITE}" '
                  f'stroke-width="4" fill="none" stroke-linecap="round"/>']


def mark_line(color: str = WHITE, dashed: bool = False, x: float = 32) -> str:
    dash = ' stroke-dasharray="7 6"' if dashed else ''
    return (f'<line x1="{x}" y1="6" x2="{x}" y2="58" stroke="{color}" '
            f'stroke-width="5"{dash}/>')


def mark_lines(xs: list[float], color: str = WHITE, dashed: bool = True) -> list[str]:
    return [mark_line(color, dashed, x) for x in xs]


def mark_shift() -> list[str]:
    """中央線の変移。折れた線。"""
    return [f'<path d="M24 6 L24 24 L40 34 L40 58" fill="none" stroke="{YELLOW}" '
            f'stroke-width="5"/>']


def mark_zebra(frame: bool = False) -> list[str]:
    """導流帯・立入禁止部分の斜縞。frame で外枠を付ける。"""
    out = []
    for i in range(-2, 5):
        x = 8 + i * 11
        out.append(f'<line x1="{x}" y1="54" x2="{x + 26}" y2="8" stroke="{WHITE}" '
                   f'stroke-width="4" clip-path="url(#c)"/>')
    if frame:
        # 枠は縞の上に重ねる（下に描くと縞に埋もれる）
        out.append(f'<rect x="9" y="9" width="46" height="46" fill="none" '
                   f'stroke="{WHITE}" stroke-width="5"/>')
    return out


def mark_box_cross() -> list[str]:
    """停止禁止部分。白枠に×。"""
    return [
        f'<rect x="12" y="12" width="40" height="40" fill="none" stroke="{WHITE}" '
        f'stroke-width="4"/>',
        f'<path d="M16 16 L48 48 M48 16 L16 48" stroke="{WHITE}" stroke-width="4"/>',
    ]


def mark_crosswalk(diagonal: bool = False) -> list[str]:
    """横断歩道の縞。斜めのものは路面からはみ出すのでクリップする。"""
    out = []
    for i in range(6):
        if diagonal:
            x = -8 + i * 12
            out.append(f'<path d="M{x} 54 L{x + 16} 10 L{x + 22} 10 L{x + 6} 54 Z" '
                       f'fill="{WHITE}" clip-path="url(#c)"/>')
        else:
            x = 8 + i * 11
            out.append(f'<rect x="{x}" y="10" width="7" height="44" fill="{WHITE}"/>')
    return out


def mark_arrow_fan(dirs: tuple[str, ...] = ("left", "up", "right"),
                   narrow: bool = False) -> list[str]:
    """路面の進行方向の矢印。塗りで描き、外側の2本は傾ける。

    実物は L 字の矢印だが、20px では折れ目が潰れて読めない。根元から扇状に
    傾けた直線の矢印にすると、小さくても向きが分かる。

    narrow は通行帯の線と併せるとき用。線の間（各車線）に収まるよう、
    間隔を広げて傾きを浅くする。
    """
    H, W, T = (16, 9, 2.4) if narrow else (18, 10, 2.6)

    def arrow(cx: float, base: float, deg: float) -> str:
        body = (
            f'<path d="M{-T} 0 L{-T} {-H + 7} L{-W / 2} {-H + 7} L0 {-H} '
            f'L{W / 2} {-H + 7} L{T} {-H + 7} L{T} 0 Z" fill="{WHITE}"/>'
        )
        return f'<g transform="translate({cx} {base}) rotate({deg})">{body}</g>'

    if narrow:
        lay = {("left", "up", "right"): [(12, -14), (32, 0), (52, 14)]}.get(tuple(dirs))
    else:
        lay = {
            ("up",): [(32, 0)],
            ("left", "right"): [(21, -32), (43, 32)],
            ("left", "up", "right"): [(17, -28), (32, 0), (47, 28)],
        }.get(tuple(dirs))
    if lay is None:
        raise ValueError(f"未対応の組み合わせ: {dirs}")
    return [arrow(cx, 52, deg) for cx, deg in lay]


def mark_roadside() -> list[str]:
    """路側帯。端に寄せた2本の白線。"""
    return [
        f'<line x1="16" y1="6" x2="16" y2="58" stroke="{WHITE}" stroke-width="5"/>',
        f'<line x1="24" y1="6" x2="24" y2="58" stroke="{WHITE}" stroke-width="4"/>',
    ]


def mark_parking_bay() -> list[str]:
    """駐車方法の指定。駐車枠。"""
    return [
        f'<path d="M12 14 L52 14 M12 14 L12 50 M52 14 L52 50" fill="none" '
        f'stroke="{WHITE}" stroke-width="5"/>',
        f'<path d="M12 50 L52 50" stroke="{WHITE}" stroke-width="5" '
        f'stroke-dasharray="6 6"/>',
    ]


def mark_platform() -> list[str]:
    """路面電車停留場。ホーム。"""
    return [
        f'<g transform="translate(0 2) scale(0.5)">{picto_tram(WHITE)}</g>',
        f'<rect x="8" y="46" width="48" height="10" rx="2" fill="{WHITE}"/>',
    ]


# ---- SVG の組み立て --------------------------------------------------------

CLIP = (
    '<defs><clipPath id="c"><rect x="3" y="3" width="58" height="58" rx="4"/>'
    '</clipPath></defs>'
)


def svg(parts: list[str], clip: bool = False) -> str:
    body = "".join(parts)
    defs = CLIP if clip else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" '
        f'viewBox="0 0 {SIZE} {SIZE}">{defs}{body}</svg>'
    )

# ---- 実物の道路標示にもとづく部品 -----------------------------------------
# 別表第六の図（e-Gov の法令データ）を見て形を決めている。
# **道路標示に赤は使わない。** 白（一部黄）だけで描く。


def mark_arrow_l(dirs: tuple[str, ...] = ("left", "up", "right")) -> list[str]:
    """進行方向別通行区分（標示110）。実物どおり、軸に「かえし」が付いたL字の矢印。"""
    def shaft(cx: float, barb: int) -> str:
        # 軸（下から上へ）＋先端の三角＋根元寄りの横向きのかえし
        out = [f'<path d="M{cx - 2.6} 52 L{cx - 2.6} 26 L{cx - 6} 26 L{cx} 18 '
               f'L{cx + 6} 26 L{cx + 2.6} 26 L{cx + 2.6} 52 Z" fill="{WHITE}"/>']
        if barb:
            d = barb  # -1 で左、+1 で右
            x0 = cx + 2.6 * d
            out.append(
                f'<path d="M{x0} 36 L{x0 + 6 * d} 36 L{x0 + 6 * d} 32.5 '
                f'L{x0 + 11 * d} 38.5 L{x0 + 6 * d} 44.5 L{x0 + 6 * d} 41 '
                f'L{x0} 41 Z" fill="{WHITE}"/>'
            )
        return out

    # 2本組は通行帯の線（x=9・55 に置く）とかえしが重ならない位置にする
    lay = {("up",): [(32, 0)],
           ("left", "right"): [(26, -1), (38, 1)],
           ("left", "up", "right"): [(18, -1), (32, 0), (46, 1)]}.get(tuple(dirs))
    if lay is None:
        raise ValueError(f"未対応の組み合わせ: {dirs}")
    return [part for cx, barb in lay for part in shaft(cx, barb)]


def mark_turn_path() -> list[str]:
    """右左折の方法（標示111）。交差点内を曲がる軌跡の矢印。"""
    return [
        # 左へ曲がる軌跡
        f'<path d="M20 56 L20 34 C20 28 24 24 30 24 L34 24 L34 16 L46 27 L34 38 '
        f'L34 31 L31 31 C29 31 28 32 28 34 L28 56 Z" fill="{WHITE}"/>',
        # 交差点であることを示す横の道
        f'<path d="M4 20 L58 20" stroke="{WHITE}" stroke-width="3" '
        f'stroke-dasharray="5 4"/>',
    ]


def mark_keepout() -> list[str]:
    """立入り禁止部分（標示106）。角丸の輪郭の中を斜縞で埋める。"""
    out = [f'<defs><clipPath id="k"><rect x="14" y="8" width="36" height="48" rx="18"/>'
           f'</clipPath></defs>']
    for i in range(-2, 6):
        x = 8 + i * 9
        out.append(f'<line x1="{x}" y1="58" x2="{x + 22}" y2="6" stroke="{WHITE}" '
                   f'stroke-width="4" clip-path="url(#k)"/>')
    out.append(f'<rect x="14" y="8" width="36" height="48" rx="18" fill="none" '
               f'stroke="{WHITE}" stroke-width="3.5"/>')
    return out


def mark_no_stop_area() -> list[str]:
    """停止禁止部分（標示107）。枠の内側に短い斜線を並べる。"""
    out = [f'<rect x="11" y="11" width="42" height="42" fill="none" stroke="{WHITE}" '
           f'stroke-width="3.5"/>']
    for i in range(4):
        y = 17 + i * 10
        out.append(f'<line x1="13" y1="{y + 6}" x2="21" y2="{y}" stroke="{WHITE}" '
                   f'stroke-width="3"/>')
        out.append(f'<line x1="43" y1="{y + 6}" x2="51" y2="{y}" stroke="{WHITE}" '
                   f'stroke-width="3"/>')
    return out


def mark_diagonal_crossing() -> list[str]:
    """斜め横断可（標示201の2）。交差点の四隅を斜めに横断する縞。"""
    bands = []
    for deg in (45, -45):
        for i in range(-1, 2):
            # 帯は中心(32)を軸に等間隔で並べる
            bands.append(
                f'<g transform="rotate({deg} 32 32)">'
                f'<rect x="{29.5 + i * 11}" y="2" width="5" height="60" fill="{WHITE}"/></g>'
            )
    # クリップは回転していない外側の g に掛ける（内側に掛けるとクリップも回る）
    return [f'<g clip-path="url(#c)">{"".join(bands)}</g>']


def mark_tram_stop() -> list[str]:
    """路面電車停留場（標示209）。軌道の脇に細長い島を置く。"""
    return [
        f'<line x1="44" y1="4" x2="44" y2="60" stroke="{WHITE}" stroke-width="3"/>',
        f'<line x1="54" y1="4" x2="54" y2="60" stroke="{WHITE}" stroke-width="3"/>',
        f'<path d="M18 12 L34 12 L34 44 L26 56 L18 56 Z" fill="none" stroke="{WHITE}" '
        f'stroke-width="3.5"/>',
    ]


def mark_bike_entry_bar() -> list[str]:
    """普通自転車の交差点進入禁止（標示114の4）。自転車と進入を塞ぐ横棒。"""
    return [
        f'<g transform="translate(10 26) scale(0.34)">{picto_bike()}</g>',
        f'<rect x="12" y="16" width="40" height="6" rx="1" fill="{WHITE}"/>',
    ]
