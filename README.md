# jartic-regulation-sprite

日本道路交通情報センター（JARTIC）が公開している[交通規制情報](https://www.jartic.or.jp/service/opendata/)の
**共通規制種別コードごとのアイコン**を、MapLibre 向けスプライトとして配信します。

[jartic-traffic-regulation-converter](https://github.com/shiwaku/jartic-traffic-regulation-converter)
が作る PMTiles には、各フィーチャに共通規制種別コード（属性 `code`）が入っています。
このスプライトはそのコードをそのままアイコン名にしているので、地図側は次の1行で引けます。

```js
'icon-image': ['concat', 'reg:', ['get', 'code']]
```

## 配信URL

```
https://shiwaku.github.io/jartic-regulation-sprite/sprite      // .json / .png
https://shiwaku.github.io/jartic-regulation-sprite/sprite@2x   // .json / .png
```

アイコンの一覧は [配信サイトのトップページ](https://shiwaku.github.io/jartic-regulation-sprite/)
で見られます（`tools/gen_site.py` が生成）。個別のアイコンは
`icons/<コード>.svg`（例 `.../icons/63.svg`）でも取得できます。

## 使い方

MapLibre のスタイルに**もう1本のスプライトとして**足します。既存のスプライトを
置き換えるのではなく、`sprite` を配列にして id を付けます。

```js
style.sprite = [
  { id: 'default', url: '既存のスプライトのURL' },  // 既存の参照はそのまま動く
  { id: 'reg', url: 'https://shiwaku.github.io/jartic-regulation-sprite/sprite' },
]
```

**`id` が `default` のスプライトはプレフィックス無しで参照できます。** 背景地図の
スタイル（地理院の最適化ベクトルタイルなど）が持つ `icon-image` を書き換えずに、
規制のアイコンだけを `reg:` 付きで足せます。

```js
map.addLayer({
  id: 'reg-icon',
  type: 'symbol',
  source: 'reg',
  'source-layer': 'stop',
  minzoom: 13,
  layout: {
    'icon-image': ['concat', 'reg:', ['get', 'code']],
    'icon-size': 0.34,
    'icon-allow-overlap': false,
  },
})
```

密度の高いデータなので、`icon-allow-overlap` は `false` のままにして
衝突判定に間引かせるのが前提の設計です。

## 収録内容

| 項目 | 内容 |
|---|---|
| アイコン数 | 73（仕様書 表4 の有効な共通規制種別コードすべて） |
| 大きさ | 64×64（`@2x` は 128×128） |
| 形式 | SVG から生成した PNG スプライト |

コードの一覧は [`data/codes.csv`](data/codes.csv)、どのコードにどんな絵を当てたかは
[`docs/icon-list.md`](docs/icon-list.md)、意匠の考え方は
[`docs/design-spec.md`](docs/design-spec.md) にあります。

**規制種別は「103種」ではなく73種です。** 仕様書
[拡張版標準フォーマット k_2.1](https://www.jartic.or.jp/d/opendata/typeD_kisei_73_k_2.1.pdf)
の表4 は82行あり、そのうち9行（18・25・26・89・95・96・97・103・109）は「未使用」と
書かれています。ファイル名の `kisei_73` がこの73と一致します。
2026年6月の実データに現れたのは69種でした（有効なのに出ないのは
`10 高さ制限`・`84 並進可`・`101 高齢運転者等標章自動車停車可`・
`102 高齢運転者等専用時間制限駐車区間`）。

## アイコンの出所

**対応する道路標識があるものは、標識令で定められた図案をそのまま使っています。**
地図の上で「見慣れた標識」であることを優先しました。

| 出所 | 数 | 内容 |
|---|---|---|
| 標識令の図案 | 44 | 「道路標識、区画線及び道路標示に関する命令」別表第二の図案（`signs/`）を 64×64 に正規化 |
| 独自作図 | 29 | 標識が無いもの（道路標示など）、または標識はあるが再現SVGが無いもの |

### 元データ

SVGファイルは
**[Wikimedia Commons の Road signs in Japan](https://commons.wikimedia.org/wiki/Road_signs_in_Japan)**
のコレクションから取り込んでいます。

- **列挙**: Commons API（`list=allimages&aiprefix=Japan_road_sign`）で実在ファイルを全件取得（407件）。
  ファイル名を推測せず、実在するものだけを対象にしています
- **取得**: `https://commons.wikimedia.org/wiki/Special:FilePath/Japan_road_sign_<番号>.svg`
- **記録**: ファイルごとの出所は各アイコン先頭の XML コメントと
  [`data/sign_refs.csv`](data/sign_refs.csv) にあります

**「公式」という言い方は避けています。** 公式なのは*図案*（法令で定められたもの）で、
`signs/` の **SVGファイル自体は政府配布ではありません**（Commons の利用者が図案を
再現したもの、`PD-Japan-exempt`）。政府配布の図は
[e-Gov 法令検索の標識令](https://laws.e-gov.go.jp/law/335M50004002003)にありますが、
別表第二の図は **JPEG のラスタ画像**（`pict/S35F03102010003-*.jpg`）なので
地図アイコンには使えません。

図案のSVGは文字がすでにパス化されているので、`止まれ`・`50`・`3.3m`・`通行止`
といった文字もそのまま入り、ラスタライズ時にフォントを必要としません。
取り込みは `width` / `height` を 64 にするだけで、**パスには手を入れません**。

### 網羅性

**e-Gov の法令データから別表第二（標識の一覧）を抽出し、Commons の実在ファイル全件と
突き合わせて確かめました。** 使える図案はすべて使っています。

独自作図が残るのは次の2つの理由で、コードごとの根拠は
[`data/handdrawn_reasons.csv`](data/handdrawn_reasons.csv) にあります。

| 理由 | 数 | 例 |
|---|---|---|
| 別表第二に標識があるが Commons に再現SVGが無い | 8 | `92` 停止線（406の2）、`111` 専用通行帯（327の4）、`110` 普通自転車専用通行帯（327の4の2）、`24` 路線バス等優先通行帯（327の5）、`21` 車両通行区分（327）、`70` 駐車可（403）、`116` 駐車方法の指定（327の11〜13） |
| そもそも標識が無い（道路標示・標示板で規定、または JARTIC 独自の組合せ） | 21 | 停止線以外の路面標示、信号機、通行帯の組合せ |

この突き合わせで、`100` 高齢運転者等標章自動車駐車可 に **停車可（403の2）の図案を
当てていた誤り**が見つかって直しました（正しくは 402の2）。あわせて `101` 停車可も
図案に置き換えました。

### 取り込みが崩れていないか確かめる

```bash
npm run compare              # icons/ と signs/ を並べ、色の構成を比べる
npm run compare -- --strict  # ずれていたら異常終了する
```

比較画像は `.cache/compare.png`。どちらもリポジトリ内にあるのでネットワークは使いません。

## 作り直す

```bash
npm install
npm run icons     # signs/ の取り込み＋独自作図分の生成で icons/*.svg を作る
npm run verify    # コード表・SVG・スプライトの整合を見る
npm run bounds    # 独自作図が枠や台紙からはみ出していないか調べる
npm run compare   # 標識令の図案と並べて突き合わせる
npm run docs      # docs/icon-list.md を作り直す
npm run build     # _site/sprite{,@2x}.{png,json} を作る
npm start         # ビルドしてローカルで配信（http://localhost:8080）
```

依存は Python 3.12 標準ライブラリと [@unvt/sprite-one](https://github.com/unvt/sprite-one) だけです。
`icons/*.svg` は生成物ですがリポジトリに入れています（差分が見えるように）。
CI は `npm run icons` を回して**コミットされた SVG と生成結果が一致するか**を確かめ、
`npm run compare -- --strict` で標識令の図案との一致、
`npm run bounds -- --strict` ではみ出しも見ます。

実データでの件数を一覧に載せるには、変換器のリポジトリを隣に置いて次を実行します。

```bash
python tools/pull_counts.py   # ../jartic-traffic-regulation-converter/data/parse_report.json を読む
```

## 出典

- 交通規制種別コード: [公益財団法人 日本道路交通情報センター（JARTIC）](https://www.jartic.or.jp/service/opendata/) 拡張版標準フォーマット k_2.1 表4
- 標識の意匠: 道路標識、区画線及び道路標示に関する命令 別表第二

## 関連

- [jartic-traffic-regulation-converter](https://github.com/shiwaku/jartic-traffic-regulation-converter) — このスプライトを使う交通規制情報の変換器とビューワ
- [dm-sprite](https://github.com/shiwaku/dm-sprite) — 公共測量標準図式の地図記号のスプライト。作りはこれに倣っています

## ライセンス

**ツール類・独自作図のアイコン**: MIT License（[LICENSE](LICENSE)）。

**標識令の図案にもとづくアイコン（`signs/` とそれに由来する `icons/*.svg`）**:
著作権の対象外。道路標識の図案は「道路標識、区画線及び道路標示に関する命令」別表第二で
定められた法令の図案であり、著作権法13条により著作権の対象になりません。
ファイルは [Wikimedia Commons](https://commons.wikimedia.org/wiki/Road_signs_in_Japan)
（`PD-Japan-exempt`）から取り込んだ再現SVGで、各アイコンの先頭に取得元をコメントで
書いています。対応表は [`data/sign_refs.csv`](data/sign_refs.csv)。

生成物のスプライト（`sprite.png` / `sprite.json`）は両方を含みます。
