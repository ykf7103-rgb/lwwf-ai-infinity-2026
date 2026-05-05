"""
Batch 將 HTML 入面所有 photo-frame placeholder
換成 has-image + <img>，根據 pf-id 編號自動揾對應 filename。

只會替換已經存在嘅 image file (避免 broken link)。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()
HTML = HERE / "AI_INFINITY_終極家長簡報_45頁_v2.html"

# pf-id 編號 → filename
MAPPING = {
    "10":  "p10_chinese_class.png",
    "12":  "p12_chinese_dictation.png",
    "13":  "p13_english_class.png",
    "14":  "p14_english_ai_dictation.png",
    "16":  "p16_math_class.png",
    "17":  "p17_math_comic.png",
    "19":  "p19_music_class.png",
    "20":  "p20_fruit_month_suno.png",
    "21":  "p21_pe_class.png",
    "22":  "p22_national_treasure.png",
    "23":  "p23_ai_pe_tv.png",
    "23b": "p23b_yaoshan_lizard.png",
    "24":  "p24_science_class.png",
    "25":  "p25_plant_id.png",
    "26":  "p26_aldabra_tortoise.png",
    "27":  "p27_humanities.png",
    "28":  "p28_lokjoy_award.png",
    "29":  "p29_culture_fitting.png",
    "30":  "p30_visual_arts.png",
    "31":  "p31_modern_door_god.png",
    "32":  "p32_future_career_app.png",
    "40":  "p40_parent_workshop.png",
    "41a": "p41a_ai_garden.png",
    "41b": "p41b_butterfly_garden.png",
    "41c": "p41c_parent_empowerment.png",
    "45":  "p45_cta_horizon.png",
}

# Pattern: 揾 plain photo-frame (唔包括已 has-image 嗰啲)
# match 多行 + lenient whitespace + 可選 style attr
PATTERN = re.compile(
    r'<div class="photo-frame"([^>]*)>\s*'
    r'<div class="pf-id">相片位 #([\w]+) · ([^<]+)</div>\s*'
    r'<div class="pf-hint">([^<]+)</div>\s*'
    r'</div>',
    re.DOTALL,
)


def replace_one(m: re.Match) -> str:
    extra_attrs = m.group(1).rstrip()
    num = m.group(2)
    title = m.group(3).strip()

    if num not in MAPPING:
        print(f"  ⚠️ 冇 mapping for #{num}（{title}）— 保留 placeholder")
        return m.group(0)

    filename = MAPPING[num]
    if not (HERE / filename).exists():
        print(f"  ⏳ {filename} 仲未生成 — 保留 placeholder")
        return m.group(0)

    print(f"  ✓ #{num:<4} → {filename}")
    return (
        f'<div class="photo-frame has-image"{extra_attrs}>\n'
        f'          <img class="real" src="{filename}" alt="{title}">\n'
        f'        </div>'
    )


def main():
    if not HTML.exists():
        sys.exit(f"❌ HTML 唔見: {HTML}")

    text = HTML.read_text(encoding="utf-8")
    print(f"→ 讀 {HTML.name}")
    print(f"→ 掃描 photo-frame (唔包括已 has-image 嗰啲)...\n")

    new_text, n = PATTERN.subn(replace_one, text)

    if n == 0:
        print("\n冇任何 photo-frame 替換。")
        return

    print(f"\n→ 共替換 {n} 個 photo-frame")
    backup = HTML.with_suffix(".html.bak")
    backup.write_text(text, encoding="utf-8")
    print(f"→ 原 HTML backup 喺 {backup.name}")
    HTML.write_text(new_text, encoding="utf-8")
    print(f"✓ 已寫回 {HTML.name}")


if __name__ == "__main__":
    main()
