// 自作アイコンを公式意匠と突き合わせる。
//
//   node tools/compare-official.mjs          # 比較して結果を出す
//   node tools/compare-official.mjs --strict # ずれがあったら異常終了する
//
// data/official_refs.csv に書いた対応（コード → Wikimedia Commons のファイル名）で
// 標識SVGを取ってきて、自作アイコンと並べた画像と、色の構成の比較表を出す。
// 公式意匠は標識令別表第二にもとづくもので、著作権法13条により著作権の対象外
// （Commons のライセンス表記は PD-Japan-exempt）。取得物は .cache/ に置き、
// リポジトリには含めない。
//
// 「色の構成」は、赤・青・白・灰が占める割合。地の色や縁の色を間違えると大きく動くので、
// **家族（禁止／指定／指示／路面標示）を取り違えていないか**の検査に使える。
// 中の図形の細かい違いは見ない（そもそも実物どおりには描いていない）。

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import sharp from 'sharp'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const CACHE = path.join(ROOT, '.cache', 'official')
const OUT = path.join(ROOT, '.cache', 'compare.png')
const REFS = path.join(ROOT, 'data', 'official_refs.csv')
const UA = 'jartic-regulation-sprite/0.1 (+https://github.com/shiwaku/jartic-regulation-sprite)'
/** これ以上ずれていたら家族を取り違えていると見なす（ポイント）。 */
const THRESHOLD = 30

function readRefs() {
  const lines = fs.readFileSync(REFS, 'utf8').trim().split(/\r?\n/).slice(1)
  return lines.map((l) => {
    const [code, file, ref, expect] = l.split(',')
    // expect=different は「参考にした標識とは意味が違うので、意匠も違って当然」の印
    return { code, file, ref, expect: expect || 'same' }
  })
}

async function download(file, dest) {
  const url = `https://commons.wikimedia.org/wiki/Special:FilePath/Japan_road_sign_${file}.svg`
  const res = await fetch(url, { headers: { 'User-Agent': UA } })
  if (!res.ok) throw new Error(`${url} が取れない (HTTP ${res.status})`)
  const text = await res.text()
  if (!text.trimStart().startsWith('<?xml') && !text.trimStart().startsWith('<svg')) {
    throw new Error(`${url} が SVG ではない`)
  }
  fs.writeFileSync(dest, text)
}

/** 赤・青・白・灰が占める割合（%）。 */
async function composition(file) {
  const { data } = await sharp(file)
    .resize(48, 48, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 0 } })
    .ensureAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true })
  let red = 0, blue = 0, white = 0, gray = 0, other = 0, total = 0
  for (let i = 0; i < data.length; i += 4) {
    const [r, g, b, a] = [data[i], data[i + 1], data[i + 2], data[i + 3]]
    if (a < 60) continue
    total++
    const mx = Math.max(r, g, b), mn = Math.min(r, g, b)
    if (mx - mn < 28) { mx > 200 ? white++ : gray++; continue }
    if (r > 150 && r > g * 1.6 && r > b * 1.6) red++
    else if (b > 110 && b > r * 1.4) blue++
    else other++
  }
  const pct = (n) => Math.round((n / Math.max(total, 1)) * 100)
  return { red: pct(red), blue: pct(blue), white: pct(white), gray: pct(gray), other: pct(other) }
}

const TILE = 78, COLS = 4
const PAIR = TILE * 2 + 10

async function main() {
  const strict = process.argv.includes('--strict')
  fs.mkdirSync(CACHE, { recursive: true })
  const refs = readRefs()

  const tiles = []
  const report = []
  for (let i = 0; i < refs.length; i++) {
    const { code, file, ref, expect } = refs[i]
    const mine = path.join(ROOT, 'icons', `${code}.svg`)
    const official = path.join(CACHE, `${code}.svg`)
    if (!fs.existsSync(official)) await download(file, official)

    for (const [j, f] of [mine, official].entries()) {
      tiles.push({
        input: await sharp(f)
          .resize(TILE - 6, TILE - 6, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 0 } })
          .png().toBuffer(),
        left: (i % COLS) * PAIR + j * TILE + 3,
        top: Math.floor(i / COLS) * (TILE + 10) + 5,
      })
    }
    const m = await composition(mine), o = await composition(official)
    const diff = Math.max(...['red', 'blue', 'white'].map((k) => Math.abs(m[k] - o[k])))
    report.push({
      code, ref, expect, mine: m, official: o, diff,
      ok: diff < THRESHOLD || expect === 'different',
    })
  }

  await sharp({
    create: {
      width: COLS * PAIR, height: Math.ceil(refs.length / COLS) * (TILE + 10),
      channels: 4, background: { r: 235, g: 236, b: 240, alpha: 1 },
    },
  }).composite(tiles).png().toFile(OUT)

  const bad = report.filter((r) => !r.ok)
  const expected = report.filter((r) => r.expect === 'different')
  console.log(
    `比べたコード ${report.length} / 家族がずれているもの ${bad.length}` +
      (expected.length ? ` / 意図して違えているもの ${expected.length}` : ''),
  )
  console.log(` 左が自作、右が公式の並び画像: ${path.relative(ROOT, OUT)}`)
  const fmt = (c) => `赤${String(c.red).padStart(3)} 青${String(c.blue).padStart(3)} 白${String(c.white).padStart(3)}`
  for (const r of bad) {
    console.log(`  ${r.code.padStart(3)} (参考 ${r.ref}): 自作 ${fmt(r.mine)} / 公式 ${fmt(r.official)}`)
  }
  if (bad.length && strict) process.exit(1)
}

main().catch((e) => {
  console.error(e.message)
  process.exit(2)
})
