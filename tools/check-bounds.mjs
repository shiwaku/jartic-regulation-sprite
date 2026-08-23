// 独自作図のアイコンが枠の外へ描いていないかを調べる。
//
//   node tools/check-bounds.mjs           # はみ出しているものを並べる
//   node tools/check-bounds.mjs --strict  # 1つでもあれば異常終了する
//
// 64×64 の外へ描いた図形は切り落とされる（矢印の先や線が欠ける）。目で探すのは
// あてにならないので、**viewBox を広げて描き直し、本来の 64×64 の外に色が乗って
// いないか**を見る。乗っていれば、その分は配信物では欠けている。
//
// あわせて **台紙（円・正方形・路面など）の外に出ていないか** も見る。枠の中でも
// 台紙から飛び出していれば、地図では「絵が台紙からこぼれている」ように見える。
//
// 対象は独自作図（viewBox が "0 0 64 64" のもの）だけ。標識令の図案は台紙が
// 枠いっぱいに描かれているのが正しい形なので、この検査にはかけない。

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import sharp from 'sharp'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const ICONS = path.join(ROOT, 'icons')
const BOX = 64
const PAD = 16                       // 上下左右にこれだけ広げて描く
const SCALE = 3                      // 1 単位あたりの画素数
const ALPHA = 40                     // これ以上の不透明度を「中身」とする
const OURS = 'viewBox="0 0 64 64"'

/** 台紙の形。SVG の先頭に置く台紙から見分ける。 */
function plate(svg) {
  if (/<circle cx="32" cy="32" r="27"/.test(svg)) return { kind: 'circle', r: 27.5 }
  if (/<path d="M32 3 L59 22/.test(svg)) return { kind: 'pentagon' }
  if (/<path d="M4 12 L60 12/.test(svg)) return { kind: 'triangle' }
  if (/<rect x="5" y="5" width="54" height="54"/.test(svg)) return { kind: 'rect', a: 5, b: 59 }
  if (/<rect x="4" y="4" width="56" height="56"/.test(svg)) return { kind: 'rect', a: 4, b: 60 }
  if (/<rect x="3" y="3" width="58" height="58"/.test(svg)) return { kind: 'rect', a: 3, b: 61 }
  if (/<rect x="3" y="18" width="58" height="28"/.test(svg)) return { kind: 'rect', a: 3, b: 61, top: 18, bottom: 46 }
  return null
}

/** 台紙の外に乗っている面積（64換算の平方px）。多角形は判定が難しいので見ない。 */
async function outsidePlate(file, svg) {
  const pl = plate(svg)
  if (!pl || pl.kind === 'pentagon' || pl.kind === 'triangle') return null
  const side = BOX * SCALE
  const { data } = await sharp(Buffer.from(
    svg.replace(/width="\d+" height="\d+"/, `width="${side}" height="${side}"`),
  )).ensureAlpha().raw().toBuffer({ resolveWithObject: true })
  let out = 0
  for (let y = 0; y < side; y++) {
    for (let x = 0; x < side; x++) {
      if (data[(y * side + x) * 4 + 3] <= ALPHA) continue
      const ux = (x + 0.5) / SCALE, uy = (y + 0.5) / SCALE
      let inside
      if (pl.kind === 'circle') {
        inside = (ux - 32) ** 2 + (uy - 32) ** 2 <= pl.r ** 2
      } else {
        const top = pl.top ?? pl.a, bottom = pl.bottom ?? pl.b
        inside = ux >= pl.a && ux <= pl.b && uy >= top && uy <= bottom
      }
      if (!inside) out++
    }
  }
  return out / (SCALE * SCALE)
}

/** 枠の外に乗っている画素の数を、上下左右ごとに返す。 */
async function outside(file) {
  const svg = fs.readFileSync(file, 'utf8')
  const padded = svg
    .replace(OURS, `viewBox="${-PAD} ${-PAD} ${BOX + PAD * 2} ${BOX + PAD * 2}"`)
    .replace(/width="\d+" height="\d+"/, `width="${(BOX + PAD * 2) * SCALE}" height="${(BOX + PAD * 2) * SCALE}"`)
  const side = (BOX + PAD * 2) * SCALE
  const { data } = await sharp(Buffer.from(padded)).ensureAlpha().raw()
    .toBuffer({ resolveWithObject: true })
  const at = (x, y) => data[(y * side + x) * 4 + 3]
  const lo = PAD * SCALE, hi = (PAD + BOX) * SCALE
  const out = { top: 0, bottom: 0, left: 0, right: 0 }
  for (let y = 0; y < side; y++) {
    for (let x = 0; x < side; x++) {
      if (at(x, y) <= ALPHA) continue
      if (y < lo) out.top++
      else if (y >= hi) out.bottom++
      else if (x < lo) out.left++
      else if (x >= hi) out.right++
    }
  }
  return out
}

async function main() {
  const strict = process.argv.includes('--strict')
  const files = fs.readdirSync(ICONS).filter((f) => f.endsWith('.svg'))
    .sort((a, b) => parseInt(a) - parseInt(b))
  const ours = files.filter((f) => fs.readFileSync(path.join(ICONS, f), 'utf8').includes(OURS))

  const bad = []
  for (const f of ours) {
    const full = path.join(ICONS, f)
    const svg = fs.readFileSync(full, 'utf8')
    const o = await outside(full)
    const frame = (o.top + o.bottom + o.left + o.right) / (SCALE * SCALE)
    const spill = await outsidePlate(full, svg)
    // 1平方px 未満は丸め誤差として見逃す。台紙外は縁の抗ざらつきが出るので少し緩める
    if (frame >= 1 || (spill !== null && spill >= 4)) {
      bad.push({ code: f.replace('.svg', ''), ...o, frame, spill })
    }
  }

  console.log(`独自作図 ${ours.length} 個を調べた / はみ出しているもの ${bad.length}`)
  for (const b of bad) {
    const px = (n) => (n / (SCALE * SCALE)).toFixed(1)
    const where = [
      b.top && `上${px(b.top)}`, b.bottom && `下${px(b.bottom)}`,
      b.left && `左${px(b.left)}`, b.right && `右${px(b.right)}`,
    ].filter(Boolean).join(' ')
    const parts = []
    if (b.frame >= 1) parts.push(`枠外 ${b.frame.toFixed(1)}（${where}）`)
    if (b.spill !== null && b.spill >= 4) parts.push(`台紙外 ${b.spill.toFixed(1)}`)
    console.log(`  ${b.code.padStart(3)}: ${parts.join(' / ')}`)
  }
  console.log('（面積は 64×64 換算の平方px）')
  if (bad.length && strict) process.exit(1)
}

main().catch((e) => {
  console.error(e.message)
  process.exit(2)
})
