# Poe AI 圖片生成 setup

`_gen_image.py` 用 Poe API 調用 Nano Banana / Imagen / FLUX 等模型生圖，落本地直接整合落 HTML。

## 安裝 API key（揀其中一個方法）

### ⭐ 方法 1：環境變數（最簡單）

```powershell
# PowerShell（一次性，永久）
setx POE_API_KEY "你嘅_poe_key_由_https://poe.com/api_key_攞"

# 之後重啟 terminal，再 verify
python _gen_image.py --check
```

**優點：** 簡單、跨 terminal 通用  
**缺點：** Key 用明文存喺 Windows User registry（其他 admin 可能睇到）

### 🔒 方法 2：Windows Credential Manager + keyring（最安全）

```powershell
pip install keyring
python -c "import keyring; keyring.set_password('poe-api', 'default', input('Paste POE key: '))"
```

Key 會經 Windows DPAPI 加密存喺 Credential Manager。其他用戶／其他 admin 都解唔到。

**優點：** 真正加密、跨 terminal 通用  
**缺點：** 要安裝 `keyring` library

### 📁 方法 3：本地 _secrets/poe_key.txt（最快試）

```powershell
# 將 key 寫入呢個檔
'你嘅_poe_key' | Out-File -Encoding utf8 _secrets/poe_key.txt
```

`_secrets/` 資料夾已預設加入 `.gitignore` —— 永遠唔會 push 上 GitHub。

**優點：** 即試即用、唔需要重啟 terminal  
**缺點：** 明文存喺資料夾（需要保護資料夾權限）

⚠️ **千祈唔好** 將 key 直接寫入 chat、commit message、或者其他 .py / .md 檔。

## 用法

### 試一次連線
```bash
python _gen_image.py --check
```
會生成一張紅色圓形 test 圖確認 key 正常。

### 生一張
```bash
python _gen_image.py --prompt "Beautiful minimalist icon..." --out icon_test.png
```

預設用 Nano Banana（最平最快）。要更高質：
```bash
python _gen_image.py --prompt "..." --out p20_fruit.png --model Imagen-4
```

### Batch 多張（一個檔搞掂）
寫一個 `_batch.txt`，每行格式：`檔名.png | prompt`

```
icon_science.png | Beautiful minimalist square icon, emerald leaf with DNA helix
icon_music.png   | Beautiful minimalist square icon, music note with sound waves
icon_pe.png      | Beautiful minimalist square icon, running figure with motion lines
```

然後：
```bash
python _gen_image.py --batch _batch.txt
# 或者改 model
python _gen_image.py --batch _batch.txt --model Imagen-4
```

## 模型對照表

| Model 參數 | 質素 | 速度 | 成本 (估算) |
|---|---|---|---|
| `Gemini-2.5-Flash-Image` ⭐預設 | 中上 | ~5 秒 | 最平 |
| `Imagen-4` | 高 | ~15 秒 | 中 |
| `Imagen-3` | 中高 | ~10 秒 | 平 |
| `FLUX-pro-1.1` | 最高 | ~20 秒 | 最貴 |
| `FLUX-Schnell` | 中 | ~3 秒 | 最平 |
| `DALL-E-3` | 高 | ~15 秒 | 中 |
| `Ideogram-3` | 中（文字強）| ~10 秒 | 中 |

實際點數消耗會 fluctuate — 第一次試嗰陣留意 Poe 個 dashboard 扣咗幾多。

## 安全 checklist

- ✅ `_secrets/` 喺 `.gitignore`
- ✅ Key 唔會 commit
- ✅ Script 用 `os.environ.get` 唔會 hardcode
- ✅ 唔好喺 chat 直接貼 key（即使俾 Claude，因為 transcript 可能會 log）

## Troubleshooting

| 訊息 | 解法 |
|---|---|
| `搵唔到 POE_API_KEY` | 重啟 terminal；用方法 3（本地 file）即試 |
| `Poe API error 401` | Key 錯／過期，重新去 poe.com/api_key 攞 |
| `Poe API error 402` | 點數用完，去 Poe 訂閱／買 credit |
| `揾唔到 image URL` | Model 唔生圖（揀錯 model）；睇 `_debug_xxx.json` |
