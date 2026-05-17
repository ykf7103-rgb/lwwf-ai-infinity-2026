"""
Export LWWF AI INFINITY v6 deck -> A4 landscape PDF (one slide per page).

Each .slide becomes one A4 landscape page (297 x 210 mm) full-bleed.
Auto-fit shrinks any slide whose .slide-inner overflows the A4 frame.

Run:
  python _export_a4_v6.py             # exports both v6 + v6-cn
  python _export_a4_v6.py --html AI_INFINITY_v6.html --out v6_traditional_A4.pdf
"""
from __future__ import annotations
import sys
import argparse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).parent.resolve()
OUT_DIR = HERE / "_exports_a4"
OUT_DIR.mkdir(exist_ok=True)

A4_W_MM = 297   # landscape
A4_H_MM = 210
RENDER_W = 2100
RENDER_H = int(RENDER_W * A4_H_MM / A4_W_MM)   # ~1485 px (1.414 ratio)

PRINT_CSS = """
@page { size: 297mm 210mm; margin: 0; }

@media print {
@page { size: 297mm 210mm; margin: 0; }

html, body {
  margin: 0 !important;
  padding: 0 !important;
  width: 297mm !important;
  background: var(--bg, #0d0c0b) !important;
}
body::before { position: fixed !important; inset: 0 !important; opacity: 0.18 !important;
                z-index: 0 !important; display: block !important; pointer-events: none !important; }
body::after { position: fixed !important; inset: 0 !important; opacity: 0.6 !important;
               z-index: 0 !important; display: block !important; pointer-events: none !important; }

#progress, #section-tag, #brand, #pageInfo, #hint, #dots,
.lang-switcher, .nav-controls, .progress-bar, .progress-dots,
nav.print-hide, header.print-hide, footer.print-hide, .help-overlay,
button[data-lang], .nav-arrow, .keyboard-hint,
.lang-buttons, [class*="lang-switch"] { display: none !important; }

.slide {
  position: relative !important;
  inset: auto !important;
  width: 297mm !important;
  height: 210mm !important;
  min-height: 210mm !important;
  max-height: 210mm !important;
  margin: 0 !important;
  padding: 7mm 10mm !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
  page-break-after: always !important;
  break-after: page !important;
  opacity: 1 !important;
  visibility: visible !important;
  transform: none !important;
  transition: none !important;
  animation: none !important;
  pointer-events: auto !important;
}
.slide:last-child, .slide:last-of-type { page-break-after: auto !important; break-after: auto !important; }
.slide.active { opacity: 1 !important; transform: none !important; }

.slide-inner {
  width: 100% !important;
  height: 100% !important;
  max-width: 1800px !important;
  max-height: none !important;
  transform: none !important;
}
.slide-inner > * { animation: none !important; opacity: 1 !important; }

.slide *, .slide *::before, .slide *::after {
  animation: none !important;
  animation-fill-mode: none !important;
  opacity: 1 !important;
}
.slide .with-bg::after { opacity: 0.60 !important; }
.slide .with-bg::before { opacity: 0 !important; }

:root { --slide-scale: 1 !important; }

* { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
}
"""


def export_one(html_path: Path, out_pdf: Path):
    from playwright.sync_api import sync_playwright

    if not html_path.exists():
        print(f"  ! Missing HTML: {html_path}")
        return False

    url = html_path.resolve().as_uri()
    print(f"  -> Loading {html_path.name}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": RENDER_W, "height": RENDER_H},
            device_scale_factor=2,
        )
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)

        page.evaluate("""() => {
          document.querySelectorAll('.slide').forEach(s => {
            s.classList.add('active');
            s.style.opacity = '1';
            s.style.visibility = 'visible';
            s.style.transform = 'none';
          });
          window.__noScale = true;
          document.documentElement.style.setProperty('--slide-scale', '1');
        }""")

        # Emulate print media FIRST so PRINT_CSS @media print rules become active
        # for measurement (otherwise auto-fit measures at screen viewport size,
        # but PDF renders at A4 size — content would overflow).
        page.emulate_media(media="print")
        page.add_style_tag(content=PRINT_CSS)
        page.wait_for_timeout(1500)

        # Auto-fit per slide via CSS zoom (measured in print media so sizes
        # match the actual PDF page dimensions).
        page.evaluate("""() => {
          const slides = document.querySelectorAll('.slide');
          slides.forEach(slide => {
            const inner = slide.querySelector('.slide-inner');
            if (!inner) return;
            const prevOverflow = inner.style.overflow;
            inner.style.overflow = 'visible';
            const slideH = slide.clientHeight;
            const slideW = slide.clientWidth;
            const innerH = inner.scrollHeight;
            const innerW = inner.scrollWidth;
            inner.style.overflow = prevOverflow || '';
            const factorH = innerH > slideH ? slideH / innerH : 1;
            const factorW = innerW > slideW ? slideW / innerW : 1;
            const factor = Math.min(factorH, factorW);
            if (factor < 0.999) {
              const z = Math.max(0.55, factor * 0.98);
              inner.style.zoom = z.toFixed(3);
            }
          });
        }""")
        page.wait_for_timeout(800)

        n_slides = page.evaluate("document.querySelectorAll('.slide').length")
        print(f"    Slides: {n_slides}")

        print(f"  -> Writing {out_pdf.name}")
        page.pdf(
            path=str(out_pdf),
            width=f"{A4_W_MM}mm",
            height=f"{A4_H_MM}mm",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            prefer_css_page_size=False,
            scale=1.0,
        )
        browser.close()

    size_mb = out_pdf.stat().st_size / (1024 * 1024)
    print(f"    OK: {out_pdf.name}  ({size_mb:.1f} MB)")
    return True


def main():
    ap = argparse.ArgumentParser(description="A4 landscape PDF exporter for LWWF v6 deck")
    ap.add_argument("--html", help="Single HTML file (skips default batch)")
    ap.add_argument("--out", help="Output PDF filename (used with --html)")
    args = ap.parse_args()

    if args.html:
        targets = [(args.html, args.out or args.html.replace(".html", "_A4.pdf"))]
    else:
        targets = [
            ("AI_INFINITY_v6.html",    "AI_INFINITY_v6_traditional_A4.pdf"),
            ("AI_INFINITY_v6-cn.html", "AI_INFINITY_v6_simplified_A4.pdf"),
            ("AI_INFINITY_v6-en.html", "AI_INFINITY_v6_english_A4.pdf"),
        ]

    for src, dst in targets:
        html_path = HERE / src
        out_pdf = OUT_DIR / dst
        print(f"\n=== {src} ===")
        try:
            export_one(html_path, out_pdf)
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\nDone.  Output: {OUT_DIR}")


if __name__ == "__main__":
    main()
