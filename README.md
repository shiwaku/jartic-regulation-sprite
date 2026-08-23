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

## アイコンは自作です

**道路標識の画像を取り込んではいません。** 標識令別表第二の意匠を参考に、
地図で 20px 前後に縮めても読めるように描き直したものです。
中の文字（最高速度の数字など）は幾何図形に置き換えています。
理由と対応は [`docs/design-spec.md`](docs/design-spec.md) に書いてあります。

参考にした意匠は
[Wikimedia Commons の道路標識SVG](https://commons.wikimedia.org/wiki/Road_signs_in_Japan)
（著作権法13条により法令の図案は著作権の対象外、`PD-Japan-exempt`）で確認しました。

## 作り直す

```bash
npm install
npm run icons     # data/codes.csv と tools/gen_icons.py から icons/*.svg を作る
npm run verify    # コード表・SVG・スプライトの整合を見る
npm run docs      # docs/icon-list.md を作り直す
npm run build     # _site/sprite{,@2x}.{png,json} を作る
npm start         # ビルドしてローカルで配信（http://localhost:8080）
```

依存は Python 3.12 標準ライブラリと [@unvt/sprite-one](https://github.com/unvt/sprite-one) だけです。
`icons/*.svg` は生成物ですがリポジトリに入れています（差分が見えるように）。
CI は `npm run icons` を回して**コミットされた SVG と生成結果が一致するか**を確かめます。

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

Apache License 2.0（[LICENSE](LICENSE)）。
