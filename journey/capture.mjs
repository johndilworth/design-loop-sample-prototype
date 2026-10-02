#!/usr/bin/env node
// Runs journey/flows.yaml with headless Chromium and writes screenshots + journey/manifest.json.
// Usage: node journey/capture.mjs [--cycle 1] [--base-url URL] [--flow key] [--out journey/out]
import { chromium } from 'playwright'
import YAML from 'yaml'
import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'
import { execSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, arr) => {
  if (a.startsWith('--')) acc.push([a.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true])
  return acc
}, []))
const spec = YAML.parse(fs.readFileSync(path.join(here, 'flows.yaml'), 'utf8'))
const cycle = Number(args.cycle || 1)
const baseUrl = (args['base-url'] || process.env.DEPLOY_URL || spec.base_url).replace(/\/$/, '')
const outRoot = path.resolve(args.out || path.join(here, 'out'))
const manifestPath = path.resolve(args.manifest || path.join(here, 'manifest.json'))
let commit = process.env.COMMIT_SHA || null
try { commit = commit || execSync('git rev-parse HEAD', { cwd: here }).toString().trim() } catch {}

// Normalize a URL path into a route template: strip query/hash, replace id-like segments with :id
export function routeTemplate(urlStr) {
  const u = new URL(urlStr)
  return u.pathname.split('/').map((seg) => (
    /\d/.test(seg) || /^[0-9a-f]{8,}$/i.test(seg) || /^[0-9a-f-]{36}$/i.test(seg) ? ':id' : seg
  )).join('/').replace(/\/$/, '') || '/'
}

const loc = (page, t) => page.getByRole(t.role, { name: t.name, exact: true })

async function screenInfo(page) {
  return page.evaluate(() => {
    const vis = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' }
    const texts = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6,label,legend,th,button,a,[role=radio]')]
      .filter(vis).map((e) => `${e.tagName.toLowerCase()}:${e.innerText.trim().replace(/\s+/g, ' ')}`).filter((t) => !t.endsWith(':'))
    const h1 = document.querySelector('h1')
    return { title: document.title, h1: h1 ? h1.innerText.trim() : null, texts }
  })
}

async function elementInfo(locator) {
  const box = await locator.boundingBox()
  const cssPath = await locator.evaluate((el) => {
    const parts = []
    for (let n = el; n && n.nodeType === 1 && n.tagName !== 'HTML'; n = n.parentElement) {
      let p = n.tagName.toLowerCase()
      if (n.id) { parts.unshift(`${p}#${n.id}`); break }
      const sibs = n.parentElement ? [...n.parentElement.children].filter((c) => c.tagName === n.tagName) : []
      if (sibs.length > 1) p += `:nth-of-type(${sibs.indexOf(n) + 1})`
      parts.unshift(p)
    }
    return parts.join(' > ')
  })
  return { box, cssPath }
}

const browser = await chromium.launch({ headless: true })
const entries = []
const flows = spec.flows.filter((f) => !args.flow || f.key === args.flow)
for (const flow of flows) {
  // reducedMotion + capture flag: the animated ASCII background renders one deterministic static frame,
  // so screenshots are stable across runs but still show the texture.
  const context = await browser.newContext({ viewport: spec.viewport, deviceScaleFactor: 1, reducedMotion: 'reduce' })
  await context.addInitScript(() => { window.__DESIGN_LOOP_CAPTURE__ = true })
  const page = await context.newPage()
  await page.goto(baseUrl + flow.start_url, { waitUntil: 'networkidle' })
  const dir = path.join(outRoot, `cycle-${cycle}`, flow.key, 'raw')
  fs.mkdirSync(dir, { recursive: true })
  for (const [i, step] of flow.steps.entries()) {
    if (step.expect?.h1) await page.getByRole('heading', { level: 1, name: step.expect.h1, exact: true }).waitFor({ timeout: 10000 })
    await page.waitForLoadState('networkidle')
    for (const p of step.prepare || []) {
      if (p.fill) await loc(page, p.fill).fill(String(p.value))
      else if (p.check) await loc(page, p.check).check()
      else if (p.click) await loc(page, p.click).click()
    }
    await page.mouse.move(0, 0)
    await page.waitForTimeout(150)
    const url = page.url()
    const route = routeTemplate(url)
    const info = await screenInfo(page)
    const warnings = []
    if (step.expect?.route && step.expect.route !== route) warnings.push(`route ${route} != expected ${step.expect.route}`)
    let clicked = null
    if (step.action?.click) {
      const l = loc(page, step.action.click)
      await l.scrollIntoViewIfNeeded()
      const { box, cssPath } = await elementInfo(l)
      const click = { x: Math.round(box.x + box.width / 2), y: Math.round(box.y + box.height / 2) }
      clicked = { role: step.action.click.role, name: step.action.click.name, cssPath,
        bbox: { x: Math.round(box.x), y: Math.round(box.y), width: Math.round(box.width), height: Math.round(box.height) }, click }
    }
    const file = `${String(i + 1).padStart(2, '0')}-${step.key}.png`
    await page.screenshot({ path: path.join(dir, file) })
    const fingerprint = crypto.createHash('sha256').update(info.texts.join('\n')).digest('hex').slice(0, 16)
    entries.push({
      stepKey: step.key, flow: flow.key, flowName: flow.name, cycle, index: i + 1,
      url, route, title: info.title, h1: info.h1, clicked,
      textFingerprint: fingerprint, fingerprintSource: 'sha256(visible h1-h6,label,legend,th,button,a,[role=radio] text)[:16]',
      screenshot: path.relative(path.dirname(manifestPath), path.join(dir, file)),
      timestamp: new Date().toISOString(), commit, deployUrl: baseUrl, viewport: spec.viewport, warnings,
    })
    console.log(`[cycle ${cycle}] ${flow.key} ${step.key} ${route} "${info.title}" ${warnings.join('; ')}`)
    if (clicked) {
      await page.mouse.click(clicked.click.x, clicked.click.y)
      await page.waitForLoadState('networkidle')
    }
  }
  await context.close()
}
await browser.close()

// merge with existing manifest (replace same cycle+flow)
let manifest = { version: 1, generatedAt: null, entries: [] }
if (fs.existsSync(manifestPath)) manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'))
const keys = new Set(entries.map((e) => `${e.cycle}|${e.flow}`))
manifest.entries = manifest.entries.filter((e) => !keys.has(`${e.cycle}|${e.flow}`)).concat(entries)
manifest.generatedAt = new Date().toISOString()
fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2))
console.log(`wrote ${manifestPath} (${manifest.entries.length} entries)`)
