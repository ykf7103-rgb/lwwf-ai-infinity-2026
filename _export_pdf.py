"""
自動將 LWWF 簡報 export 做 PDF（45 頁，每頁 1280×720 16:9）。

兩種做法：

【方法 1：手動 Chrome】（最簡單，免裝）
  1. Chrome 揭 index.html
  2. Ctrl+P
  3. 「目的地」揀「另存為 PDF」
  4. 「紙張大小」揀 Custom: 1280 × 720 px（或者 Letter Landscape 都得）
  5. 「邊距」揀「無」
  6. ☑ 勾選「背景圖形」(Background graphics)
  7. 儲存

【方法 2：呢個 script（自動，需 playwright）】
  pip install playwright
  python -m playwright install chromium

  python _export_pdf.py                    # 預設 output.pdf
  python _export_pdf.py --out 簡報.pdf
  python _export_pdf.py --html AI_INFINITY_終極家長簡報_45頁_v2.html

呢個 script 會：
  - 用 headless Chromium 揭簡報
  - 等 Chart.js 渲染完
  - 用 @media print CSS export 16:9 PDF
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

# Force UTF-8 stdout for Windows terminal
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).parent.resolve()
DEFAULT_HTML = "AI_INFINITY_終極家長簡報_45頁_v2.html"
DEFAULT_OUT = "AI_INFINITY_家長簡報.pdf"


QUALITY_PRESETS = {
    "draft":  {"scale": 1, "width": 1280, "height": 720, "wait": 2500},
    "screen": {"scale": 2, "width": 1280, "height": 720, "wait": 3500},  # 預設
    "print":  {"scale": 2, "width": 1920, "height": 1080, "wait": 4500},  # 4K-ish
    "ultra":  {"scale": 3, "width": 1920, "height": 1080, "wait": 5500},  # 投影 / 印刷
}


def export(html_file: Path, out_file: Path, quality: str = "screen",
           wait_override: int | None = None,
           width_override: int | None = None,
           height_override: int | None = None,
           scale_override: int | None = None):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 需要 playwright:")
        print("   pip install playwright")
        print("   python -m playwright install chromium")
        sys.exit(1)

    if not html_file.exists():
        sys.exit(f"❌ 揾唔到 HTML: {html_file}")

    preset = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["screen"])
    width = width_override or preset["width"]
    height = height_override or preset["height"]
    scale = scale_override or preset["scale"]
    wait_ms = wait_override or preset["wait"]

    url = html_file.resolve().as_uri()
    print(f"→ 揭 {html_file.name}")
    print(f"→ Quality: {quality}  | Canvas: {width}×{height}  | Scale: {scale}x  | Wait: {wait_ms}ms")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=scale,
        )
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(wait_ms)

        # 觸發所有 slide 渲染（部分 chart 可能要 active 先 render）
        page.evaluate("""() => {
            document.querySelectorAll('.slide').forEach(s => {
                s.classList.add('active');
            });
        }""")
        page.wait_for_timeout(1500)

        print(f"→ Export PDF：{out_file.name}")
        page.pdf(
            path=str(out_file),
            width=f"{width}px",
            height=f"{height}px",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            prefer_css_page_size=False,  # 我哋 explicit 指定 size
            scale=1.0,  # CSS scale；唔係 raster scale
        )
        browser.close()

    size_mb = out_file.stat().st_size / (1024 * 1024)
    print(f"✓ 完成：{out_file}  ({size_mb:.2f} MB)")


def main():
    p = argparse.ArgumentParser(
        description="LWWF 簡報 → PDF (16:9)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quality presets:
  draft   1280×720,  1x scale  → 細 size，做 quick proof
  screen  1280×720,  2x scale  → 預設，屏幕睇靚仔
  print   1920×1080, 2x scale  → 投影講座 / 高清打印
  ultra   1920×1080, 3x scale  → 報紙 / 海報級印刷

例：
  python _export_pdf.py --quality print
  python _export_pdf.py --quality ultra --out 印刷版.pdf
  python _export_pdf.py --width 1600 --height 900 --scale 2
""",
    )
    p.add_argument("--html", default=DEFAULT_HTML,
                   help=f"輸入 HTML 檔（預設 {DEFAULT_HTML}）")
    p.add_argument("--out", default=DEFAULT_OUT,
                   help=f"輸出 PDF（預設 {DEFAULT_OUT}）")
    p.add_argument("--quality", choices=list(QUALITY_PRESETS.keys()), default="screen",
                   help="預設 quality preset（default screen）")
    p.add_argument("--width", type=int, help="自訂畫布寬 (px)，覆蓋 preset")
    p.add_argument("--height", type=int, help="自訂畫布高 (px)，覆蓋 preset")
    p.add_argument("--scale", type=int, choices=[1, 2, 3], help="raster scale，覆蓋 preset")
    p.add_argument("--wait", type=int, help="等待 Chart.js / 字型 render 嘅毫秒數")
    args = p.parse_args()

    html_file = (HERE / args.html) if not Path(args.html).is_absolute() else Path(args.html)
    out_file = (HERE / args.out) if not Path(args.out).is_absolute() else Path(args.out)
    export(html_file, out_file,
           quality=args.quality,
           wait_override=args.wait,
           width_override=args.width,
           height_override=args.height,
           scale_override=args.scale)


if __name__ == "__main__":
    main()
