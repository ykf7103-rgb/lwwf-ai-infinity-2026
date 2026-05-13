"""
Export LWWF AI INFINITY v5 deck → A3 landscape PDF, every slide fills the full page.

Why this script:
  Earlier exports used a 16:9 PDF page printed onto A3 paper, so the print
  driver shrank everything into a small rectangle with thick white borders.
  This script outputs a true A3 landscape (420 × 297 mm) PDF, with each
  slide stretched / scaled so the visible content fills the entire A3 sheet.

Run:
  pip install playwright
  python -m playwright install chromium
  python _export_a3_print.py

Output:
  _exports/AI_INFINITY_LWWF_2026_v5_A3_<lang>.pdf
"""
from __future__ import annotations
import sys
import shutil
import argparse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).parent.resolve()
OUT_DIR = HERE / "_exports"
OUT_DIR.mkdir(exist_ok=True)

# A3 landscape physical = 420 x 297 mm.  Render canvas at 2x density.
# Playwright uses CSS pixels at 96 DPI.  420mm = ~1587 px, 297mm = ~1123 px.
A3_W_MM = 420
A3_H_MM = 297

# Render viewport bigger than physical for crispness.
RENDER_W = 2400
RENDER_H = int(RENDER_W * A3_H_MM / A3_W_MM)   # 1697 px ≈ A3 ratio (1.414)

# Print-only CSS injected at runtime.
# Goal:
#   * Every .slide becomes exactly one PDF page = 420mm × 297mm.
#   * Each slide's own background colour / gradient extends to fill the page.
#   * The 16:9 slide-inner reference frame is preserved at A3 width so the
#     designed layout renders exactly as on screen, just much bigger.
#     A3 landscape ratio (1.414) is narrower than 16:9 (1.778) — anchoring
#     on WIDTH gives a content strip 420mm × 236.25mm centred vertically
#     (≈30 mm of slide-bg padding top + bottom).
#   * Disable all transitions / opacity / transforms left over from the
#     interactive deck logic.
PRINT_CSS = """
@page { size: 420mm 297mm; margin: 0; }

@media print {
@page { size: 420mm 297mm; margin: 0; }

html, body {
  margin: 0 !important;
  padding: 0 !important;
  width: 420mm !important;
  background: var(--bg, #0d0c0b) !important;
}
/* Keep paper-texture body bg visible in PDF (user wants slide bg image visible).
   body::before is the bg_main.png paper texture, body::after is gradient orbs. */
body::before { position: fixed !important; inset: 0 !important; opacity: 0.18 !important;
                z-index: 0 !important; display: block !important; pointer-events: none !important; }
body::after { position: fixed !important; inset: 0 !important; opacity: 0.6 !important;
               z-index: 0 !important; display: block !important; pointer-events: none !important; }

/* Hide interactive UI chrome */
#progress, #section-tag, #brand, #pageInfo, #hint, #dots,
.lang-switcher, .nav-controls, .progress-bar, .progress-dots,
nav.print-hide, header.print-hide, footer.print-hide, .help-overlay,
button[data-lang], .nav-arrow, .keyboard-hint,
.lang-buttons, [class*="lang-switch"] { display: none !important; }

/* Each .slide = exactly one A3 landscape page, full-bleed.
   Keep the deck's natural flex centering for .slide-inner — do NOT
   force a height on .slide-inner; the slide bg fills any extra space. */
.slide {
  position: relative !important;
  inset: auto !important;
  width: 420mm !important;
  height: 297mm !important;
  min-height: 297mm !important;
  max-height: 297mm !important;
  margin: 0 !important;
  padding: 10mm 14mm !important;
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

/* Let slide-inner take its designed shape; raise its max-width so it
   uses the full A3 width.  Critical: keep height:100% so flex:1
   children expand correctly. */
.slide-inner {
  width: 100% !important;
  height: 100% !important;
  max-width: 1800px !important;
  max-height: none !important;
  transform: none !important;
}
.slide-inner > * { animation: none !important; opacity: 1 !important; }

/* CRITICAL: kill ALL CSS animations everywhere.  The deck uses
   `animation: v4ZoomIn ... backwards` on cards / images / titles —
   when rendered statically, "backwards" leaves them at the 0%
   keyframe (invisible / scaled-to-0).  Force fill-mode to none so
   the element's normal style applies. */
.slide *, .slide *::before, .slide *::after {
  animation: none !important;
  animation-fill-mode: none !important;
  opacity: 1 !important;
}
/* Preserve decorative bg-image opacity for v6 print clarity (was 0.05 in EN
   version; v6 uses written Chinese which is shorter so we can show more bg). */
.slide .with-bg::after { opacity: 0.60 !important; }
.slide .with-bg::before { opacity: 0 !important; }

/* Kill the JS-driven scale variable */
:root { --slide-scale: 1 !important; }

/* Keep colours exact */
* { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
}
"""


def export_one(html_path: Path, out_pdf: Path):
    from playwright.sync_api import sync_playwright

    if not html_path.exists():
        print(f"  ! Missing HTML: {html_path}")
        return False

    url = html_path.resolve().as_uri()
    print(f"  → Loading {html_path.name}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": RENDER_W, "height": RENDER_H},
            device_scale_factor=2,
        )
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(4000)

        # Activate every slide and disable the dynamic scale logic
        page.evaluate("""() => {
          document.querySelectorAll('.slide').forEach(s => {
            s.classList.add('active');
            s.style.opacity = '1';
            s.style.visibility = 'visible';
            s.style.transform = 'none';
          });
          // Stop any goTo() / scroll observers
          window.__noScale = true;
          document.documentElement.style.setProperty('--slide-scale', '1');
        }""")

        # Inject print stylesheet
        page.add_style_tag(content=PRINT_CSS)

        # Force layout settle
        page.wait_for_timeout(2000)

        # Per-slide auto-fit: any slide-inner that overflows its A3 frame
        # gets shrunk via CSS zoom (zoom affects layout box, not just paint,
        # so children re-flow cleanly inside the smaller box).
        page.evaluate("""() => {
          const slides = document.querySelectorAll('.slide');
          slides.forEach(slide => {
            const inner = slide.querySelector('.slide-inner');
            if (!inner) return;
            // Temporarily allow overflow to measure natural size
            const prevOverflow = inner.style.overflow;
            inner.style.overflow = 'visible';
            // Slide box at A3 minus our 10/14 mm padding ≈ 277 × 392 mm
            const slideH = slide.clientHeight;
            const slideW = slide.clientWidth;
            const innerH = inner.scrollHeight;
            const innerW = inner.scrollWidth;
            inner.style.overflow = prevOverflow || '';
            const factorH = innerH > slideH ? slideH / innerH : 1;
            const factorW = innerW > slideW ? slideW / innerW : 1;
            const factor = Math.min(factorH, factorW);
            if (factor < 0.999) {
              const z = Math.max(0.70, factor * 0.99);  // 1% safety margin
              inner.style.zoom = z.toFixed(3);
            }
          });
        }""")
        page.wait_for_timeout(800)

        # Pre-flight: count slides
        n_slides = page.evaluate("document.querySelectorAll('.slide').length")
        print(f"    Slides: {n_slides}")

        print(f"  → Writing {out_pdf.name}")
        page.emulate_media(media="print")
        page.pdf(
            path=str(out_pdf),
            width=f"{A3_W_MM}mm",
            height=f"{A3_H_MM}mm",
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
    ap = argparse.ArgumentParser(description="A3 landscape full-bleed PDF exporter for LWWF v5 deck")
    ap.add_argument("--html", default="AI_INFINITY_終極版_v5-en.html",
                    help="Input HTML filename (default: English v5)")
    ap.add_argument("--out",  default="AI_INFINITY_LWWF_2026_v5_A3_english.pdf",
                    help="Output PDF filename (in _exports/)")
    ap.add_argument("--all-langs", action="store_true",
                    help="Export trad / simp / english at once.")
    args = ap.parse_args()

    if args.all_langs:
        targets = [
            ("AI_INFINITY_終極版_v5.html",    "AI_INFINITY_LWWF_2026_v5_A3_traditional.pdf"),
            ("AI_INFINITY_終極版_v5-cn.html", "AI_INFINITY_LWWF_2026_v5_A3_simplified.pdf"),
            ("AI_INFINITY_終極版_v5-en.html", "AI_INFINITY_LWWF_2026_v5_A3_english.pdf"),
        ]
    else:
        targets = [(args.html, args.out)]

    for src, dst in targets:
        html_path = HERE / src
        out_pdf = OUT_DIR / dst
        print(f"\n=== {src} ===")
        try:
            export_one(html_path, out_pdf)
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\nDone.  Output folder: {OUT_DIR}")


if __name__ == "__main__":
    main()
