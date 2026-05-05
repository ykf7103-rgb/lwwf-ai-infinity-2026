"""
Poe AI image generator — for LWWF 簡報用.

支持模型 (model 參數)：
  - Gemini-2.5-Flash-Image    [預設, "Nano Banana", 最快最平]
  - Imagen-4                  [Google, 高細節]
  - Imagen-3                  [Google, 平啲]
  - FLUX-pro-1.1              [最高質但貴]
  - FLUX-Schnell              [最平最快]
  - DALL-E-3
  - Ideogram-3                [文字渲染強]

用法：
  python _gen_image.py --prompt "Beautiful minimalist square icon..." --out icon_test.png
  python _gen_image.py --prompt "..." --out p20_fruit.png --model Imagen-4
  python _gen_image.py --batch batch.txt   (batch.txt 每行: filename | prompt)

Setup:
  1. 上 https://poe.com/api_key 攞 key
  2. PowerShell: setx POE_API_KEY "your_key_here"
  3. 重啟 terminal（env var 先生效）
  4. python _gen_image.py --check  (試 key 同連線)
"""
from __future__ import annotations
import os
import re
import sys
import json
import time
import argparse
from pathlib import Path

# Force UTF-8 stdout for Windows terminal (cp950 唔識 ✓ ❌ 等)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    import requests
except ImportError:
    print("❌ 需要 requests:  pip install requests", file=sys.stderr)
    sys.exit(1)

API_URL = "https://api.poe.com/v1/chat/completions"
DEFAULT_MODEL = "Gemini-2.5-Flash-Image"
HERE = Path(__file__).parent.resolve()


def get_api_key() -> str:
    key = os.environ.get("POE_API_KEY", "").strip()
    if key:
        return key
    # fallback：keyring（如裝咗）
    try:
        import keyring
        k = keyring.get_password("poe-api", "default")
        if k:
            return k.strip()
    except ImportError:
        pass
    # fallback：本地 _secrets/poe_key.txt（已喺 .gitignore）
    secret_file = HERE / "_secrets" / "poe_key.txt"
    if secret_file.exists():
        return secret_file.read_text(encoding="utf-8").strip()
    raise SystemExit(
        "❌ 搵唔到 POE_API_KEY。請：\n"
        "   PowerShell: setx POE_API_KEY \"your_key\"\n"
        "   或者: pip install keyring && keyring set poe-api default\n"
        "   或者: 將 key 寫入 _secrets/poe_key.txt"
    )


def call_poe(prompt: str, model: str, timeout: int = 180) -> dict:
    key = get_api_key()
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    r = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(
            f"Poe API error {r.status_code}: {r.text[:500]}"
        )
    return r.json()


def extract_image_url(response: dict) -> str | None:
    """Poe response 可能有多種 image URL 位置——逐個試。"""
    try:
        choice = response["choices"][0]
        msg = choice.get("message", {})
        content = msg.get("content", "")

        # 1. markdown ![...](url)
        m = re.search(r"!\[[^\]]*\]\((https?://[^\s\)]+)\)", content)
        if m:
            return m.group(1)

        # 2. plain URL in content
        m = re.search(r"https?://[^\s\)]+\.(?:png|jpg|jpeg|webp|gif)", content, re.I)
        if m:
            return m.group(0)

        # 3. attachments array (Poe specific)
        for att in msg.get("attachments", []) or []:
            for k in ("url", "image_url", "image"):
                v = att.get(k)
                if isinstance(v, str) and v.startswith("http"):
                    return v
                if isinstance(v, dict):
                    u = v.get("url")
                    if u:
                        return u

        # 4. 整個 message 入面任何 URL
        m = re.search(r"https?://\S+\.(?:png|jpg|jpeg|webp|gif)", json.dumps(response), re.I)
        if m:
            return m.group(0).rstrip(',"\\')
    except Exception as e:
        print(f"⚠️  Extract URL 出錯: {e}", file=sys.stderr)
    return None


def download_image(url: str, out_path: Path, timeout: int = 60) -> Path:
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    out_path.write_bytes(r.content)
    return out_path


def gen_one(prompt: str, out: str, model: str = DEFAULT_MODEL,
            verbose: bool = False) -> Path:
    out_path = HERE / out if not Path(out).is_absolute() else Path(out)
    print(f"→ [{model}] {out}  ({len(prompt)} chars prompt)")
    t0 = time.time()
    response = call_poe(prompt, model)
    dt = time.time() - t0
    if verbose:
        print(json.dumps(response, indent=2, ensure_ascii=False)[:1500])
    url = extract_image_url(response)
    if not url:
        # save raw response 做 debug
        debug = HERE / f"_debug_{out}.json"
        debug.write_text(json.dumps(response, indent=2, ensure_ascii=False),
                         encoding="utf-8")
        raise RuntimeError(
            f"❌ 揾唔到 image URL — 已存 raw response 到 {debug.name}"
        )
    download_image(url, out_path)
    size_kb = out_path.stat().st_size / 1024
    print(f"  ✓ {out_path.name}  {size_kb:,.0f} KB  ({dt:.1f}s)")
    return out_path


def check_connection():
    """Quick smoke test."""
    print("→ 測試 Poe API 連線...")
    try:
        key = get_api_key()
        print(f"  ✓ POE_API_KEY 找到 (長度 {len(key)}, 前綴 {key[:4]}...)")
    except SystemExit as e:
        print(e)
        return False
    try:
        out = gen_one(
            "A simple red circle on white background, minimalist icon style",
            "_test_circle.png",
            model=DEFAULT_MODEL,
        )
        print(f"  ✓ 連線正常，測試圖已儲存：{out.name}")
        return True
    except Exception as e:
        print(f"  ❌ {e}")
        return False


def run_batch(batch_file: Path, model: str):
    """每行 'filename.png | prompt text' 格式。"""
    if not batch_file.exists():
        raise SystemExit(f"❌ batch 檔唔存在: {batch_file}")
    lines = [l.strip() for l in batch_file.read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.lstrip().startswith("#")]
    failed = 0
    for i, line in enumerate(lines, 1):
        if "|" not in line:
            print(f"  ⚠️ 第 {i} 行格式錯誤，跳過：{line[:60]}")
            failed += 1
            continue
        fname, prompt = (s.strip() for s in line.split("|", 1))
        try:
            gen_one(prompt, fname, model=model)
        except Exception as e:
            print(f"  ❌ {fname}: {e}")
            failed += 1
    print(f"\n完成：{len(lines) - failed}/{len(lines)} 成功")


def main():
    p = argparse.ArgumentParser(
        description="Poe AI image generator for LWWF 簡報",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--prompt", help="Image prompt")
    p.add_argument("--out", help="Output filename (e.g. icon_test.png)")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help=f"Model (default: {DEFAULT_MODEL})")
    p.add_argument("--check", action="store_true",
                   help="Quick connection test")
    p.add_argument("--batch", help="Batch file: each line 'filename | prompt'")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    if args.check:
        sys.exit(0 if check_connection() else 1)
    if args.batch:
        run_batch(Path(args.batch), args.model)
        return
    if not args.prompt or not args.out:
        p.error("--prompt 同 --out 都必填（除非用 --check 或 --batch）")
    gen_one(args.prompt, args.out, args.model, args.verbose)


if __name__ == "__main__":
    main()
