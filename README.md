# LWWF · AI INFINITY 家長簡報 (2026)

樂善堂梁黃蕙芳紀念學校 · 2026 家長講座主簡報。

## 開啟方式

| 環境 | 做法 |
|---|---|
| **本地 USB / Google Drive** | 雙擊 `index.html`（會自動跳到主簡報） |
| **GitHub Pages 線上版** | 揭 repo settings 列出嘅 Pages URL（自動載入 index → 主簡報） |
| **Chrome 拖檔** | 將 `AI_INFINITY_終極家長簡報_45頁_v2.html` 拖落 Chrome 視窗 |

## 結構

```
.
├─ index.html                                        ← 入口（auto-redirect）
├─ AI_INFINITY_終極家長簡報_45頁_v2.html              ← 主簡報（45 頁）
├─ _lib/chart.umd.min.js                             ← 本地 Chart.js（offline 都正常）
├─ icon_*.png                                        ← 8 大科目 button icon
├─ p*_*.png                                          ← 各頁 hero / 配圖
├─ bg_main.png                                       ← 全站背景
└─ _make_icons.py                                    ← 4 個 minimalist icon 生成 script（PIL）
```

## 鍵盤操作

| 鍵 | 動作 |
|---|---|
| `→` / `Space` / `PageDown` | 下一頁 |
| `←` / `PageUp` | 上一頁 |
| `F` | 全屏 |

## 講座 fallback Plan

1. **Plan A** — USB + Chrome（現場必備）
2. **Plan B** — GitHub Pages line（這個 repo 嘅 Pages URL）
3. **Plan C** — 手機 hotspot + Plan B

字型已預設 `Microsoft JhengHei` / `PingFang TC` / `PMingLiU` fallback——即使無 wifi、Google Fonts 載唔到，都唔會變細明體走樣。

## 維護

加新相 / 改文字 → 直接編輯 HTML → `git add . && git commit -m "..." && git push` → GitHub Pages 自動 re-deploy（30 秒內）。

---

## 📄 Export PDF（45 頁，每頁 1280×720 16:9）

### 方法 1 — Chrome 手動（最簡單）
1. Chrome 揭 `index.html`
2. `Ctrl + P`
3. 「目的地」→「另存為 PDF」
4. 「紙張大小」→ Custom: **1280 × 720 px**（或 Letter Landscape）
5. 「邊距」→ **無**
6. ☑ 勾選「**背景圖形**」(Background graphics) — **必須**否則一片空白
7. 儲存

### 方法 2 — 自動化（要裝 playwright）
```bash
pip install playwright
python -m playwright install chromium

python _export_pdf.py                          # 預設 → AI_INFINITY_家長簡報.pdf
python _export_pdf.py --out 給家長.pdf
```

---

## 🗜️ 壓縮圖片（加完相之後一定要做）

```bash
python _optimize_images.py             # dry run，淨係預覽
python _optimize_images.py --apply     # 真正執行（原檔自動 backup 喺 _orig/）
```

預設策略：
- > 500 KB 嘅 PNG / JPG 都壓
- 寬度 cap @ 1600px
- 無 alpha 嘅 PNG → 自動轉 JPG（細好多）
- 有 alpha 嘅 PNG → 保留，optimize=True

實測效果：66MB → 23MB（省 65%）。

---

## 🎨 Poe AI 生圖（可選）

詳細：[POE_SETUP.md](POE_SETUP.md)

```bash
python _gen_image.py --check                              # 試 API key
python _gen_image.py --prompt "..." --out icon_test.png   # 預設 Nano Banana
python _gen_image.py --prompt "..." --out p20.png --model Imagen-4
python _gen_image.py --batch _batch.txt                   # 一次過多張
```

---

© 2026 樂善堂梁黃蕙芳紀念學校
