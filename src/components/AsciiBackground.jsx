import { useEffect, useRef } from 'react'
import { isCaptureMode } from '../captureMode'

// Subtle animated ASCII "shader" behind the home page only (cycle-2 feedback; home-only since cycle 3).
// - Plain <canvas>, no dependencies; ~12 fps; pauses while the tab is hidden.
// - Static single frame when the user prefers reduced motion, or during journey capture
//   (window.__DESIGN_LOOP_CAPTURE__ set by journey/capture.mjs, or ?capture=1 in the URL),
//   so screenshots are deterministic but still show the texture.
const CHARS = ' .,:;-=+*#'
const CELL_W = 12
const CELL_H = 18
const FPS = 12
const STATIC_T = 7.25 // deterministic time used for the frozen frame

function isFrozen() {
  if (typeof window === 'undefined') return true
  if (isCaptureMode()) return true
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}

export default function AsciiBackground() {
  const ref = useRef(null)
  useEffect(() => {
    const canvas = ref.current
    const ctx = canvas.getContext('2d')
    let w = 0, h = 0, raf = 0, last = 0
    const start = performance.now()

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      w = window.innerWidth; h = window.innerHeight
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr)
      canvas.style.width = w + 'px'; canvas.style.height = h + 'px'
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    }

    const draw = (t) => {
      ctx.clearRect(0, 0, w, h)
      ctx.font = "13px 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
      ctx.textBaseline = 'top'
      ctx.fillStyle = '#8f9bff' // light glyphs on the dark theme (cycle 3)
      const cols = Math.ceil(w / CELL_W), rows = Math.ceil(h / CELL_H)
      const cx = cols * 0.7, cy = rows * 0.35
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          const d = Math.hypot((x - cx) * 0.6, y - cy)
          let v = Math.sin(x * 0.09 + t * 0.6) + Math.sin(y * 0.16 - t * 0.45) +
            Math.sin((x + y) * 0.05 + t * 0.3) + Math.sin(d * 0.22 - t * 0.9)
          v = (v + 4) / 8 // 0..1
          const i = Math.floor(Math.pow(v, 1.4) * CHARS.length)
          if (i <= 0) continue
          ctx.globalAlpha = 0.04 + v * 0.12
          ctx.fillText(CHARS[Math.min(i, CHARS.length - 1)], x * CELL_W, y * CELL_H)
        }
      }
      ctx.globalAlpha = 1
    }

    const loop = (now) => {
      raf = requestAnimationFrame(loop)
      if (document.hidden || now - last < 1000 / FPS) return
      last = now
      draw((now - start) / 1000)
    }

    resize()
    const frozen = isFrozen()
    draw(STATIC_T)
    canvas.dataset.state = frozen ? 'static' : 'animated'
    const onResize = () => { resize(); if (frozen) draw(STATIC_T) }
    window.addEventListener('resize', onResize)
    if (!frozen) raf = requestAnimationFrame(loop)
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', onResize) }
  }, [])
  return <canvas ref={ref} className="ascii-bg" aria-hidden="true" data-testid="ascii-bg" />
}
