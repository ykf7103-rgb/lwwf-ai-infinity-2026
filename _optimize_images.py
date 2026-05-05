"""
壓縮 PPT 資料夾入面所有 PNG/JPG，等 GitHub Pages 載入快、bandwidth 唔會爆。

策略：
  - PNG > 500KB  → 用 Pillow optimize=True 重存 + 壓 quality=85
  - JPG > 500KB  → quality=82 重存
  - PNG with alpha → 保留 RGBA
  - PNG without alpha → 轉 JPG（細好多）
  - 8 大科目 icon 同 P 開頭嘅 photo 都會處理
  - 原檔自動備份去 _orig/

用法：
  python _optimize_images.py              # dry run，淨係 list 將會做嘅事
  python _optimize_images.py --apply      # 真正執行
  python _optimize_images.py --apply --max 800   # 改 quality 上限
"""
from __future__ import annotations
import argparse
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌ 需要 Pillow:  pip install Pillow", file=sys.stderr)
    sys.exit(1)

HERE = Path(__file__).parent.resolve()
BACKUP = HERE / "_orig"

# 唔好 touch 嘅檔（已優化／非簡報資源）
SKIP = {
    "chart.umd.min.js",
}

THRESHOLD_KB = 500   # > 呢個 size 就壓


def human(n: int) -> str:
    for u in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:,.0f} {u}"
        n /= 1024
    return f"{n:.1f} GB"


def optimize_one(src: Path, apply: bool, max_w: int = 1600,
                 png_quality: int = 85, jpg_quality: int = 82) -> dict:
    """Return dict with stats."""
    orig_size = src.stat().st_size
    if orig_size < THRESHOLD_KB * 1024:
        return {"action": "skip", "reason": "細於 threshold", "save": 0}

    try:
        img = Image.open(src)
    except Exception as e:
        return {"action": "error", "reason": str(e), "save": 0}

    # downscale if too wide
    w, h = img.size
    if w > max_w:
        ratio = max_w / w
        new_size = (max_w, int(h * ratio))
    else:
        new_size = (w, h)

    suffix = src.suffix.lower()
    has_alpha = (img.mode in ("RGBA", "LA") or
                 (img.mode == "P" and "transparency" in img.info))

    # 決定 output format
    if suffix in (".jpg", ".jpeg"):
        out_ext = ".jpg"
        save_kwargs = {"format": "JPEG", "quality": jpg_quality, "optimize": True, "progressive": True}
    elif has_alpha:
        out_ext = ".png"
        save_kwargs = {"format": "PNG", "optimize": True}
    else:
        # PNG without alpha → 轉 JPG（細好多）
        out_ext = ".jpg"
        save_kwargs = {"format": "JPEG", "quality": jpg_quality, "optimize": True, "progressive": True}

    target = src.with_suffix(out_ext)
    if not apply:
        # dry run：估算
        return {
            "action": "would_compress",
            "from": suffix, "to": out_ext,
            "old_size": orig_size,
            "old_dim": f"{w}×{h}",
            "new_dim": f"{new_size[0]}×{new_size[1]}",
        }

    # backup 原檔
    BACKUP.mkdir(exist_ok=True)
    backup_path = BACKUP / src.name
    if not backup_path.exists():
        shutil.copy2(src, backup_path)

    # resize + save
    if new_size != (w, h):
        img = img.resize(new_size, Image.LANCZOS)
    if save_kwargs["format"] == "JPEG" and img.mode != "RGB":
        # JPG 唔支持 alpha；用 cream 背景做 backdrop
        bg = Image.new("RGB", img.size, (255, 248, 240))
        if img.mode == "RGBA":
            bg.paste(img, mask=img.split()[-1])
        else:
            bg.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
        img = bg

    img.save(target, **save_kwargs)

    # 如果 extension 改咗，刪除原 PNG
    if target != src:
        src.unlink()

    new_size_b = target.stat().st_size
    return {
        "action": "compressed",
        "from": src.name, "to": target.name,
        "old_size": orig_size, "new_size": new_size_b,
        "save": orig_size - new_size_b,
    }


def main():
    p = argparse.ArgumentParser(
        description="壓縮 PPT 資料夾入面 PNG/JPG"
    )
    p.add_argument("--apply", action="store_true",
                   help="真正執行（預設 dry-run）")
    p.add_argument("--threshold-kb", type=int, default=THRESHOLD_KB,
                   help=f"壓縮 threshold（KB，default {THRESHOLD_KB}）")
    p.add_argument("--max-width", type=int, default=1600,
                   help="最大寬度（px，default 1600）")
    p.add_argument("--png-quality", type=int, default=85)
    p.add_argument("--jpg-quality", type=int, default=82)
    p.add_argument("--include-icons", action="store_true",
                   help="連 icon_*.png 都壓（預設只壓 > threshold 嘅大檔）")
    args = p.parse_args()

    candidates = set()
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG"):
        candidates.update(HERE.glob(ext))
    # 去 _orig 同 _lib，同埋去重
    candidates = [c for c in candidates if "_orig" not in c.parts and "_lib" not in c.parts]
    candidates = sorted(set(candidates), key=lambda f: f.stat().st_size, reverse=True)

    if not candidates:
        print("冇圖可以壓")
        return

    mode = "真正執行" if args.apply else "DRY RUN"
    print(f"=== {mode} ===")
    print(f"  threshold = {args.threshold_kb} KB")
    print(f"  max width = {args.max_width} px")
    print(f"  PNG quality = {args.png_quality}, JPG quality = {args.jpg_quality}\n")

    total_old = total_new = 0
    actions = []
    for src in candidates:
        result = optimize_one(src, args.apply,
                              max_w=args.max_width,
                              png_quality=args.png_quality,
                              jpg_quality=args.jpg_quality)
        result["src"] = src.name
        actions.append(result)

    # report
    print(f"{'檔名':<48} {'動作':<15} {'原 size':>10} {'新 size':>10} {'省':>10}")
    print("-" * 100)
    for r in actions:
        if r["action"] == "skip":
            continue
        if r["action"] == "would_compress":
            print(f"{r['src']:<48} {'would compress':<15} "
                  f"{human(r['old_size']):>10} {'?':>10} {'?':>10}  "
                  f"({r['old_dim']} → {r['new_dim']}, → {r['to']})")
            total_old += r["old_size"]
        elif r["action"] == "compressed":
            print(f"{r['src']:<48} → {r['to']:<28} "
                  f"{human(r['old_size']):>10} {human(r['new_size']):>10} "
                  f"{human(r['save']):>10}")
            total_old += r["old_size"]
            total_new += r["new_size"]
        elif r["action"] == "error":
            print(f"{r['src']:<48} ERROR  {r['reason']}")

    print("-" * 100)
    if args.apply:
        saved = total_old - total_new
        pct = (saved / total_old * 100) if total_old else 0
        print(f"原 total: {human(total_old)}  →  新 total: {human(total_new)}  "
              f"省 {human(saved)} ({pct:.1f}%)")
        print(f"原檔 backup 喺 {BACKUP}")
    else:
        print(f"\nDry run 完成。run `python _optimize_images.py --apply` 真正執行。")


if __name__ == "__main__":
    main()
