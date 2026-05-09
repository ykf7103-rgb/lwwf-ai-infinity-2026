"""
Export 3 個語言版本的 PDF + PPTX 到 _exports/ folder。

用法：
  python _export_all.py              # 全部 (3 PDF + 3 PPTX)
  python _export_all.py --pdf-only   # 只 PDF
  python _export_all.py --pptx-only  # 只 PPTX
"""
from __future__ import annotations
import sys
import argparse
import shutil
from pathlib import Path

# Force UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).parent.resolve()
OUT_DIR = HERE / "_exports"
OUT_DIR.mkdir(exist_ok=True)

LANG_FILES = [
    ("traditional", "繁體中文", "AI_INFINITY_精選_20頁_v3.html"),
    ("simplified",  "簡體中文", "AI_INFINITY_精選_20頁_v3-cn.html"),
    ("english",     "英文",     "AI_INFINITY_精選_20頁_v3-en.html"),
]

WIDTH = 1920
HEIGHT = 1080


def export_pdf(html_file: Path, out_pdf: Path):
    """Use playwright to export PDF."""
    from playwright.sync_api import sync_playwright

    url = html_file.resolve().as_uri()
    print(f"  → PDF: {html_file.name}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=2,
        )
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3500)
        # Force all slides to be active so they all render
        page.evaluate("""() => {
            document.querySelectorAll('.slide').forEach(s => s.classList.add('active'));
        }""")
        page.wait_for_timeout(1500)
        page.pdf(
            path=str(out_pdf),
            width=f"{WIDTH}px",
            height=f"{HEIGHT}px",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            scale=1.0,
        )
        browser.close()
    size_mb = out_pdf.stat().st_size / (1024 * 1024)
    print(f"    ✓ {out_pdf.name}  ({size_mb:.1f} MB)")


def export_pptx(html_file: Path, out_pptx: Path):
    """Screenshot each slide individually + bundle into PPTX."""
    from playwright.sync_api import sync_playwright
    from pptx import Presentation
    from pptx.util import Emu

    url = html_file.resolve().as_uri()
    tmp_dir = OUT_DIR / f"_tmp_{html_file.stem}"
    tmp_dir.mkdir(exist_ok=True)

    print(f"  → PPTX: {html_file.name}")

    images = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=1,
        )
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)

        # Get total slides
        total = page.evaluate("document.querySelectorAll('.slide').length")
        print(f"    Slides: {total}")

        for i in range(total):
            # Click to nav, or call goTo()
            page.evaluate(f"goTo({i})")
            page.wait_for_timeout(900)
            png_path = tmp_dir / f"slide_{i+1:02d}.png"
            page.screenshot(path=str(png_path), full_page=False, omit_background=False, animations='disabled')
            images.append(png_path)

        browser.close()

    # Build PPTX
    prs = Presentation()
    # Set slide size to 16:9 (1920x1080 = 25.4 cm × 14.29 cm; or in EMU)
    prs.slide_width = Emu(int(WIDTH * 9525))   # 9525 EMU per pixel at 96 DPI
    prs.slide_height = Emu(int(HEIGHT * 9525))

    blank_layout = prs.slide_layouts[6]  # Blank layout
    for img_path in images:
        slide = prs.slides.add_slide(blank_layout)
        slide.shapes.add_picture(
            str(img_path), 0, 0,
            width=prs.slide_width, height=prs.slide_height
        )

    prs.save(str(out_pptx))
    size_mb = out_pptx.stat().st_size / (1024 * 1024)
    print(f"    ✓ {out_pptx.name}  ({size_mb:.1f} MB, {len(images)} slides)")

    # Clean tmp
    shutil.rmtree(tmp_dir, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-only", action="store_true")
    ap.add_argument("--pptx-only", action="store_true")
    args = ap.parse_args()

    do_pdf = not args.pptx_only
    do_pptx = not args.pdf_only

    for slug, label, fname in LANG_FILES:
        print(f"\n=== {label} ({slug}) ===")
        html_file = HERE / fname
        if not html_file.exists():
            print(f"  ❌ 唔見 {fname}")
            continue
        if do_pdf:
            out_pdf = OUT_DIR / f"AI_INFINITY_LWWF_2026_{slug}.pdf"
            try:
                export_pdf(html_file, out_pdf)
            except Exception as e:
                print(f"  PDF error: {e}")
        if do_pptx:
            out_pptx = OUT_DIR / f"AI_INFINITY_LWWF_2026_{slug}.pptx"
            try:
                export_pptx(html_file, out_pptx)
            except Exception as e:
                print(f"  PPTX error: {e}")

    print(f"\n📁 全部已存喺：{OUT_DIR}")


if __name__ == "__main__":
    main()
