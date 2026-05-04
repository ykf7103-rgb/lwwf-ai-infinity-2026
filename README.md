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

© 2026 樂善堂梁黃蕙芳紀念學校
