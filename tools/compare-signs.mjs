// 取り込んだアイコンが標識の図案と一致しているかを確かめる。
//
//   node tools/compare-official.mjs          # 比べて結果を出す
//   node tools/compare-official.mjs --strict # ずれていたら異常終了する
//
// data/official_refs.csv の対応で、icons/<コード>.svg と signs/<ファイル>.svg を
// 並べた画像（.cache/compare.png）を作り、色の構成を比べる。どちらもリポジトリ内に
// あるので、ネットワークは使わない。
//
// 取り込み（tools/import_official.py）はルート要素の width/height を書き換えるだけで
// パスに手を入れないので、ここでずれが出たら取り込みが壊れている。

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import sharp from 'sharp'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const OUT = path.join(ROOT, '.cache', 'compare.png')
const REFS = path.join(ROOT, 'data', 'sign_refs.csv')
/** これ以上ずれていたら取り込みが壊れていると見なす（ポイント）。 */
const THRESHOLD = 8

function readRefs() {
  return fs
    .readFileSync(REFS, 'utf8')
    .trim()
    .split(/\r?\n/)
    .slice(1)
    .map((line) => {
      // note に読点は入るがカンマは入れない決まり。先頭3つだけを取る
      const [code, file, signNo] = line.split(',')
      return { code, file, signNo }
    })
}

/** 赤・青・白・灰・黄が占める割合（%）。 */
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

const TILE = 78, COLS = 4, PAIR = TILE * 2 + 10

async function main() {
  const strict = process.argv.includes('--strict')
  fs.mkdirSync(path.dirname(OUT), { recursive: true })
  const refs = readRefs()

  const tiles = []
  const report = []
  for (let i = 0; i < refs.length; i++) {
    const { code, file, signNo } = refs[i]
    const mine = path.join(ROOT, 'icons', `${code}.svg`)
    const sign = path.join(ROOT, 'signs', `${file}.svg`)
    for (const f of [mine, sign]) {
      if (!fs.existsSync(f)) throw new Error(`${path.relative(ROOT, f)} が無い`)
    }
    for (const [j, f] of [mine, sign].entries()) {
      tiles.push({
        input: await sharp(f)
          .resize(TILE - 6, TILE - 6, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 0 } })
          .png().toBuffer(),
        left: (i % COLS) * PAIR + j * TILE + 3,
        top: Math.floor(i / COLS) * (TILE + 10) + 5,
      })
    }
    const m = await composition(mine), o = await composition(sign)
    const diff = Math.max(...['red', 'blue', 'white', 'gray'].map((k) => Math.abs(m[k] - o[k])))
    report.push({ code, signNo, mine: m, official: o, diff, ok: diff < THRESHOLD })
  }

  await sharp({
    create: {
      width: COLS * PAIR, height: Math.ceil(refs.length / COLS) * (TILE + 10),
      channels: 4, background: { r: 235, g: 236, b: 240, alpha: 1 },
    },
  }).composite(tiles).png().toFile(OUT)

  const bad = report.filter((r) => !r.ok)
  console.log(`標識の図案を使っているコード ${report.length} / ずれ ${bad.length}`)
  console.log(` 左が取り込み後、右が元の意匠: ${path.relative(ROOT, OUT)}`)
  const fmt = (c) => `赤${String(c.red).padStart(3)} 青${String(c.blue).padStart(3)} 白${String(c.white).padStart(3)}`
  for (const r of bad) {
    console.log(`  ${r.code.padStart(3)} (標識 ${r.signNo}): 取り込み後 ${fmt(r.mine)} / 元 ${fmt(r.official)}`)
  }
  if (bad.length && strict) process.exit(1)
}

main().catch((e) => {
  console.error(e.message)
  process.exit(2)
})
