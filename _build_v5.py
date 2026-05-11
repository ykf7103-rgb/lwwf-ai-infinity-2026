"""Build v5-cn.html (OpenCC) + v5-en.html (native idiomatic rewrite) from v5.html.

V5 = Ultimate Edition. Builds on v4 EN base, adds new pages:
- P2 講座流程概覽
- P3 上下午課程編排
- P4 校本特色概覽
- P24-P25 P1 新分班 (Class A/B/C)
- P26-P28 英尖班 3 頁
- P29-P30 無考默政策
- P31 評估三軌 + P32 功輔課託
- P33-P34 啟發潛能
- P35-P36 課外活動
- P37-P38 升小適應
- P40 Q&A
"""
import re
from pathlib import Path
from opencc import OpenCC
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = Path(__file__).parent
SRC = ROOT / "AI_INFINITY_終極版_v5.html"
DST_CN = ROOT / "AI_INFINITY_終極版_v5-cn.html"
DST_EN = ROOT / "AI_INFINITY_終極版_v5-en.html"

text = SRC.read_text(encoding="utf-8")

# ============================================================
# 1. Simplified (HK 繁 → 大陸簡)
# ============================================================
cc = OpenCC('hk2s')
cn = cc.convert(text)
cn = cn.replace('<html lang="zh-Hant">', '<html lang="zh-Hans">')
cn = cn.replace('<title>AI INFINITY · LWWF · 終極版 v5</title>',
                '<title>AI INFINITY · LWWF · 终极版 v5</title>')
cn = cn.replace(
    '<button data-lang="t" class="active" title="繁體中文">繁</button>',
    '<button data-lang="t" title="繁体中文">繁</button>'
)
cn = cn.replace(
    '<button data-lang="s" title="简体中文">简</button>',
    '<button data-lang="s" class="active" title="简体中文">简</button>'
)
DST_CN.write_text(cn, encoding="utf-8")
print(f"OK {DST_CN.name} ({DST_CN.stat().st_size/1024:.0f} KB)")

# ============================================================
# 2. English — Native idiomatic rewrite
# Strategy: Start from v4-en (which has v3+v4 native dict applied),
#           extend with v5-specific dict for new pages.
# ============================================================

v4_en = (ROOT / "AI_INFINITY_精選_20頁_v4-en.html").read_text(encoding="utf-8")

# Replace title/lang
v5_en = v4_en.replace(
    '<title>AI INFINITY · LWWF · Editorial v4 — Parent Briefing</title>',
    '<title>AI INFINITY · LWWF · Ultimate Edition v5 — Parent Briefing</title>'
)

# Update page count
v5_en = v5_en.replace(
    '<div id="pageInfo"><span id="pn">1</span><span class="total"> / 21</span></div>',
    '<div id="pageInfo"><span id="pn">1</span><span class="total"> / 40</span></div>'
)

# Update fileMap (cross-language switch)
v5_en = v5_en.replace(
    "'t': 'AI_INFINITY_精選_20頁_v4.html'",
    "'t': 'AI_INFINITY_終極版_v5.html'"
)
v5_en = v5_en.replace(
    "'s': 'AI_INFINITY_精選_20頁_v4-cn.html'",
    "'s': 'AI_INFINITY_終極版_v5-cn.html'"
)
v5_en = v5_en.replace(
    "'e': 'AI_INFINITY_精選_20頁_v4-en.html'",
    "'e': 'AI_INFINITY_終極版_v5-en.html'"
)

# Update version badge in CSS
v5_en = v5_en.replace("content:'V4 EDITORIAL';", "content:'V5 ULTIMATE';")

# Extract v5 page-specific CSS (keyframes / utility classes) from source
m = re.search(r'/\* =+\s*V5 PAGE-SPECIFIC EFFECTS[\s\S]*?\.act-tile \.cat-list\{[^}]*\}', text)
if m:
    v5_css = m.group(0)
    # Inject before </style> in the editorial-polish block
    v5_en = v5_en.replace(
        "</style>\n<style>\n:root{",
        v5_css + "\n</style>\n<style>\n:root{",
        1
    )

# Extract v5-font-boost-2 + v5-font-boost (both style blocks) and inject at top
for boost_id in ['v5-font-boost-2', 'v5-font-boost']:
    m_boost = re.search(rf'<style id="{boost_id}">[\s\S]*?</style>', text)
    if m_boost:
        font_boost = m_boost.group(0)
        if f'id="{boost_id}"' not in v5_en:
            v5_en = re.sub(
                r'(<link[^>]+fonts\.googleapis[^>]+>\s*)',
                r'\1\n' + font_boost + '\n',
                v5_en, count=1
            )

# Extract v5-final-overrides (must be LAST style block — wins all specificity) inject before </head>
m_final = re.search(r'<style id="v5-final-overrides">[\s\S]*?</style>', text)
if m_final:
    final_css = m_final.group(0)
    if 'id="v5-final-overrides"' not in v5_en:
        v5_en = v5_en.replace('</head>', final_css + '\n</head>', 1)

# Inject fit-to-screen IIFE + video reset JS into v5-en script section
# (these were added to v5.html but v5-en is built from v3-en which lacks them)
FIT_TO_SCREEN_JS = """// FIT-TO-SCREEN: scale 1600x900 reference frame to fit any viewport
(function fitToScreen(){
  const REF_W = 1600, REF_H = 900;
  function update(){
    const scale = Math.min(window.innerWidth / REF_W, window.innerHeight / REF_H);
    document.documentElement.style.setProperty('--slide-scale', scale.toFixed(4));
  }
  window.addEventListener('resize', update);
  window.addEventListener('orientationchange', update);
  update();
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(update);
  }
})();
"""

if 'fitToScreen' not in v5_en:
    # Inject IIFE right after <script> opening tag
    v5_en = v5_en.replace(
        '<script>\nconst slides',
        '<script>\n' + FIT_TO_SCREEN_JS + 'const slides',
        1
    )

# Inject video-reset logic into goTo function
VIDEO_RESET_JS = """  slides[idx].querySelectorAll('.stat-num[data-target]').forEach(animateCount);
  slides[idx].querySelectorAll('video').forEach(v => {
    try { v.currentTime = 0; const p = v.play(); if (p !== undefined) p.catch(() => {}); } catch(e) {}
  });
  slides.forEach((s, i) => {
    if (i !== idx) s.querySelectorAll('video').forEach(v => { try { v.pause(); } catch(e) {} });
  });"""

if 'currentTime = 0' not in v5_en:
    # Replace the line that animates count with the expanded version
    v5_en = v5_en.replace(
        "slides[idx].querySelectorAll('.stat-num[data-target]').forEach(animateCount);",
        VIDEO_RESET_JS,
        1
    )

# Now insert the NEW v5 pages by extracting them from source v5.html and
# applying the EN translation dictionary.

# Extract opening pages (P2-P4) and new sections (P24-P40) from v5 source
def extract_section(html, start_marker, end_marker):
    """Extract HTML between two comment markers (inclusive of start, exclusive of end)."""
    start = html.find(start_marker)
    end = html.find(end_marker)
    if start == -1 or end == -1:
        return None
    return html[start:end]

# All NEW pages: P2-P4 (opening) and P24-P40 (校本特色 + Q&A)
opening_block = extract_section(text,
    '<!-- ===== P2 v5 講座流程概覽 ===== -->',
    '<!-- ===== P2 全球研究：未來工作劇變 ===== -->')

new_pages_block = extract_section(text,
    '<!-- ===== P24 v5 來年 P1 三班別概覽 ===== -->',
    '<!-- ===== P20 CTA 結語 ===== -->')

qa_block = extract_section(text,
    '<!-- ===== P40 v5 Q&A 問答時間 ===== -->',
    '<script>')

# ============================================================
# V5 NEW PAGES — translation dictionary (sentence/phrase level)
# ============================================================
V5_NATIVE_REWRITES = {
    # === Common terms (high frequency) ===
    "工作坊": "workshops",
    "工作紙": "worksheets",
    "核心詞彙": "Core vocabulary",
    "升小適應": "P1 Onboarding",
    "評估比重": "weight in assessment",
    "簡體中文": "Simplified Chinese",
    "繁體中文": "Traditional Chinese",
    "大主題": "Topics",
    "校本": "School-based",
    "啟發潛能課": "Talent Programme",
    "啟發潛能教育": "Invitational Education",
    "啟發潛能": "Talent Programme",
    "情智教育": "Affective Education",
    "親職教育": "Parent Education",
    "外籍英語": "Native-English",
    "閱讀課": "Reading Class",
    "導修堂": "Tutorial Class",
    "導修": "tutorials",
    "加輔": "additional support",
    "成長": "growth",
    "班營": "class camp",
    "人文": "Humanities",
    "德公": "Civic Ed.",
    "六日循環": "Six-Day Cycle",
    "全日制": "Whole-Day",
    "正規課程": "Core Curriculum",
    "班主任課": "homeroom class",
    "早會": "morning assembly",
    "早操": "morning exercise",
    "午膳": "Lunch",
    "小息": "Break",
    "教師專業發展": "Teacher Professional Development",
    "共同備課": "joint lesson planning",
    "放學": "dismissal",
    "星期一": "Monday",
    "星期二": "Tuesday",
    "星期三": "Wednesday",
    "星期四": "Thursday",
    "星期五": "Friday",
    "全人成長": "Whole-Person Growth",
    "全人發展": "whole-person development",
    "國際視野": "Global Perspective",
    "家校共學": "Home-School Co-Learning",
    "家校共學": "Home-School Co-Learning",
    "親子閱讀": "parent-child reading",
    "情緒娃娃": "emotion plush dolls",
    "情緒識別": "emotion recognition",
    "情緒管理": "emotion regulation",
    "管教技巧": "parenting techniques",
    "解決衝突": "conflict resolution",
    "自我認識": "self-awareness",
    "人際相處": "social skills",
    "互動演繹": "interactive storytelling",
    "親身講故事": "tells stories in person",
    "課室": "classroom",
    "課本": "textbook",
    "招生流程": "Admission Process",
    "招生": "Admission",
    "面試": "interview",
    "面談": "interview",
    "升中": "secondary school transition",
    "升中銜接": "secondary school transition",
    "升中面試": "secondary school interview",
    "課程組": "Curriculum Office",
    "課程統籌": "Curriculum Coordinator",
    "課程統籌主任": "Curriculum Coordinator",
    "主任": "Dean",
    "校長": "Principal",
    "副校": "Vice Principal",
    "課堂": "lessons",
    "科目": "subjects",
    "學年": "academic year",
    "學期": "term",
    "下學期": "spring term",
    "上學期": "autumn term",
    "本校": "Our school",
    "本校": "Our school",
    "對應": "aligned with",
    "推行": "rolled out",
    "推行學年": "Launch Year",
    "取消科目": "Subjects Removed",
    "全港": "Hong Kong-wide",
    "全港小學": "HK primary schools",
    "全港首間": "First in Hong Kong",
    "首間": "first school",
    "第一間": "first school",
    "新分班": "New Streams",
    "三班別": "Three Streams",
    "英尖班": "English Elite Class",
    "博藝班": "Arts & Sports Class",
    "創科班": "AI Innovation Class",
    "英語沉浸式": "English Immersive",
    "英語語境": "English environment",
    "英語沉浸環境": "English-immersive setting",
    "英語話劇": "English drama",
    "英語話劇訓練": "English drama training",
    "英語自信": "English confidence",
    "英語日常活動": "daily English activities",
    "話劇成果": "Drama Showcase",
    "學術英語": "Academic English",
    "日常英語": "Everyday English",
    "學習興趣": "learning interest",
    "學習自主": "Self-directed Learning",
    "學習自信": "learning confidence",
    "學習壓力": "learning stress",
    "課程理念": "Programme Philosophy",
    "三大支柱": "Three Pillars",
    "三大特色": "Three Pillars",
    "三大計劃": "Three Initiatives",
    "三軌": "Three Tracks",
    "三軌並行": "Three Tracks in Parallel",
    "全面評估": "Full Picture Assessment",
    "全面反映能力": "reflect real ability",
    "三層架構": "three-track framework",
    "三層": "three layers",
    "紙筆評估": "Paper & Pen Assessment",
    "紙筆": "Paper & Pen",
    "歷程檔案": "Process Portfolio",
    "實作": "Performance",
    "口頭解說": "Oral Defence",
    "口語表達": "speaking",
    "閱讀理解": "reading comprehension",
    "寫作": "writing",
    "討論": "discussion",
    "課堂表現": "class performance",
    "實作項目": "project work",
    "口語": "speaking",
    "多元評估": "Multi-Track Assessment",
    "多元方法": "diverse methods",
    "AI 代寫": "AI ghostwriting",
    "抗 AI 代寫": "AI-ghostwriting-resistant",
    "代寫": "ghostwriting",
    "演示": "demonstrate",
    "解說": "explain",
    "草稿": "drafts",
    "修改記錄": "revision history",
    "自評": "self-assessment",
    "同學評": "peer assessment",
    "AI 時代": "AI era",
    "AI 時代教育": "AI-era education",
    "終身學習": "lifelong learning",
    "終身學習嘅基石": "the foundation of lifelong learning",
    "AI 倫理": "AI ethics",
    "倫理": "Ethics",
    "紅線": "red lines",
    "邊界": "boundaries",
    "判斷": "judgement",
    "再創造": "re-creation",
    "創造": "creation",
    "應用": "application",
    "創新": "innovation",
    "創意": "creativity",
    "創作": "creation",
    "創客": "Maker",
    "比賽": "competition",
    "比賽中": "in competition",
    "獎項": "awards",
    "獎": "Award",
    "優異獎": "Merit Award",
    "季軍": "Third Place",
    "公開演出": "public performance",
    "音樂修養": "musical skill",
    "團體合作": "teamwork",
    "團體合作精神": "team-spirit",
    "團體紀律": "group discipline",
    "服務精神": "service spirit",
    "區域聯校活動": "inter-school activities",
    "區際": "district-level",
    "學界比賽": "inter-school competitions",
    "重點栽培": "school-championed",
    "明星活動": "Signature Activities",
    "重點精選": "Signature Picks",
    "代表精選": "Signature Picks",
    "由專業導師教授": "led by specialist coaches",
    "專業導師": "specialist coaches",
    "聘專業導師": "trained specialists",
    "並進": "developing in parallel",
    "視藝科融合 AI 創作": "Visual Arts subject integrated with AI creation",
    "AI 創作": "AI creation",
    "AI 動作分析": "AI motion analysis",
    "AI 動作分析輔助訓練": "AI motion analysis supports training",
    "校隊": "school team",
    "AI LAB": "AI LAB",
    "未來 AI 創新者": "future AI innovators",
    "活動 menu": "activity menu",
    "活動": "activities",
    "課外活動": "Extra-curricular Activities",
    "報名通告": "registration notice",
    "報名": "registration",
    "報名截止": "Registration Deadline",
    "額滿即止": "until full",
    "名額有限": "limited places",
    "先到先得": "first-come first-served",
    "面試挑選": "interview selection",
    "面試前": "before the interview",
    "六大類別": "6 Categories",
    "6 大類別": "6 Categories",
    "代表性活動": "representative activities",
    "深入介紹": "deep dive",
    "學生熱門": "student favourites",
    "家長關注": "parent-watched",
    "音樂": "Music",
    "體育": "Sports",
    "視藝": "Visual Arts",
    "STEAM": "STEAM",
    "語言": "Languages",
    "服務及多元": "Service & Beyond",
    "弦樂合奏團": "String Ensemble",
    "鋼琴演奏": "Piano Performance",
    "鋼琴匯演": "piano recital",
    "弦樂團演出": "string ensemble performance",
    "弦樂合奏": "String Ensemble",
    "大提琴": "Cello",
    "小提琴": "Violin",
    "手鐘": "Handbells",
    "合唱團": "Choir",
    "合唱": "Choral Speaking",
    "手鈴": "Tone Chimes",
    "田徑": "Athletics",
    "籃球": "Basketball",
    "排球": "Volleyball",
    "足球": "Football",
    "花式跳繩": "Rope Skipping",
    "跳繩": "Rope Skipping",
    "跆拳道": "Taekwondo",
    "創意繪畫": "Creative Drawing",
    "沙畫": "Sand Art",
    "書法": "Calligraphy",
    "書法及書畫": "Calligraphy & Ink Painting",
    "馬賽克": "Mosaic",
    "校園小畫家": "Junior Artists Club",
    "編程班": "Coding Club",
    "編程": "Coding",
    "STEAM 小精英": "STEAM Elite Team",
    "AI LAB 創作": "AI LAB Creation",
    "劍橋英語": "Cambridge English",
    "英語集誦": "English Choral Speaking",
    "英語集誦 / 集誦": "English Choral Speaking",
    "普通話集誦": "Putonghua Recitation",
    "普通話": "Putonghua",
    "數遊": "Math Games",
    "奧數": "Math Olympiad",
    "珠心算": "Mental Arithmetic",
    "公益少年團": "Community Youth Club",
    "幼童軍": "Cub Scouts",
    "小女童軍": "Brownies",
    "讀書會": "Book Club",
    "Kids for Kids": "Kids for Kids",
    "魔術": "Magic Club",
    "街舞": "Hip-Hop",
    "爵士舞": "Jazz Dance",
    "童軍": "Cub Scouts",
    "童軍合照": "Cub Scouts group photo",
    "童軍 · 公益少年團": "Cub Scouts · Community Youth Club",
    "童軍 / 服務": "Scouts / Service",
    "STEAM 學生創作": "STEAM Students Creating",
    "砌彩色拼圖": "building colourful puzzles",
    "MATATALAB": "MATATALAB",
    "MATATALAB 工作坊": "MATATALAB Workshop",
    "MATATALAB 比賽": "MATATALAB Competition",
    "Matatalab": "MATATALAB",
    "Matatalab 機械人": "MATATALAB robot",
    "Matatalab 課程": "MATATALAB Course",
    "AI Sport 課程": "AI Sport Course",
    "AI Sport": "AI Sport",
    "AI 螢幕": "AI screen",
    "互動運動遊戲": "interactive sports games",
    "運動競技": "sports competition",
    "競賽經驗": "competition experience",
    "建立競賽經驗": "building competition experience",
    "粵語歌": "Cantonese songs",
    "親子歌": "parent-child songs",
    "親子 AI 共創": "Family AI Co-Creation",
    "親子共創": "parent-child co-creation",

    # === P2 講座流程概覽 ===
    "講座流程 · AGENDA": "AGENDA · TODAY'S TALK",
    "今日": "Today's",
    "講座流程": "Programme",
    "7 大主題，每環節時間分配清楚，方便家長跟進。":
        "Seven topics, each timed clearly so you can follow along.",
    "由開場校情速覽，到 AI IN ALL SUBJECTS、來年 P1 新分班、無考默政策、放學後支援、啟發潛能課，最後設問答環節。":
        "From the opening school overview, through AI IN ALL SUBJECTS, next year's new P1 streams, our no-dictation policy, after-school support, and the Talent Programme — capped by an open Q&A.",
    "OPENING · 講座流程": "OPENING · AGENDA",
    "🎬 講座流程概覽 · 校情速覽": "🎬 Agenda Overview · School Snapshot",
    "🤖 AI IN ALL SUBJECTS — 8 大科 AI 教育":
        "🤖 AI IN ALL SUBJECTS — AI Across 8 Subjects",
    "📚 英尖班 English Elite + 來年 P1 新分班":
        "📚 English Elite + 2026-27 New P1 Streams",
    "✏️ 評估安排與無考默政策": "✏️ Assessment & No-Dictation Policy",
    "🏫 功輔班及課後託管": "🏫 Tutorial & After-School Care",
    "🎨 啟發潛能課 + 課外活動 + 升小適應":
        "🎨 Talent Programme · Activities · P1 Onboarding",
    "🎯 總結與問答時間": "🎯 Wrap-Up & Q&A",
    "2 分鐘": "2 min", "13 分鐘": "13 min", "3 分鐘": "3 min",
    "5 分鐘": "5 min", "視情況": "Flexible",
    "主講：": "Speakers: ",
    "許敏詩 校長": "Principal Ms Hui",
    "蕭蕙欣 課程統籌主任": "Dean Siu, Curriculum Coordinator",
    "學年：": "Academic Year: ",

    # === P3 上下午課程編排 ===
    "OPENING · 上下午編排": "OPENING · DAILY RHYTHM",
    "課程編排 · CURRICULUM RHYTHM": "DAILY RHYTHM · CURRICULUM",
    "全日制": "Whole-Day",
    "雙軌節奏": "Two-Track Rhythm",
    "上午紥實正規課程，下午活動與導修並行——每日節奏穩定，學習與探索兼備。":
        "Solid core curriculum in the morning. Activities and tutorials in the afternoon. A steady daily rhythm that balances learning and exploration.",
    "上午 · MORNING": "MORNING",
    "☀️ 正規課程": "☀️ Core Curriculum",
    "8 大科目按教育局指引推進——中文、英文、數學、人文／常識、科學、音樂、體育、視藝，每一科都融入 AI 應用。":
        "Eight subjects taught per EDB guidelines — Chinese, English, Math, Humanities, Science, Music, PE, Visual Arts — each weaving AI applications into the lesson.",
    "配合 P1-P3 奠基期、P4-P6 賦能期螺旋課程設計。":
        "Aligned with the P1-P3 foundation phase and P4-P6 empowerment phase of our spiral curriculum.",
    "下午 · AFTERNOON": "AFTERNOON",
    "🎨 活動 · 導修 · 啟潛": "🎨 Activities · Tutorials · Talent Programme",
    "活動課堂、學科導修、啟發潛能課——每項都有專業導師或科組老師主理。":
        "Activity sessions, subject tutorials, and the Talent Development Programme — each led by specialist coaches or our own subject teachers.",
    "學科鞏固，AI 工具輔助個別差異": "Subject reinforcement, with AI tools supporting individual differences",
    "啟發潛能課：": "Talent Programme: ",
    "多元智能探索，6 年系統設計": "Multiple-intelligences exploration on a six-year roadmap",
    "情智教育 + 親職教育：": "Affective Education & Parent Education: ",
    "全人發展": "whole-person development",
    "午膳及小息共 1 小時，學生有充足休息時間。":
        "Lunch and breaks total one hour — students get plenty of time to rest.",
    "📖 每週特色：閱讀課由外籍英語老師主講故事 · 拓闊國際視野":
        "📖 Weekly Highlight: a native-English teacher leads our reading class — opening up an international perspective.",
    "導修：": "Tutorials: ",

    # === P4 校本特色概覽 ===
    "OPENING · 校本特色": "OPENING · SCHOOL DNA",
    "校本特色 · SCHOOL DNA": "SCHOOL DNA · OUR THREE PILLARS",
    "梁校三大": "LWWF's Three",
    "核心特色": "Core Pillars",
    "學科以外的隱性課程——學會做人、學會學習、學會與家共成長。":
        "What sits beneath the formal curriculum — learning to live, learning to learn, learning to grow alongside family.",
    "特色 ①": "Pillar 1",
    "特色 ②": "Pillar 2",
    "特色 ③": "Pillar 3",
    "情智教育": "Affective Education",
    "每週情智課堂，由班主任及輔導老師帶領，培養情緒管理、人際相處、自我認識。":
        "A weekly Affective Education class, led by class teachers and counsellors — cultivating emotional regulation, social skills, and self-awareness.",
    "對應 OECD「Well-being」框架。":
        "Aligned with the OECD Well-being framework.",
    "外籍英語閱讀課": "Native English Reading",
    "外籍英語老師親身講故事——語境式英語學習，由 P1 開始建立國際視野。":
        "A native-English teacher tells stories in person — immersive English learning that builds an international outlook from P1 onwards.",
    "P1-P6 每週恆常進行。": "Held every week from P1 through P6.",
    "親職教育": "Parent Education",
    "定期家長 workshop、家校通訊、親職講座——家庭與學校無縫共學。":
        "Regular parent workshops, home-school newsletters, and parenting talks — seamless co-learning between home and school.",
    "每學期 2 次以上 workshop。": "At least two workshops per term.",
    "大科目": "Subjects",
    "校本特色": "Core Pillars",
    "六年螺旋": "Six-Year Spiral",
    "新分班年": "New Streaming",

    # === P24 P1 新分班概覽 ===
    "P1 新分班 · 班別概覽": "P1 STREAMS · OVERVIEW",
    "2026-2027 · P1 新分班": "2026-2027 · NEW P1 STREAMS",
    "三班別": "Three Streams,",
    "特色定位": "Distinct Focus",
    "以學生為本，啟發潛能，打造梁校特色課程——除英尖班外，配合時代發展培育 AI 人才。":
        "Student-centred. Talent-driven. LWWF's signature curriculum — beyond English Elite, we're also raising AI talent for the years ahead.",
    "英尖班": "English Elite Class",
    "博藝班": "Arts & Sports Class",
    "創科班": "AI Innovation Class",
    "🎯 目的：": "🎯 Focus: ",
    "打造英語語境，提升學生英語能力。":
        "Build an English-immersive environment to lift students' English ability.",
    "對體藝活動特別有興趣的同學，讓他們發揮所長。":
        "For students with a strong interest in arts and sports — a place to play to their strengths.",
    "對 AI 及電子學習有濃厚的興趣。":
        "For students fascinated by AI and digital learning.",
    "⚡ 特色": "⚡ Features",
    "數學科以英語作為學習語言": "Math taught in English",
    "科學科以英語作為學習語言": "Science taught in English",
    "下學期啟潛課堂進行": "Talent Programme in spring features ",
    "英語話劇訓練": "English drama training",
    "體藝活動訓練": "arts-and-sports training",
    "音樂 · 美術 · 體育綜合培育": "Integrated music, art, and PE development",
    "多元智能配套發展": "Multiple-intelligences support",
    "課室內常駐 ": "Around ",
    "22 部 iPad": "22 iPads kept in the classroom",
    "科學探究加入": "Science inquiry deepens with ",
    "深度 AI 創作": "AI-powered creation",
    "下學期啟潛：": "Spring Talent Programme: ",
    "製作 CHATBOT": "build a CHATBOT",
    " 課程": " unit",
    "資料來源：": "Source: ",
    "2026-2027 年小一班別安排（梁校課程組）":
        "2026-2027 P1 Streaming Arrangement, LWWF Curriculum Office",

    # === P25 P1 分班細節 ===
    "P1 新分班 · 機制細節": "P1 STREAMS · DETAILS",
    "家長意願": "Parent Choice",
    "出入轉班機制": "Class Mobility Rules",
    "尊重家長選擇，並設清晰嘅入學同轉班規則——配合學生實際發展調整。":
        "We respect parents' choice — with clear enrolment and transfer rules to fit each student's real-world development.",
    "家長意願 · PARENT CHOICE": "PARENT CHOICE",
    "👨‍👩‍👧 自由選擇": "👨‍👩‍👧 Free to Choose",
    "A 班（英尖）": "Class A (English Elite)",
    "家長可自由選擇，": "Parents may choose freely. ",
    "需 6 月份進行面試": "A June interview is required",
    "B 班（博藝） + C 班（創科）": "Class B (Arts & Sports) + Class C (AI Innovation)",
    "家長可自由選擇適合自己子女嘅班別。":
        "Parents choose the stream that fits their child. ",
    "如人數太多會面試": "If demand exceeds capacity, interviews will be held",
    "，根據學生實際情況入讀。":
        " — placement is based on each student's circumstances.",
    "📅 6 月面試：A 班所有報讀家長均需出席。":
        "📅 June Interview: required for all Class A applicants.",
    "出入機制 · CLASS MOBILITY": "CLASS MOBILITY",
    "🔄 升班轉班規則": "🔄 Year-to-Year Transfer Rules",
    "🅰️ A 班（英尖）": "🅰️ Class A (English Elite)",
    "P.1 → P.2：": "P.1 → P.2: ",
    "可出可入 ✅": "transfers in and out are open ✅",
    "P.2 → P.3：": "P.2 → P.3: ",
    "可出不可入 ⚠️": "transfers out only ⚠️",
    "（插班生除外）": " (mid-year entrants are an exception)",
    "🅱️🆎 B 班 / C 班（博藝 + 創科）": "🅱️🆎 Class B / C (Arts & Sports + AI Innovation)",
    "P.1-P.3：": "P.1 to P.3: ",
    "可自由出入 ✅": "free movement ✅",
    "P.4-P.6：": "P.4 to P.6: ",
    "按中英數能力": "students are grouped by ability in Chinese, English, and Math for ",
    "分組教學": "differentiated instruction",
    "💡 機制設計：讓學生有發揮機會，亦給家長調整空間。":
        "💡 By design: students get room to shine, and parents get room to adjust.",
    "提醒：": "Note: ",
    "分班並非「能力分流」，而係「興趣定位」——每位學生都有適合發展嘅班別。":
        "Streams are about interest, not ability sorting — every student has a stream that suits them.",

    # === P26 英尖班 概述 ===
    "英尖班 · 概述": "ENGLISH ELITE · OVERVIEW",
    "英尖班 · ENGLISH ELITE　·　Class A": "ENGLISH ELITE · Class A",
    "打造": "Building an",
    "英語沉浸式": "English-Immersive",
    "　學習語境": "Learning Environment",
    "英尖班課堂實況　·　16:9 預留位":
        "English Elite class photo · 16:9 placeholder",
    "科目英授": "Subjects in English",
    "啟動年級": "Starting Grade",
    "家長面試": "Parent Interview",
    "🎯 課程理念": "🎯 Programme Philosophy",
    "透過": "Through ",
    "英語沉浸環境": "English-immersive surroundings",
    "，將英語由「一個科目」轉化為「學習工具」——讓學生喺數學、科學、藝術等真實情境中運用英文，全面提升":
        ", English shifts from being just \"another subject\" to being a learning tool — students use it in math, science, and arts contexts to lift all four areas: ",
    "聽 · 講 · 讀 · 寫": "Listening · Speaking · Reading · Writing",
    "四大能力": "",
    "📚 三大支柱": "📚 Three Pillars",
    "① ": "① ",
    "數學科": "Math",
    " 英語授課": " in English",
    "② ": "② ",
    "科學科": "Science",
    "③ 下學期啟潛課堂 ": "③ Spring Talent Programme: ",
    "英語話劇訓練": "English drama training",
    "💡 為何選擇英尖班？": "💡 Why English Elite?",
    "適合": "For students with ",
    "英文基礎良好、有興趣深入學習": "a solid English foundation and a real interest in going deeper",
    "嘅學生——升中時 EMI（英文授課）中學銜接優勢明顯。":
        " — the transition to EMI (English-medium) secondary schools is notably smoother.",

    # === P27 英尖班 三大特色 ===
    "英尖班 · 三大特色": "ENGLISH ELITE · THREE PILLARS",
    "英授課堂　×　": "EMI Classes ×",
    "話劇訓練": "Drama Training",
    "數學、科學、班務常規——三條主線同步推進，建構完整嘅英語學習生態。":
        "Math, Science, and class routines — three threads moving in step to build a complete English-learning ecology.",
    "數學科英授": "Math in English",
    "課本、工作紙、評估全部以英語為學習語言——讓學生由認識數學概念開始，同時學會英文嘅":
        "Textbook, worksheets, and assessments are all in English — so students learn math concepts and the matching English ",
    "學術用語": "academic vocabulary",
    "（如：addition, subtraction, equation, perimeter）。":
        " (addition, subtraction, equation, perimeter) at the same time.",
    "📊 適合升讀英中（EMI 中學）": "📊 Strong preparation for EMI secondary schools",
    "科學科英授": "Science in English",
    "實驗單元嘅工作紙、評估都以英文進行——學生喺做實驗時自然吸收 ":
        "Lab unit worksheets and assessments are in English — students absorb ",
    " （如：hypothesis, observation, experiment, conclusion）。":
        " (hypothesis, observation, experiment, conclusion) naturally as they do experiments.",
    "🔬 培養科學英語表達能力": "🔬 Develops scientific expression in English",
    "班務 + 英語話劇": "Routines + English Drama",
    "日常班務常規以英語進行——加上": "Daily class routines are run in English — paired with ",
    "下學期啟潛英語話劇訓練": "the spring Talent Programme's drama training",
    "，學生喺真實情境中運用英語，由「會睇會聽」進化為「敢講敢演」。":
        ", students use English in authentic contexts — moving from \"can read, can listen\" to \"dare to speak, dare to perform\".",
    "🎤 提升口語自信": "🎤 Builds spoken confidence",
    "🌐 學年延展：4 年級開始加入英語跨學科 PBL（Project-Based Learning），預備升中銜接。":
        "🌐 As they progress: English cross-subject PBL (Project-Based Learning) starts in P4, preparing students for secondary school.",

    # === P28 英尖班 學習成果 + 家長關注 ===
    "英尖班 · 成果與家長關注": "ENGLISH ELITE · OUTCOMES & FAQ",
    "學習成果　＋　": "Outcomes + ",
    "家長常見疑問": "Common Parent Questions",
    "📈 學習成果 · OUTCOMES": "📈 OUTCOMES",
    "英語自信：": "English Confidence: ",
    "學生敢於以英語表達意見": "students speak up in English without hesitation",
    "學術英語：": "Academic English: ",
    "掌握數理科學專業詞彙": "command of math and science vocabulary",
    "EMI 銜接：": "EMI Pathway: ",
    "升中時可順利適應英文授課中學": "smooth transition into English-medium secondary schools",
    "話劇成果：": "Drama Showcase: ",
    "每年下學期展演": "every spring features a public performance",
    "英語話劇匯演相片　·　16:9 預留位":
        "English drama performance photo · 16:9 placeholder",
    "❓ 我子女英文水平唔夠高，揀英尖班會唔會跟唔上？":
        "❓ My child's English isn't that strong — will English Elite be too tough?",
    "A 班招生着重": "Class A admissions emphasise ",
    "學習興趣": "learning interest",
    "而非「現有水平」——6 月面試會評估學生適應能力。如果中途發現不適應，":
        " over \"current level\". The June interview assesses adaptability. If your child doesn't settle in, ",
    "P.1 升 P.2 階段可以轉去 B / C 班": "you can transfer to Class B or C between P.1 and P.2",
    "。": ".",
    "❓ B / C 班學生會唔會少咗英文資源？":
        "❓ Will Class B/C students get less English exposure?",
    "唔會。": "No. ",
    "英語科本身全校統一": "the English subject itself is identical school-wide",
    "，B / C 班只係": "; Class B and C simply have ",
    "數學、科學": "Math and Science",
    "用中文教。所有班別都有外籍英語老師閱讀課、英語日常活動。":
        " taught in Chinese. All classes still have native-English reading lessons and daily English activities.",
    "❓ 點解 P.2 升 P.3 之後唔可以入英尖班？":
        "❓ Why can't students join English Elite after P.2 → P.3?",
    "因為 P.3 開始": "Because from P.3 onwards, ",
    "英授科目嘅累積知識": "the accumulated knowledge in English-medium subjects",
    "已經唔少（如數學嘅 word problems、科學嘅實驗報告）。中途插入會令學生壓力大。":
        " is substantial (math word problems, lab reports, etc.). Joining mid-stream creates too much pressure. ",
    "插班生例外處理": "Mid-year entrants are handled case-by-case",
    "💡 仍然有疑問？": "💡 Still have questions?",
    "歡迎喺問答環節提出 · 6 月面試前可聯絡課程組詳談。":
        "Bring them to Q&A — or contact our Curriculum Office before the June interview for a detailed chat.",

    # === P29 無考默政策 ===
    "評估革新 · 無考默政策": "ASSESSMENT REFORM · NO-DICTATION POLICY",
    "評估革新 · NO-DICTATION POLICY": "ASSESSMENT REFORM",
    "為何梁校": "Why LWWF",
    "取消傳統考默？": "Dropped Traditional Dictation",
    "由「背誦能力」評估　轉為「應用能力」評估——回應 AI 時代真正需要嘅學習能力。":
        "From assessing memorisation to assessing application — answering what the AI era actually demands.",
    "無考默宣傳片": "No-dictation video",
    "影片 keyframe 預留位（11月17日無考默 V7.mov）":
        "Keyframe placeholder (Nov 17 V7 video)",
    "📌 並非「不再學生字」，而係「不用機械式默寫去評估」。":
        "📌 We're not abandoning vocabulary — we're abandoning rote dictation as the way to assess it.",
    "支柱 ①": "Pillar 1",
    "支柱 ②": "Pillar 2",
    "支柱 ③": "Pillar 3",
    "支柱 ④": "Pillar 4",
    "🔄 減少機械式背誦　·　釋出學習空間":
        "🔄 Less Rote Memorisation · More Room to Learn",
    "將原本俾默書嘅時間，用於": "We redirect dictation time into ",
    "閱讀理解、寫作、討論": "reading comprehension, writing, and discussion",
    "——培養更深層次嘅語文能力。":
        " — building deeper language ability.",
    "💪 減低壓力　·　保護學習興趣":
        "💪 Lower Pressure · Protect the Joy of Learning",
    "傳統默書令學生對中／英文產生": "Traditional dictation breeds ",
    "排斥感": "resistance to Chinese and English",
    "。無考默政策讓學生": ". Without it, students ",
    "持續喜歡學習": "keep loving the language",
    "，係終身學習嘅基石。":
        " — the foundation of lifelong learning.",
    "🤖 AI 時代　·　評估嘅再思考":
        "🤖 The AI Era · Rethinking Assessment",
    "當 AI 可以即時提供答案，": "When AI can produce answers on demand, ",
    "背誦默寫嘅實際價值大幅下降": "the practical value of rote memorisation collapses",
    "——真正重要係": " — what truly matters is ",
    "應用、判斷、創造": "application, judgement, and creation",
    "📊 多元評估　·　全面反映能力":
        "📊 Multi-Track Assessment · Reflects Real Ability",
    "改用": "We use ",
    "閱讀理解、寫作、口語、實作": "reading comprehension, writing, speaking, and project work",
    "等多元方法評估——更貼近真實語言運用能力。":
        " instead — measures that align with real language use.",

    # === P30 無考默 學生家長 ===
    "評估革新 · 學生 + 家長角度": "ASSESSMENT · STUDENT + PARENT VIEWS",
    "無考默 · 學生收穫 + 家長配合":
        "NO-DICTATION · STUDENT GAINS + PARENT ROLE",
    "學生　×　": "Students ×",
    "家長": "Parents",
    "　雙贏": "— A Win-Win",
    "取消傳統考默，並非「家長不用管」——而係家校角色轉變，由「監督背誦」走向「共讀共學」。":
        "Dropping dictation doesn't mean parents step back — it means the role shifts. From supervising memorisation to reading and learning together.",
    "學生角度 · STUDENT": "STUDENT VIEW",
    "😊 收穫": "😊 What They Gain",
    "學習壓力降低": "Lower Learning Stress",
    "，唔再為背默而焦慮": " — no more dictation anxiety",
    "閱讀興趣提升": "Stronger Reading Interest",
    "，由「被迫背」轉為「主動讀」": " — from \"forced to memorise\" to \"choosing to read\"",
    "表達能力進步": "Better Expression",
    "，喺討論、寫作中累積": " — built through discussion and writing",
    "時間更有彈性": "More Flexible Time",
    "，可發展興趣同特長": " — room to pursue interests and strengths",
    "「不再害怕默書日 · 反而期待中文堂」 — 學生分享":
        "\"I no longer dread dictation days — I actually look forward to Chinese class.\" — Student",
    "家長角度 · PARENT": "PARENT VIEW",
    "🤝 角色轉變": "🤝 Shifting Roles",
    "由「監督」轉為「共讀」": "From \"supervising\" to \"reading together\"",
    "，親子閱讀代替默書": " — parent-child reading replaces dictation drilling",
    "用 AI 默書助手": "Use the AI Magic Dictation tool",
    "（v4 P10 介紹）作為自學工具": " (introduced earlier) as a self-study companion",
    "關注學生興趣": "Focus on interest",
    "多於成績數字": " rather than test scores",
    "參與家校 workshop": "Attend home-school workshops",
    "，與孩子共學 AI": " — learn AI alongside your child",
    "家長配合越深入　·　學生收穫越大。":
        "The deeper parents engage, the more students gain.",
    "核心原則：": "Core Principle: ",
    "「無考默」不等於「不評估」——詳見下頁": "\"no dictation\" doesn't mean \"no assessment\" — see the next page on our ",
    "評估三軌進階版": "three-track assessment framework",

    # === P31 評估三軌 ===
    "評估三軌 · 進階版": "ASSESSMENT · THREE-TRACK FRAMEWORK",
    "評估三軌 · ASSESSMENT FRAMEWORK": "THREE-TRACK ASSESSMENT",
    "三軌並行": "Three Tracks,",
    "全面評估": "Full Picture",
    "並非取消評估——而係由「單一紙筆」轉為「三軌並行」，避免 AI 代寫盲點。":
        "We didn't drop assessment — we moved from \"paper-and-pen only\" to three parallel tracks, closing the AI-ghostwriting blind spot.",
    "軌道 ①": "Track 1",
    "軌道 ②": "Track 2",
    "軌道 ③": "Track 3",
    "紙筆評估": "Paper & Pen",
    "傳統測驗、考試保留——測試基本知識掌握、運算技能、書寫能力。":
        "We keep traditional tests and exams — to assess core knowledge, computation, and writing skills.",
    "適用：": "Best for: ",
    "核心概念 · 基礎技能": "core concepts · foundational skills",
    "歷程檔案": "Process Portfolio",
    "收集學生整個學期嘅作品、反思、進度——記錄":
        "Collects a term's worth of work, reflections, and progress — capturing ",
    "學習過程": "the learning journey",
    "而非只看結果。": ", not just the result.",
    "創作 · 寫作 · PBL": "creative work · writing · PBL",
    "實作 + 口頭解說": "Performance + Oral Defence",
    "學生親自演示、解說作品——": "Students demonstrate and explain their own work — ",
    "抗 AI 代寫": "the strongest defence against AI ghostwriting",
    "嘅最有效評估方式。": " we have.",
    "STEAM · 跨科 · AI 創作": "STEAM · cross-subject · AI creation",
    "紙筆不會被取代，但已不足以反映 AI 時代的真實能力。三軌並行，先見學生真正成長。":
        "Paper and pen won't disappear, but alone they no longer measure real ability in the AI era. Three tracks together — that's where you see a student actually grow.",

    # === P32 功輔課託 ===
    "放學後 · 功輔 vs 課託": "AFTER-SCHOOL CARE · TUTORIAL vs DAYCARE",
    "放學後支援 · AFTER-SCHOOL CARE": "AFTER-SCHOOL SUPPORT",
    "功輔班　vs　": "Tutorial vs",
    "課後託管": "After-School Care",
    "兩種放學後支援　·　不同時間 / 服務 / 校車安排——家長按需要自由選擇。":
        "Two after-school options · different hours, services, and school-bus arrangements — choose what fits your family.",
    "項目": "Item",
    "⏰ 時間": "⏰ Hours",
    "📚 服務內容": "📚 Services",
    "🚌 校車服務": "🚌 School Bus",
    "👥 適合對象": "👥 Best For",
    "📝 功輔班": "📝 Homework Tutorial",
    "🏫 課後託管": "🏫 After-School Daycare",
    "下午 3:00 – 4:30": "3:00 – 4:30 PM",
    "下午 3:00 – 6:30": "3:00 – 6:30 PM",
    "放學後 1.5 小時": "90 minutes after dismissal",
    "放學後 3.5 小時": "3.5 hours after dismissal",
    "協助學生": "Helps students ",
    "完成功課": "complete homework",
    "功課輔導 + ": "Homework support + ",
    "溫習": "revision",
    " + ": " + ",
    "茶點": "snacks",
    "遊戲": "games",
    "✅ 提供": "✅ Provided",
    "❌ 不提供": "❌ Not provided",
    "需要功課輔導但要趕校車返屋企嘅學生":
        "Students who need homework help but take the school bus home",
    "需要全面照顧、家長較晚下班嘅家庭":
        "Families who need full after-school care or have late-finishing parents",
    "報名安排：": "Enrolment: ",
    "每學年開學前發放報名通告　·　名額有限以先到先得處理":
        "A registration notice goes out before each school year begins · places are limited, first-come first-served",

    # === P33 啟發潛能 理念 ===
    "啟發潛能 · 理念": "TALENT PROGRAMME · PHILOSOPHY",
    "啟發潛能課 · TALENT DEVELOPMENT": "TALENT DEVELOPMENT PROGRAMME",
    "六年系統": "Six Years,",
    "多元智能": "Multiple Intelligences",
    "　探索": "Explored",
    "啟發潛能課程＝梁校獨有設計——每位學生於 6 年內":
        "The Talent Programme is LWWF's signature design — across six years, every student ",
    "有系統地": "systematically",
    "體驗 8 大智能領域。": " explores all eight intelligence domains.",
    "🌟 核心理念": "🌟 Core Philosophy",
    "「每一位學生都有獨特天賦」——啟發潛能課程旨在":
        "\"Every child has a unique gift.\" The Talent Programme is designed to ",
    "促進不同智能的發展，啟發學生的潛能，盡展所長":
        "develop each intelligence, unlock potential, and let students shine where they're strongest",
    "📚 設計依據": "📚 Design Foundation",
    "根據 Howard Gardner 嘅": "Built on Howard Gardner's ",
    "多元智能理論": "Theory of Multiple Intelligences",
    "，將 8 種智能融入 6 年課程設計——學生於低年級廣泛探索、高年級深入發展。":
        " — eight intelligences mapped across six years. Junior students explore broadly; senior students go deep.",
    "⏰ 課程安排": "⏰ When It Happens",
    "每週固定下午時段——由": "A fixed afternoon slot each week — led by ",
    "專業導師或科組老師": "specialist coaches or our own subject teachers",
    "主理。": ".",
    "8 大智能 · 8 INTELLIGENCES": "EIGHT INTELLIGENCES",
    "💃 肢體動覺": "💃 Bodily-Kinesthetic",
    "🎵 音樂": "🎵 Musical",
    "🎨 空間視覺": "🎨 Spatial",
    "📖 語文": "📖 Linguistic",
    "🔢 數理邏輯": "🔢 Logical-Mathematical",
    "🌳 自然": "🌳 Naturalist",
    "🤝 人際": "🤝 Interpersonal",
    "🪞 內省": "🪞 Intrapersonal",
    "所有 8 種智能於 P1-P6 都會輪流體驗——詳見下頁 P1-P6 發展計劃表。":
        "All eight intelligences rotate through P1 to P6 — see the next page for the detailed roadmap.",
    "教育並不是裝滿一桶水，而是點燃一把火——啟發潛能，就係幫每個學生搵到屬於佢嘅火種。":
        "Education isn't filling a bucket — it's lighting a fire. The Talent Programme helps every student find their spark.",
    "蕭蕙欣主任 · 課程統籌": "— Dean Siu, Curriculum Coordinator",

    # === P34 啟潛 P1-P6 發展表 ===
    "啟發潛能 · 6 年發展表": "TALENT PROGRAMME · 6-YEAR ROADMAP",
    "啟發潛能 · P1-P6 螺旋發展": "TALENT PROGRAMME · P1-P6 SPIRAL",
    "六年級": "Six-Year",
    "發展計劃": "Roadmap",
    "　一覽": "at a Glance",
    "年級": "Grade",
    "發展智能": "Intelligences",
    "配合發展嘅活動": "Matching Activities",
    "一年級": "P.1",
    "二年級": "P.2",
    "三年級": "P.3",
    "四年級": "P.4",
    "五年級": "P.5",
    "六年級 ": "P.6",
    "肢體 / 音樂 / 空間 / 語文": "Bodily · Musical · Spatial · Linguistic",
    "自然 / 空間 / 音樂 / 數理邏輯": "Naturalist · Spatial · Musical · Logical-Math",
    "人際及綜合智能": "Interpersonal & Integrated",
    "花繩": "Cat's Cradle", "彩虹鐘": "Rainbow Bells",
    "創意畫": "Creative Drawing", "日文": "Japanese",
    "躲避盤": "Dodge Disc", "聲藝": "Vocal Arts",
    "黏土繪藝": "Clay Art", "韓文": "Korean",
    "攀石": "Climbing", "非洲鼓": "Djembe",
    "馬賽克砌砌樂": "Mosaic Craft", "手語": "Sign Language",
    "夏威夷小結他": "Ukulele", "魔力橋": "Bridge Building",
    "立體模型創作": "3D Model Making",
    "STEAM 創意活動": "STEAM Creative Sessions",
    "中學體驗活動": "Secondary School Tasters",
    "升中面試活動": "Secondary School Interview Prep",
    "自選活動": "Self-Selected Activities",
    "📊 P1-P3：": "📊 P1-P3: ",
    "廣泛探索（4 大智能輪流）": "broad exploration across four intelligences",
    "🎯 P4：": "🎯 P4: ",
    "加入 STEAM 跨域發展": "STEAM enters the mix",
    "🚀 P5-P6：": "🚀 P5-P6: ",
    "升中銜接 + 自選發展": "secondary-school prep + self-directed growth",

    # === P35 課外活動 6 類 ===
    "課外活動 · 6 類概覽": "EXTRA-CURRICULAR · 6 CATEGORIES",
    "課外活動 · ECA OVERVIEW": "EXTRA-CURRICULAR ACTIVITIES",
    "30+ 課外活動": "30+ Activities,",
    "6 大類別": "6 Categories",
    "課餘時間嘅多元選擇——音樂、體育、視藝、STEAM、語言、服務及多元——總有一項適合你嘅孩子。":
        "Diverse choices for after-class hours — Music, Sports, Visual Arts, STEAM, Languages, Service & Beyond — there's something for every child.",
    "音樂": "Music",
    "6 項 · MUSIC": "6 ACTIVITIES",
    "弦樂合奏 · 大提琴 · 小提琴 · 手鐘 · 合唱團 · 手鈴":
        "String Ensemble · Cello · Violin · Handbells · Choir · Tone Chimes",
    "體育": "Sports",
    "8 項 · SPORTS": "8 ACTIVITIES",
    "田徑 · 籃球 · 排球 · 足球 · 花式跳繩（初中高） · 跆拳道":
        "Athletics · Basketball · Volleyball · Football · Rope Skipping (3 levels) · Taekwondo",
    "視藝": "Visual Arts",
    "5 項 · VISUAL ARTS": "5 ACTIVITIES",
    "創意繪畫（初高體驗班） · 沙畫 · 書法及書畫 · 校園小畫家":
        "Creative Drawing (3 levels) · Sand Art · Calligraphy & Ink Painting · Junior Artists Club",
    "STEAM": "STEAM",
    "3 項 · STEAM": "3 ACTIVITIES",
    "編程班 · STEAM 小精英 · AI LAB 創作":
        "Coding Club · STEAM Elite Team · AI LAB Creation",
    "語言": "Languages",
    "5 項 · LANGUAGES": "5 ACTIVITIES",
    "劍橋英語 · 英語話劇 · 英語集誦 · 普通話集誦 · 數遊／奧數／珠心算":
        "Cambridge English · English Drama · English Choral Speaking · Putonghua Recitation · Math Games / Olympiad / Mental Arithmetic",
    "服務及多元": "Service & Beyond",
    "6 項 · SERVICE": "6+ ACTIVITIES",
    "公益少年團 · 幼童軍 · 小女童軍 · 讀書會 · Kids for Kids · 魔術 · 街舞 · 爵士舞":
        "Community Youth Club · Cub Scouts · Brownies · Book Club · Kids for Kids · Magic Club · Hip-Hop · Jazz Dance",
    "$ = ": "$ = ",
    "由負責老師挑選學生　·　": "by teacher selection · ",
    "# = ": "# = ",
    "興趣小組（自由報名）　·　所有活動聘專業導師訓練":
        "interest group (free sign-up) · all activities led by trained specialists",

    # === P36 課外活動 重點精選 ===
    "課外活動 · 重點精選": "EXTRA-CURRICULAR · SIGNATURE PICKS",
    "明星活動　": "Signature Activities — ",
    "代表精選": "the Showcase",
    "每類選 1 項代表性活動深入介紹——學生熱門、家長關注、學校重點栽培。":
        "One marquee activity per category — student favourites, parent-watched, school-championed.",
    "弦樂團 / 合唱表演相片　·　16:9":
        "String ensemble / choir performance · 16:9",
    "🎻 弦樂合奏團": "🎻 String Ensemble",
    "P3-6 · 每年公開演出 · 培育學生音樂修養及團體合作精神。":
        "P3-6 · annual public performance · nurtures musical skill and ensemble teamwork.",
    "花式跳繩比賽獲獎相片　·　16:9":
        "Rope skipping competition photo · 16:9",
    "🪢 花式跳繩": "🪢 Rope Skipping",
    "P2-6 · 校隊曾獲區際比賽優異獎 · AI 動作分析輔助訓練。":
        "P2-6 · school team has earned district-level merit awards · AI motion analysis supports training.",
    "STEAM 小精英作品相片　·　16:9":
        "STEAM Elite project photo · 16:9",
    "🔬 STEAM 小精英": "🔬 STEAM Elite Team",
    "P4-6 · 喺 AI LAB 進行 · 對接學界比賽如 FUN 享 STEAM、創客大賽。":
        "P4-6 · based in the AI LAB · feeds into inter-school competitions like FUN-Joy STEAM and Maker Showcase.",
    "英語話劇匯演相片　·　16:9":
        "English drama performance photo · 16:9",
    "🎤 英語話劇 · 集誦": "🎤 English Drama · Choral Speaking",
    "P3-6 · 配合英尖班話劇訓練 · 每年公開演出 · 提升口語自信。":
        "P3-6 · pairs with English Elite drama training · annual public showcase · builds spoken confidence.",

    # === P37 升小適應 MATATALAB ===
    "升小適應 · MATATALAB": "P1 ONBOARDING · MATATALAB",
    "由幼稚園　走向　": "From Kindergarten to",
    "小學一年級": "Primary One",
    "梁校為 P1 新生設計專屬": "LWWF offers an exclusive ",
    "升小適應課程": "P1 onboarding curriculum",
    "——以 MATATALAB 實物編程切入，無縫銜接創科班、博藝班、英尖班嘅 STEAM 基礎。":
        " for new P1 students — starting with MATATALAB tangible coding, dovetailing into the STEAM foundations of the AI Innovation, Arts & Sports, and English Elite streams.",
    "Matatalab 工作坊實況相片　·　16:9 預留位":
        "Matatalab workshop photo · 16:9 placeholder",
    "🧱 MATATALAB 工作坊 + 比賽": "🧱 MATATALAB Workshops + Competitions",
    "由實物編程方塊出發——學生未識字之前已經可以「砌出邏輯」，建立 AI 時代必備嘅運算思維。":
        "We begin with tangible coding blocks — before students can read, they're already \"building logic with their hands\", developing the computational thinking the AI era requires.",
    "🌱 為何用 MATATALAB？": "🌱 Why MATATALAB?",
    "P1 學生": "P1 students ",
    "未能讀寫指令": "can't yet read or write commands",
    "——MATATALAB 用": " — MATATALAB swaps code for ",
    "實物方塊代替程式碼": "physical blocks",
    "，學生用手砌出方向、循環、條件——具象化嘅運算思維啟蒙。":
        ". Students assemble direction, loops, and conditions by hand — making computational thinking tangible from day one.",
    "🎯 升小適應目標": "🎯 P1 Onboarding Goals",
    "心理銜接：": "Psychological Bridge: ",
    "建立對學習嘅興趣同自信": "build interest and confidence in learning",
    "技能銜接：": "Skills Bridge: ",
    "運算思維 · 邏輯能力": "computational thinking · logical reasoning",
    "社交銜接：": "Social Bridge: ",
    "分組合作 · 同學互動": "group collaboration · peer interaction",
    "🏆 配套比賽機會": "🏆 Competition Opportunities",
    "參與本港 MATATALAB 同類學界比賽，由 P1 開始累積競賽經驗。":
        "Compete in MATATALAB and similar inter-school events — building experience from P1 onwards.",

    # === P38 升小銜接 5 大支援 ===
    "升小適應 · 銜接安排": "P1 ONBOARDING · FIVE PILLARS",
    "梁校　": "LWWF's",
    "升小銜接": "P1 Onboarding —",
    "　5 大支援": "Five Support Pillars",
    "不只 MATATALAB——梁校為 P1 新生提供 5 個層面嘅銜接支援，幫助學生 + 家長同步適應。":
        "MATATALAB is just the start — LWWF offers five layers of onboarding support so students and parents adjust together.",
    "支援 ①": "Pillar 1",
    "支援 ②": "Pillar 2",
    "支援 ③": "Pillar 3",
    "支援 ④": "Pillar 4",
    "支援 ⑤": "Pillar 5",
    "支援 ⑥": "Pillar 6",
    "小一適應週": "Settling-In Weeks",
    "開學首兩週減慢進度——學生熟悉校園、認識老師、適應全日制節奏。":
        "The first two weeks run at a gentler pace — students learn the campus, meet teachers, and ease into the whole-day rhythm.",
    "MATATALAB 啟蒙": "MATATALAB Introduction",
    "實物編程切入——以遊戲方式啟發運算思維，建立對學習嘅好奇心。":
        "Tangible coding through play — sparks computational thinking and curiosity about learning.",
    "大哥哥大姐姐": "Big Buddies Programme",
    "P5-P6 學長學姐配對 P1 新生——小息陪伴、解答疑問、建立校園歸屬感。":
        "P5-P6 students mentor P1 newcomers — recess company, answers to questions, and a real sense of belonging.",
    "外籍英語閱讀": "Native-English Reading",
    "由 P1 開始接觸英語故事——降低對英語嘅畏懼感，建立聆聽基礎。":
        "English stories from day one — eases anxiety about English and builds listening foundations.",
    "家長同步": "Parent Sync",
    "P1 家長日 + AI 工作坊 + 親職講座——家校同心，學生適應更快。":
        "P1 Parent Day + AI workshops + parenting talks — home and school in sync means a faster transition for students.",
    "情智教育": "Affective Education",
    "每週情智課堂——學會表達情緒、與同學相處、自我認識。":
        "Weekly Affective Education classes — expressing emotions, getting along with peers, knowing oneself.",

    # === P40 Q&A ===
    "Q&A · 問答時間": "Q&A SESSION",
    "問答環節 · Q&A SESSION": "Q&A SESSION",
    "問答時間": "Q&A Time",
    "多謝您今日的參與。": "Thank you for joining us today.",
    "歡迎現場提問　·　亦可會後聯絡我們繼續討論。":
        "We welcome questions now — or feel free to follow up afterwards.",
    "學校": "School",
    "樂善堂梁黃蕙芳紀念學校":
        "Lok Sin Tong Leung Wong Wai Fong Memorial School",
    "網址：": "Website: ",
    "電話：": "Phone: ",
    "學校辦事處": "School Office",
    "校長": "Principal",
    "許敏詩 校長": "Principal Ms Hui",
    "整體校政諮詢": "School-wide policy queries",
    "升小選校面談": "P1 admissions interview",
    "課程統籌": "Curriculum",
    "蕭蕙欣 主任": "Dean Siu",
    "AI 課程 · P1 分班": "AI curriculum · P1 streaming",
    "英尖班 · 啟潛安排": "English Elite · Talent Programme",
    "歡迎提問": "Questions Welcome",
    "YOUR QUESTIONS WELCOME": "YOUR QUESTIONS WELCOME",
    "THANK YOU · 多謝　·　THANK YOU · 多謝":
        "THANK YOU · 多謝 · THANK YOU · 多謝",

    # === Update CTA wording ===
    "下頁 · 問答時間": "Next · Q&A",
    "LWWF · 樂善堂梁黃蕙芳紀念學校 · 2026":
        "LWWF · Lok Sin Tong Leung Wong Wai Fong Memorial School · 2026",

    # === V5 ROUND-3 NEW CONTENT (P2-P40 additions and changes) ===
    # P2 講座流程
    "🎬 講座流程概覽 · 校情速覽": "🎬 Programme Overview · School Snapshot",
    "🤖 AI IN ALL SUBJECTS — 8 大科 AI 教育":
        "🤖 AI IN ALL SUBJECTS — AI Across 8 Subjects",
    "📚 英尖班 English Elite + 來年 P1 新分班":
        "📚 English Elite + Next Year's New P1 Streams",
    "✏️ 評估安排與無考默政策":
        "✏️ Assessment & No-Dictation Policy",
    "🏫 功輔班及課後託管":
        "🏫 Tutorial & After-School Care",
    "🎨 啟發潛能課 + 課外活動 + 升小適應":
        "🎨 Talent Programme · Extra-Curricular · P1 Onboarding",
    "🎯 總結與問答時間":
        "🎯 Wrap-Up & Q&A",

    # P3 上下午
    "2025/26 年度全日制時間表 · TIMETABLE":
        "2025/26 Whole-Day Timetable",
    "2025/26 年度全日制時間表":
        "2025/26 Whole-Day Timetable",
    "全日制　雙軌節奏": "Whole-Day, Two-Track Rhythm",
    "六日循環": "· Six-Day Cycle",
    "上午 6 節正規課（DAY 1-6 循環） + 下午活動 / 導修 / 啟潛——學科紥實，活動豐富，每日節奏穩定。":
        "Six core periods every morning (DAY 1-6 cycle) plus afternoon activities, tutorials, and Talent Programme — solid academics, rich activities, and a steady daily rhythm.",
    "📅 完整時間表": "📅 Full Timetable",
    "DAY 1-6 六日循環　·　每日 6 節正規課（35 分鐘 1 節）":
        "DAY 1-6 cycle · six 35-minute periods each morning",
    "☀️ 上午 8:00-12:40 · 正規課程":
        "☀️ MORNING 8:00-12:40 · Core Curriculum",
    "8:00-8:25：": "8:00-8:25: ",
    "8:25-8:30：": "8:25-8:30: ",
    "8:30-12:40：": "8:30-12:40: ",
    "2 個 20 分鐘小息：": "Two 20-min breaks: ",
    "班主任課 / 早會": "Homeroom / Morning Assembly",
    "第 1-6 節學科課（中 2 節 · 英 2 節）":
        "Periods 1-6 subject classes (Chinese ×2, English ×2)",
    "🍱 12:40-13:40 · 午膳 + 小息":
        "🍱 12:40-13:40 · Lunch + Break",
    "充足 1 小時——飯後休息、操場活動、社交時間。":
        "A full hour — rest, playground time, and social space.",
    "🎨 下午 13:40-15:00 · 多元活動":
        "🎨 AFTERNOON 13:40-15:00 · Activities",
    "班營/成長 + 導修/加輔":
        "Class Camp/Growth + Tutorials",
    "導修/加輔 + 人文/德公":
        "Tutorials + Humanities / Civic Ed.",
    "閱讀課 + 導修堂":
        "Reading Class + Tutorial",
    "13:30 放學 · 教師專業發展時間":
        "13:30 dismissal · Teacher Professional Development",
    "📖 星期三閱讀課由外籍英語老師主講故事 · 星期五教師共同備課 · 學生 13:30 放學":
        "📖 Wednesday Reading led by NET teacher · Friday teachers' joint planning · Students dismissed 13:30",

    # P4 校本特色
    "OPENING · 校本特色": "OPENING · SCHOOL DNA",
    "校本特色 · SCHOOL DNA": "SCHOOL DNA · Three Pillars",
    "梁校三大　核心特色": "LWWF's Three Core Pillars",
    "學科以外的隱性課程——「情智 · 閱讀 · 親職」三條主軸，由 P1 行到 P6，全人成長嘅基石。":
        "The hidden curriculum beyond subjects — Affective, Reading, and Parenting — three throughlines from P1 to P6, the foundation of whole-person growth.",
    "情智 · 閱讀 · 親職": "Affective · Reading · Parenting",
    "三條主軸": "three throughlines",
    "5 學生持 Kimochis 情緒娃娃喺圖書館合照":
        "Five students with Kimochis emotion plush dolls in the library",
    "💙 情智教育": "💙 Affective Education",
    "📖 外籍英語閱讀課": "📖 Native-English Reading",
    "🤝 親職教育": "🤝 Parent Education",
    "每週情智課堂——使用Kimochis 情緒娃娃幫低年級識別情緒、表達感受、學習人際相處。班主任及輔導老師帶領，培養情緒管理。":
        "A weekly Affective class — Kimochis emotion plush dolls help junior students name feelings, express themselves, and learn social skills. Led by class teachers and counsellors to build emotion regulation.",
    "每週情智課堂": "A weekly Affective class",
    "Kimochis 情緒娃娃": "Kimochis emotion dolls",
    "P1-P3：情緒識別 + 表達": "P1-P3: emotion recognition + expression",
    "P4-P6：解決衝突 + 自我認識": "P4-P6: conflict resolution + self-awareness",
    "對應 OECD「Well-being」框架": "Aligned with the OECD Well-being framework",
    "外籍英語老師生動講故事 · 學生互動":
        "Native English teacher tells stories live, engaging students",
    "每週固定時段——外籍英語老師（NET）親身講故事、互動演繹。語境式英語學習，由 P1 開始建立國際視野。":
        "A fixed weekly slot — our Native English Teacher (NET) tells stories in person with interactive delivery. Immersive language learning that builds an international outlook from P1 onward.",
    "每週 1 節（星期四下午）":
        "One period per week (Wednesday afternoon)",
    "動作 · 表情 · 道具配合":
        "Action, expression, and props throughout",
    "P1-P6 全級恆常進行":
        "Held weekly from P1 through P6",
    "配合英尖班英語沉浸環境":
        "Pairs with the English Elite immersion environment",
    "家長 workshop 親職教育講座實況":
        "Parent workshop in session",
    "每星期三下午嘅親職教育時段——定期家長 workshop、親職講座、家校通訊。家庭與學校無縫共學。":
        "Wednesday afternoons host Parent Education — regular workshops, parenting talks, and home-school newsletters. A seamless co-learning loop between home and school.",
    "每星期三下午": "Every Wednesday afternoon",
    "親職教育時段": "Parent Education slot",
    "定期家長 workshop、親職講座、家校通訊":
        "regular parent workshops, parenting talks, and newsletters",
    "家庭與學校無縫共學":
        "seamless home-school co-learning",
    "AI 工作坊（Gemini × Poe）":
        "AI Workshops (Gemini × Poe)",
    "升中／升小銜接講座":
        "Secondary / Primary transition talks",
    "情緒管理與管教技巧":
        "Emotion management & parenting skills",
    "每學期 2-3 次大型講座":
        "2-3 major sessions per term",

    # P24-P25 P1 分班
    "三班別　特色定位": "Three Streams, Distinct Focus",
    "以學生為本，啟發學生潛能，打造梁校特色課程——除英尖班外，配合時代發展培育 AI 人才。":
        "Student-centred and talent-driven — LWWF's signature curriculum. Alongside English Elite, we're raising AI talent for the years ahead.",
    "🎯 目的：": "🎯 Purpose: ",
    "⚡ 特色": "⚡ Features",
    "打造英語語境，提升學生英語能力。":
        "Build an English environment that lifts students' English ability.",
    "對體藝活動特別有興趣的同學，讓他們發揮所長。":
        "For students with strong interest in arts and sports — a place to play to their strengths.",
    "對 AI 及電子學習有濃厚的興趣。":
        "For students fascinated by AI and digital learning.",
    "數學科以英語作為學習語言":
        "Math taught in English",
    "科學科以英語作為學習語言":
        "Science taught in English",
    "下學期啟潛課堂進行":
        "Spring Talent Programme features ",
    "課室內常駐 22 部 iPad":
        "About 22 iPads kept in the classroom",
    "科學探究加入深度 AI 創作":
        "Science inquiry deepened with AI creation",
    "下學期啟潛：製作 CHATBOT 課程":
        "Spring Talent Programme: build a CHATBOT unit",
    "下學期啟潛進行課堂進行體藝活動訓練":
        "Spring Talent Programme features arts-and-sports training",
    "音樂 · 美術 · 體育綜合培育":
        "Integrated music, art, and PE",
    "多元智能配套發展":
        "Multiple-intelligences support",
    "2026-2027 年小一班別安排（梁校課程組）":
        "2026-2027 P1 streaming plan, LWWF Curriculum Office",

    "家長意願　＋　出入轉班機制":
        "Parent Choice + Transfer Rules",
    "尊重家長選擇，並設清晰嘅入學同轉班規則——配合學生實際發展調整。":
        "Parents' choice is respected. Clear admission and transfer rules adapt to each student's actual development.",
    "👨‍👩‍👧 自由選擇": "👨‍👩‍👧 Free to Choose",
    "A 班（英尖）": "Class A (English Elite)",
    "B 班（博藝） + C 班（創科）": "Class B (Arts & Sports) + Class C (AI Innovation)",
    "家長可自由選擇，需 6 月份進行面試。":
        "Parents may choose freely, with a June interview required.",
    "家長可自由選擇適合自己子女嘅班別。如人數太多會面試，根據學生實際情況入讀。":
        "Parents choose the stream that fits their child. If demand exceeds capacity, interviews decide placement.",
    "📅 6 月面試：A 班所有報讀家長均需出席。":
        "📅 June Interview: required for all Class A applicants.",
    "🔄 升班轉班規則": "🔄 Year-to-Year Transfer Rules",
    "🅰️ A 班（英尖）": "🅰️ Class A (English Elite)",
    "可出可入 ✅": "transfers open in and out ✅",
    "可出不可入 ⚠️": "transfers out only ⚠️",
    "（插班生除外）": " (mid-year entrants are an exception)",
    "🅱️🆎 B 班 / C 班（博藝 + 創科）":
        "🅱️🆎 Class B / C (Arts & Sports + AI Innovation)",
    "可自由出入 ✅": "free movement ✅",
    "按中英數能力分組教學":
        "grouped by ability in Chinese, English, and Math for differentiated teaching",
    "💡 機制設計：讓學生有發揮機會，亦給家長調整空間。":
        "💡 By design: students get room to shine; parents get room to adjust.",
    "分班並非「能力分流」，而係「興趣定位」——每位學生都有適合發展嘅班別。":
        "Streams are about interest, not ability sorting — every student has a stream that suits them.",

    # P26-P28 英尖班
    "P1 新分班 · 班別概覽":
        "P1 Streams · Overview",
    "P1 新分班 · 機制細節":
        "P1 Streams · Details",
    "2026-2027 · P1 新分班":
        "2026-2027 · New P1 Streams",
    "英尖班 · 概述":
        "English Elite · Overview",
    "英尖班 · 三大特色":
        "English Elite · Three Pillars",
    "英尖班 · 三大特色 · CORE PILLARS":
        "English Elite · Three Core Pillars",
    "英尖班 · 成果與家長關注":
        "English Elite · Outcomes & FAQ",
    "英尖班 · ENGLISH ELITE　·　Class A":
        "English Elite · Class A",
    "打造　英語沉浸式　學習語境":
        "Building an English-Immersive Learning Environment",
    "一年級數學工作紙：中文版 vs 英文版對照":
        "P1 math worksheets: Chinese vs English versions",
    "📐 數概策略工作紙 · 中 vs 英":
        "📐 Math Concepts Worksheet · 中 vs EN",
    "同一概念，雙語對照——數學概念優先，英語術語同步建立。":
        "Same concept, bilingual side by side — math concepts first, English vocabulary built in step.",
    "科英授": "Subjects in English",
    "啟動年級": "Starting Grade",
    "家長面試": "Parent Interview",
    "🎯 課程理念": "🎯 Programme Philosophy",
    "透過英語沉浸環境，將英語由「一個科目」轉化為「學習工具」——讓學生喺數學、科學等真實情境中運用英文，全面提升聽 · 講 · 讀 · 寫四大能力。學術英語同日常英語並行發展。":
        "Through English immersion, English shifts from \"another subject\" to \"a learning tool\" — used in real Math and Science contexts to lift all four skills: Listening, Speaking, Reading, and Writing. Academic and everyday English develop in step.",
    "聽 · 講 · 讀 · 寫": "Listening · Speaking · Reading · Writing",
    "📚 三大支柱": "📚 Three Pillars",
    "數學科 (Mathematics) 英語授課——課本、工作紙、評估全英文":
        "Math taught in English — textbook, worksheets, and assessments all in English",
    "科學科 (Science) 英語授課——實驗、報告、評估全英文":
        "Science taught in English — experiments, reports, and assessments all in English",
    "下學期啟潛課堂 英語話劇訓練——真實情境運用英語":
        "Spring Talent Programme: English drama training — using English in real situations",
    "💡 為何選擇英尖班？": "💡 Why English Elite?",
    "適合英文基礎良好、有興趣深入學習嘅學生——升中時 EMI（英文授課）中學銜接優勢明顯。學生畢業時已具備跨學科英語能力。":
        "Best for students with a solid English foundation and genuine interest in going deeper — the transition to EMI (English-medium) secondary schools is notably smoother. Graduates already have cross-subject English ability.",
    "📋 招生流程": "📋 Admission Process",
    "家長 6 月份報名 → 學校面試（評估興趣同適應力）→ 8 月入學公布":
        "Parents register in June → school interview (assesses interest and adaptability) → August admissions announcement",

    "英授課堂　×　真實學習": "EMI Classes × Real-World Learning",
    "數學、科學、班務常規——三條主線同步推進，建構完整嘅英語學習生態。":
        "Math, Science, and class routines — three threads moving in step to build a complete English-learning ecology.",
    "2 學生用彩色積木砌數學概念":
        "Two students building math concepts with colored blocks",
    "📐 Mathematics": "📐 Mathematics",
    "🧪 Science": "🧪 Science",
    "🎭 Routines + Drama": "🎭 Routines + Drama",
    "特色 ① · 學科沉浸": "Pillar ① · Subject Immersion",
    "特色 ② · 探究式學習": "Pillar ② · Inquiry-Based",
    "特色 ③ · 真實運用": "Pillar ③ · Real-World Use",
    "課本、工作紙、評估全部英文——學生由認識數學概念開始，同時學會英文嘅學術用語。":
        "Textbook, worksheets, and assessments all in English — students learn math concepts and the matching English academic vocabulary at the same time.",
    "📚 核心詞彙：addition · subtraction · equation · perimeter · fraction · decimal · word problem":
        "📚 Core vocabulary: addition · subtraction · equation · perimeter · fraction · decimal · word problem",
    "📊 升讀 EMI 中學 · 銜接無縫":
        "📊 Smooth EMI secondary school transition",
    "3 學生展示自製火箭實驗作品":
        "Three students showing their handmade rocket experiments",
    "實驗單元嘅工作紙、評估都以英文進行——學生做實驗時自然吸收 scientific vocabulary。":
        "Lab unit worksheets and assessments are in English — students absorb scientific vocabulary naturally as they experiment.",
    "🔬 核心詞彙：hypothesis · observation · experiment · conclusion · variable · measurement":
        "🔬 Core vocabulary: hypothesis · observation · experiment · conclusion · variable · measurement",
    "🚀 真實作品：火箭製作 · 紙箱裝置":
        "🚀 Real projects: rockets, cardboard devices",
    "2 英尖班學生一齊做課室常規":
        "Two English Elite students doing class routines together",
    "日常班務常規以英語進行——加上下學期啟潛英語話劇訓練，學生由「會睇會聽」進化為「敢講敢演」。":
        "Daily class routines are in English — paired with spring English drama training, students move from \"can read and listen\" to \"dare to speak and perform\".",
    "🎤 日常用語：Good morning · May I... · Please pass me... · I would like to share...":
        "🎤 Daily phrases: Good morning · May I... · Please pass me... · I would like to share...",
    "🎬 每年下學期：英語話劇匯演":
        "🎬 Every spring: English drama showcase",
    "🌐 學年延展：P.4 開始加入英語跨學科 PBL（Project-Based Learning），預備升中銜接 · P.5-P.6 升中面試模擬訓練":
        "🌐 As they progress: English cross-subject PBL begins in P.4 to prepare for secondary school · P.5-P.6 includes interview practice",

    "學習成果　＋　家長常見疑問": "Outcomes + Common Parent Questions",
    "📈 學習成果 · OUTCOMES": "📈 OUTCOMES",
    "英語自信：學生敢於以英語表達意見、解答問題":
        "English confidence: students answer and express opinions in English without hesitation",
    "學術英語：掌握 200+ 數理科學專業詞彙":
        "Academic English: 200+ specialized math and science terms mastered",
    "EMI 銜接：升中時順利適應英文授課中學":
        "EMI Pathway: smooth transition into English-medium secondary schools",
    "話劇成果：每年下學期匯演 · 全班參與":
        "Drama Showcase: every spring performance · whole class participates",
    "學習自主：用 AI 工具自學默書、寫作":
        "Self-directed Learning: AI tools for self-study in dictation and writing",
    "Modern Primary Mathematics 1A 課本 · 英文版":
        "Modern Primary Mathematics 1A textbook · English edition",
    "📕 Modern Primary Mathematics 1A": "📕 Modern Primary Mathematics 1A",
    "❓ 我子女英文水平唔夠高，揀英尖班會唔會跟唔上？":
        "❓ My child's English isn't strong enough — will English Elite be too hard?",
    "A 班招生着重學習興趣而非「現有水平」——6 月面試會評估學生適應能力。如果中途發現不適應，P.1 升 P.2 階段可以轉去 B/C 班，無壓力。":
        "Class A admissions value learning interest over current level. The June interview assesses adaptability. If students don't settle in, they can transfer to Class B/C between P.1 and P.2 — no pressure.",
    "❓ B/C 班學生會唔會少咗英文資源？":
        "❓ Will Class B/C students get less English exposure?",
    "唔會。英文科本身全校統一教學時數同教材，B/C 班只係數學、科學用中文教。所有班別都有外籍英語老師閱讀課、英語日常活動。":
        "No. The English subject itself is identical school-wide — same hours, same materials. Class B/C simply have Math and Science taught in Chinese. All classes still have NET reading lessons and daily English activities.",
    "❓ 點解 P.2 升 P.3 之後唔可以入英尖班？":
        "❓ Why can't students join English Elite after P.2 → P.3?",
    "因為 P.3 開始英授科目嘅累積知識已經唔少（數學 word problems、科學實驗報告）。中途插入會令學生壓力大。插班生例外處理。":
        "From P.3 onwards the accumulated knowledge in English-medium subjects is substantial (math word problems, lab reports). Joining mid-stream creates too much pressure. Mid-year entrants are handled case-by-case.",
    "❓ 數學科用英文教，會唔會影響中文數學概念？":
        "❓ Will teaching Math in English affect Chinese math concepts?",
    "唔會。中文版同英文版工作紙內容完全一致（見左圖），老師教課時雙語切換。學生兩種語言嘅數學概念都熟練。":
        "No. The Chinese and English worksheets have identical content (see the photo on the left); teachers switch between languages while teaching. Students master math concepts in both languages.",
    "💡 仍然有疑問？": "💡 Still have questions?",
    "歡迎喺問答環節提出 · 6 月面試前可聯絡課程組蕭主任詳談。":
        "Bring them to the Q&A — or contact Dean Siu in the Curriculum Office before the June interview.",

    # P29-P30 無考默
    "評估革新 · 無考默政策": "ASSESSMENT REFORM · NO-DICTATION POLICY",
    "評估革新 · NO-DICTATION POLICY": "ASSESSMENT REFORM",
    "為何梁校　取消傳統考默？": "Why LWWF Dropped Traditional Dictation",
    "由「背誦能力」評估　轉為「應用能力」評估——回應 AI 時代真正需要嘅學習能力。梁校自 2024-25 學年逐步推行無考默政策，中文、英文科不再用傳統默書作為定期評估。":
        "Moving from \"memorisation testing\" to \"application testing\" — answering what the AI era actually demands. LWWF has rolled out the no-dictation policy since 2024-25; Chinese and English no longer use traditional dictation for regular assessment.",
    "無考默宣傳片": "No-dictation video",
    "影片 keyframe 預留位（11月17日無考默 V7.mov）":
        "Keyframe placeholder (Nov 17 no-dictation V7 video)",
    "並非「不再學生字」": "Not \"no more learning characters\"",
    "而係「不用機械式默寫去評估學生」":
        "but \"no more mechanical dictation to assess students\"",
    "學生仍然要學中文字、識生字、會運用——但唔再用機械式默寫測驗去量度成效。":
        "Students still learn characters, know vocabulary, and use it — we just stop using rote dictation tests to measure progress.",
    "推行學年": "Launch Year",
    "取消科目": "Subjects Removed",
    "中 + 英": "Chinese + English",
    "支柱 ①": "Pillar 1",
    "支柱 ②": "Pillar 2",
    "支柱 ③": "Pillar 3",
    "支柱 ④": "Pillar 4",
    "🔄 釋出學習空間　·　深層發展":
        "🔄 Free Up Learning Space · Go Deeper",
    "將原本俾默書準備同測驗嘅時間，用於閱讀理解、寫作、討論、口語表達——培養更深層次嘅語文能力。香港 2025 年教育局已認可呢個方向。":
        "We redirect dictation prep and test time into reading comprehension, writing, discussion, and speaking — building deeper language ability. Hong Kong's EDB endorsed this direction in 2025.",
    "💪 減低壓力　·　保護學習興趣":
        "💪 Lower Pressure · Protect Learning Interest",
    "傳統默書令學生對中／英文產生排斥感——每週多次默書，分數低就被罰。無考默政策讓學生持續喜歡語文，係終身學習嘅基石。":
        "Traditional dictation breeds resistance to Chinese and English — multiple weekly dictations, with low scores punished. Without it, students keep loving the language — the foundation of lifelong learning.",
    "🤖 AI 時代　·　評估嘅再思考":
        "🤖 The AI Era · Rethinking Assessment",
    "當 AI 可以即時提供答案、自動拼字、語音輸入，純粹「記得字點寫」嘅實際價值大幅下降——真正重要係應用、判斷、創造同分辨 AI 對錯嘅能力。":
        "When AI can answer instantly, auto-spell, and transcribe speech, the practical value of \"remembering how to write a character\" collapses. What matters is application, judgement, creation — and the ability to tell when AI is wrong.",
    "📊 多元評估　·　全面反映能力":
        "📊 Multi-Track Assessment · Reflects Real Ability",
    "改用閱讀理解、寫作、口語表達、課堂表現、實作項目等多元方法評估——更貼近真實語言運用能力。配合 P31 評估三軌進階版。":
        "We use reading comprehension, writing, speaking, class performance, and project work instead — closer to real language ability. See the Three-Track Assessment for details.",

    "評估革新 · 學生 + 家長角度": "ASSESSMENT · Student + Parent Views",
    "無考默 · 學生收穫 + 家長配合":
        "NO-DICTATION · Student Gains + Parent Role",
    "學生　×　家長　雙贏": "Students × Parents — A Win-Win",
    "取消傳統考默，並非「家長不用管」——而係家校角色轉變，由「監督背誦」走向「共讀共學」。":
        "Dropping dictation doesn't mean parents step back — it means roles shift. From supervising memorisation to reading and learning together.",
    "學生角度 · STUDENT": "STUDENT VIEW",
    "😊 收穫": "😊 What They Gain",
    "學習壓力降低，唔再為背默而焦慮":
        "Lower learning stress, no more dictation anxiety",
    "閱讀興趣提升，由「被迫背」轉為「主動讀」":
        "Stronger reading interest — from \"forced to memorise\" to \"choosing to read\"",
    "表達能力進步，喺討論、寫作中累積":
        "Better expression, built through discussion and writing",
    "時間更有彈性，可發展興趣同特長":
        "More flexible time to pursue interests and strengths",
    "「不再害怕默書日 · 反而期待中文堂」 — 學生分享":
        "\"I no longer dread dictation days — I actually look forward to Chinese class.\" — Student",
    "家長角度 · PARENT": "PARENT VIEW",
    "🤝 角色轉變": "🤝 Shifting Roles",
    "由「監督」轉為「共讀」，親子閱讀代替默書":
        "From supervising to reading together — parent-child reading replaces dictation drilling",
    "用 AI 默書助手（v4 P10 介紹）作為自學工具":
        "Use the AI Magic Dictation tool as a self-study companion",
    "關注學生興趣多於成績數字":
        "Focus on interest over test scores",
    "參與家校 workshop，與孩子共學 AI":
        "Attend home-school workshops — learn AI alongside your child",
    "家長配合越深入　·　學生收穫越大。":
        "The deeper parents engage, the more students gain.",
    "「無考默」不等於「不評估」——詳見下頁": "\"No dictation\" doesn't mean \"no assessment\" — see the next page on our ",

    # P31 評估三軌 + P32 功輔課託
    "評估三軌 · 進階版": "Three-Track Assessment · Advanced",
    "評估三軌 · ASSESSMENT FRAMEWORK": "ASSESSMENT FRAMEWORK",
    "評估三軌 · THREE-TRACK ASSESSMENT": "THREE-TRACK ASSESSMENT",
    "並非取消評估——而係由「單一紙筆」轉為「三軌並行」，避免 AI 代寫盲點，真正反映學生能力。":
        "Not abandoning assessment — moving from paper-and-pen alone to three parallel tracks. This closes the AI-ghostwriting blind spot and truly reflects ability.",
    "🔬 實作評估現場": "🔬 Performance Assessment in Action",
    "實作 + 口頭解說 — 學生親自做、親自講，AI 代寫不可能":
        "Performance + Oral Defence — students build and explain it themselves; AI ghostwriting is impossible",
    "軌道 ①": "Track 1",
    "軌道 ②": "Track 2",
    "軌道 ③": "Track 3",
    "知識基礎": "Knowledge Base",
    "學習過程": "Learning Process",
    "真實能力": "Real Ability",
    "紙筆評估 · Paper & Pen": "Paper & Pen",
    "傳統測驗、考試保留——測試基本知識掌握、運算技能、書寫能力。":
        "Traditional tests and exams stay — covering core knowledge, computation, and writing.",
    "適用：": "Best for: ",
    "核心概念 · 基礎技能 · 30-40% 評估比重":
        "core concepts · foundational skills · 30-40% weight",
    "歷程檔案 · Process Portfolio": "Process Portfolio",
    "收集整個學期作品、反思、進度——記錄學習過程而非只看結果。包括草稿、修改記錄、自評同學評。":
        "Collects a term of work, reflections, and progress — capturing the journey, not just the result. Includes drafts, revisions, self- and peer-assessment.",
    "創作 · 寫作 · PBL · 30-35% 評估比重":
        "creative work · writing · PBL · 30-35% weight",
    "實作 + 口頭解說 · Performance + Oral":
        "Performance + Oral Defence",
    "學生親自演示、解說作品——抗 AI 代寫嘅最有效評估。老師可以即場追問點解咁設計、點解咁諗。":
        "Students demonstrate and explain their own work — the strongest defence against AI ghostwriting. Teachers can probe their design decisions on the spot.",
    "STEAM · 跨科 · AI 創作 · 30-35% 評估比重":
        "STEAM · cross-subject · AI creation · 30-35% weight",

    "放學後 · 功輔 vs 課託": "AFTER-SCHOOL CARE · Tutorial vs Daycare",
    "放學後支援 · AFTER-SCHOOL CARE": "AFTER-SCHOOL SUPPORT",
    "功輔班　vs　課後託管": "Tutorial vs After-School Daycare",
    "兩種放學後支援　·　不同時間 / 服務 / 校車安排——家長按需要自由選擇。":
        "Two after-school options · different hours, services, and school-bus arrangements — choose what fits your family.",
    "學生放學後做功課 + iPad 輔助":
        "Students doing homework after school with iPad support",
    "📝 功課輔導 + AI 工具": "📝 Homework Tutoring + AI Tools",
    "放學後仍有專業老師同 AI 輔助學生功課":
        "Teachers and AI continue to support students with homework after school",
    "項目": "Item",
    "⏰ 時間": "⏰ Hours",
    "📚 服務內容": "📚 Services",
    "🚌 校車": "🚌 School Bus",
    "👥 適合對象": "👥 Best For",
    "📝 功輔班": "📝 Tutorial",
    "🏫 課後託管": "🏫 After-School Daycare",
    "下午 3:00 – 4:30": "3:00 – 4:30 PM",
    "下午 3:00 – 6:30": "3:00 – 6:30 PM",
    "放學後 1.5 小時": "90 minutes after dismissal",
    "放學後 3.5 小時": "3.5 hours after dismissal",
    "協助學生完成當日功課　·　老師即時解答疑難":
        "Helps students finish the day's homework · teacher available for questions",
    "功課輔導 + 溫習 + 茶點 + 遊戲　·　全方位照顧":
        "Homework support + revision + snacks + games · full afternoon care",
    "✅ 提供": "✅ Provided",
    "❌ 不提供": "❌ Not provided",
    "需要功課輔導但要趕校車返屋企":
        "Students needing homework help but catching the school bus home",
    "家長較晚下班 · 需要全面照顧":
        "Parents finishing late · students needing full care",
    "📋 報名安排：每學年開學前發放報名通告　·　名額有限以先到先得處理":
        "📋 Registration: a notice is sent before each school year · places are limited and first-come first-served",

    # P33-P34 啟潛
    "啟發潛能 · 理念": "Talent Programme · Philosophy",
    "啟發潛能教育 · INVITATIONAL EDUCATION": "INVITATIONAL EDUCATION",
    "五大元素　啟發潛能": "Five Elements That Invite Potential",
    "梁校嘅啟潛理念建基於國際「啟發潛能教育」框架——以關懷 · 樂觀 · 尊重 · 信任 · 刻意安排五大元素，喚醒每位學生獨特天賦。":
        "Our Talent Programme is built on the international Invitational Education framework — five elements (Care, Optimism, Respect, Trust, Intentionality) to awaken every student's unique gifts.",
    "啟發潛能教育五大元素：關懷 · 樂觀 · 尊重 · 信任 · 刻意安排":
        "Five Elements of Invitational Education: Care · Optimism · Respect · Trust · Intentionality",
    "⭐ 5 ELEMENTS · 學生為中心": "⭐ 5 ELEMENTS · Student-Centred",
    "5P 框架：People · Programs · Policies · Places · Processes":
        "The 5P Framework: People · Programs · Policies · Places · Processes",
    "💜 關懷 · CARE": "💜 CARE",
    "☀️ 樂觀 · OPTIMISM": "☀️ OPTIMISM",
    "🤝 尊重 · RESPECT": "🤝 RESPECT",
    "🌟 信任 · TRUST": "🌟 TRUST",
    "🎯 刻意安排 · INTENTIONALITY": "🎯 INTENTIONALITY",
    "每位學生都應該被看見、被聽見、被理解——老師關懷學生獨特性，建立心理安全感。":
        "Every student deserves to be seen, heard, and understood — teachers honour individuality and build psychological safety.",
    "相信每位學生都有無限可能——失敗只係下一步成功嘅起點，永遠保持希望。":
        "We believe every student has unlimited potential — failure is the next step toward success. Hope, always.",
    "尊重學生嘅選擇、興趣、節奏——唔強迫所有學生喺同一時間掌握同一技能。":
        "We respect each student's choices, interests, and pace — never forcing everyone to master the same skill at the same time.",
    "老師信任學生有自我成長嘅能力——放手讓學生自主探索、自己決定。":
        "Teachers trust students with self-growth — letting go so they can explore and decide for themselves.",
    "所有環境、活動、評估都刻意設計——並非隨機，而係有系統咁啟發每位學生獨有嘅潛能。":
        "Every environment, activity, and assessment is intentionally designed — never random, always systematically inviting each student's unique potential.",
    "教育並不是裝滿一桶水，而是點燃一把火——啟發潛能，就係幫每個學生搵到屬於佢嘅火種。":
        "Education isn't filling a bucket — it's lighting a fire. The Talent Programme helps every student find their spark.",
    "蕭蕙欣主任 · 課程統籌": "— Dean Siu, Curriculum Coordinator",

    "啟發潛能 · 6 年發展表": "Talent Programme · 6-Year Roadmap",
    "啟發潛能 · P1-P6 螺旋發展計劃": "Talent · P1-P6 Spiral Roadmap",
    "六年級　發展計劃　一覽": "The Six-Year Roadmap at a Glance",
    "每位學生於 6 年內系統地體驗 8 大多元智能——由低年級廣泛探索，到高年級深入發展，最後升中銜接。":
        "Every student systematically explores all 8 intelligences across six years — broad exploration in early years, depth in upper years, and a smooth secondary-school transition.",
    "P3 學生攀石活動": "P3 climbing activity",
    "三年級 · 攀石": "P3 · Climbing",
    "P2 學生戶外躲避盤運動": "P2 students playing Dodge Disc outdoors",
    "二年級 · 躲避盤": "P2 · Dodge Disc",
    "P4 學生創意繪畫作品": "P4 creative drawing pieces",
    "四年級 · 創意": "P4 · Creative",
    "年級": "Grade",
    "發展智能": "Intelligences",
    "配合發展嘅活動": "Matching Activities",
    "一年級": "P.1",
    "二年級": "P.2",
    "三年級": "P.3",
    "四年級": "P.4",
    "五年級": "P.5",
    "六年級": "P.6",
    "肢體 / 音樂 / 空間 / 語文":
        "Bodily · Musical · Spatial · Linguistic",
    "自然 / 空間 / 音樂 / 數理邏輯":
        "Naturalist · Spatial · Musical · Logical-Math",
    "人際及綜合智能":
        "Interpersonal & Integrated",
    "花繩 · 彩虹鐘 · 創意畫 · 日文":
        "Cat's Cradle · Rainbow Bells · Creative Drawing · Japanese",
    "躲避盤 · 聲藝 · 黏土繪藝 · 韓文":
        "Dodge Disc · Vocal Arts · Clay Art · Korean",
    "攀石 · 非洲鼓 · 馬賽克砌砌樂 · 手語":
        "Climbing · Djembe · Mosaic Craft · Sign Language",
    "STEAM · 夏威夷小結他 · 魔力橋 · 立體模型":
        "STEAM · Ukulele · Bridge Building · 3D Models",
    "STEAM 創意活動 · 中學體驗活動":
        "STEAM Creative Sessions · Secondary School Tasters",
    "升中面試活動 · 自選活動":
        "Secondary School Interview Prep · Self-Selected",
    "📊 P1-P3 廣泛探索：4 大智能輪流體驗，唔逼學生過早專注":
        "📊 P1-P3 Broad Exploration: four intelligences rotate — no rushed specialisation",
    "🎯 P4 STEAM 啟蒙：加入跨域思維，自然 + 數理邏輯":
        "🎯 P4 STEAM Foundation: cross-domain thinking enters — Naturalist + Logical-Math",
    "🚀 P5-P6 升中銜接：面試訓練 + 自選發展方向":
        "🚀 P5-P6 Secondary Transition: interview practice + self-directed development",

    # P35-P36 課外活動
    "課外活動 · 6 類概覽": "Extra-Curricular · 6 Categories",
    "課外活動 · ECA OVERVIEW": "EXTRA-CURRICULAR ACTIVITIES",
    "30+ 課外活動　6 大類別": "30+ Activities, 6 Categories",
    "課餘時間嘅多元選擇——音樂、體育、視藝、STEAM、語言、服務及多元——總有一項適合你嘅孩子。":
        "Diverse after-school options — Music, Sports, Visual Arts, STEAM, Languages, Service & Beyond — something for every child.",
    "6 項 · MUSIC": "6 ACTIVITIES",
    "8 項 · SPORTS": "8 ACTIVITIES",
    "5 項 · VISUAL ARTS": "5 ACTIVITIES",
    "3 項 · STEAM": "3 ACTIVITIES",
    "5 項 · LANGUAGES": "5 ACTIVITIES",
    "6 項 · SERVICE": "6+ ACTIVITIES",
    "弦樂合奏 · 大提琴 · 小提琴 · 手鐘 · 合唱團 · 手鈴":
        "String Ensemble · Cello · Violin · Handbells · Choir · Tone Chimes",
    "田徑 · 籃球 · 排球 · 足球 · 花式跳繩（初中高） · 跆拳道":
        "Athletics · Basketball · Volleyball · Football · Rope Skipping (3 levels) · Taekwondo",
    "創意繪畫（初高體驗班） · 沙畫 · 書法及書畫 · 校園小畫家":
        "Creative Drawing (3 levels) · Sand Art · Calligraphy & Ink Painting · Junior Artists Club",
    "編程班 · STEAM 小精英 · AI LAB 創作":
        "Coding Club · STEAM Elite Team · AI LAB Creation",
    "劍橋英語 · 英語話劇 · 英語集誦 · 普通話集誦 · 數遊／奧數／珠心算":
        "Cambridge English · English Drama · English Choral Speaking · Putonghua Recitation · Math Games / Olympiad / Mental Arithmetic",
    "公益少年團 · 幼童軍 · 小女童軍 · 讀書會 · Kids for Kids · 魔術 · 街舞 · 爵士舞":
        "Community Youth Club · Cub Scouts · Brownies · Book Club · Kids for Kids · Magic · Hip-Hop · Jazz Dance",
    "由負責老師挑選學生　·　": "Teacher-selected · ",
    "興趣小組（自由報名）　·　所有活動聘專業導師訓練":
        "Free sign-up interest group · all activities led by trained specialists",

    "課外活動 · 重點精選": "Extra-Curricular · Signature Picks",
    "明星活動　代表精選": "Signature Activities · The Showcase",
    "每類選 1 項代表性活動深入介紹——學生熱門、家長關注、學校重點栽培。":
        "One marquee activity per category — student favourites, parent-watched, school-championed.",
    "學生鋼琴匯演 · 弦樂團演出": "Student piano recital · String Ensemble performance",
    "🎻 弦樂合奏團 · 鋼琴演奏": "🎻 String Ensemble · Piano Performance",
    "P3-6 · 每年校內公開演出 · 培育學生音樂修養 + 團體合作精神 · 配合 6 大音樂活動同步發展。":
        "P3-6 · annual public performance · nurtures musical skill and ensemble teamwork · pairs with all 6 music activities.",
    "學生沙畫活動": "Student sand-art session",
    "🏖️ 沙畫 · 創意繪畫": "🏖️ Sand Art · Creative Drawing",
    "P3-6 · 由專業導師教授 · 沙畫、書法、馬賽克、創意繪畫 4 線並進 · 配合視藝科融合 AI 創作。":
        "P3-6 · led by specialist coaches · sand art, calligraphy, mosaic, and creative drawing develop in parallel · integrated with Visual Arts and AI creation.",
    "幼童軍合照": "Cub Scouts group photo",
    "⚜️ 童軍 · 公益少年團": "⚜️ Scouts · Community Youth Club",
    "P3-6 · 幼童軍、小女童軍、公益少年團 · 培育服務精神同團體紀律 · 每年區域聯校活動。":
        "P3-6 · Cub Scouts, Brownies, Community Youth Club · service spirit and discipline · annual inter-school activities.",
    "STEAM 學生創作砌彩色拼圖": "STEAM students assembling colourful puzzles",
    "🧩 STEAM 小精英 · 編程班": "🧩 STEAM Elite Team · Coding",
    "P4-6 · 喺 AI LAB 進行 · 對接學界比賽（FUN 享 STEAM、創客大賽）· 培育未來 AI 創新者。":
        "P4-6 · based in the AI LAB · feeds into inter-school competitions (FUN-Joy STEAM, Maker Showcase) · cultivating future AI innovators.",
    "💡 課外活動報名安排：每學期初發放活動 menu 通告 · 家長可揀 2-3 項 · 部分活動需面試挑選":
        "💡 Registration: an activity menu goes out at the start of each term · parents choose 2-3 activities · some require an interview",

    # P37-P38 升小適應
    "升小適應 · MATATALAB": "P1 Onboarding · MATATALAB",
    "升小適應 · K2/K3 ADAPTATION PROGRAMME":
        "P1 Onboarding · K2/K3 Adaptation Programme",
    "升小適應 · K2/K3 適應課程":
        "P1 Onboarding · K2/K3 Adaptation",
    "由幼稚園　走向　小學一年級": "From Kindergarten to Primary One",
    "梁校專為 K2/K3 學生設計嘅升小適應課程——AI Sport + MATATALAB 實物編程，無縫銜接 A/B/C 三班 STEAM 基礎。":
        "LWWF's exclusive P1 onboarding curriculum for K2/K3 students — AI Sport + MATATALAB tangible coding, dovetailing into the STEAM foundations of Streams A, B, and C.",
    "K2/K3 升小適應課程 poster · AI Sport + Matatalab":
        "K2/K3 P1 Onboarding poster · AI Sport + MATATALAB",
    "🎯 K2/K3 招收中": "🎯 K2/K3 Now Enrolling",
    "活動日期 2026 年 1 月 · 對象 2025-26 K2/K3 學生":
        "Programme date: January 2026 · For 2025-26 K2/K3 students",
    "🤖 AI Sport 課程": "🤖 AI Sport Course",
    "用 AI 螢幕同小朋友玩互動運動遊戲——數據即時回饋，齊齊體驗運動競技嘅樂趣！結合科技 + 體育，啟發 K3 學生對運動嘅興趣。":
        "Children play interactive sports games with an AI screen — live data feedback, the joy of friendly competition. Technology meets PE to spark interest in sports for K3.",
    "🧱 Matatalab 課程": "🧱 MATATALAB Course",
    "學習使用 Matatalab 機械人完成編程任務——喺比賽中完成各種挑戰。K2/K3 已開始接觸運算思維，銜接 P1 創科班。":
        "Children learn to program a MATATALAB robot through challenges in a friendly competition. K2/K3 already encounter computational thinking, easing the path into P1 Class C.",
    "📅 活動詳情": "📅 Programme Details",
    "📝 報名截止：2026/1/16（額滿即止） · 學校會喺活動期間進行拍攝，作活動宣傳之用":
        "📝 Registration closes 2026/1/16 (or until full) · we may photograph during the event for promotional use",

    "升小適應 · 銜接安排": "P1 Onboarding · Support Pillars",
    "升小適應 · 6 大支援": "P1 Onboarding · 6 Support Pillars",
    "梁校　升小銜接　全方位支援": "LWWF's P1 Onboarding · All-Round Support",
    "梁校　升小銜接　5 大支援": "LWWF's P1 Onboarding · Five Support Pillars",
    "不只 MATATALAB——梁校為 P1 新生提供 5 個層面嘅銜接支援，幫助學生 + 家長同步適應。":
        "More than MATATALAB — LWWF offers five layers of support so students and parents adjust together.",
    "MATATALAB Coding for Future 2026 比賽 poster":
        "MATATALAB Coding for Future 2026 competition poster",
    "🏆 MATATALAB 比賽": "🏆 MATATALAB Competition",
    "P1 學生開心上學": "P1 students happy at school",
    "😊 P1 學生": "😊 P1 Students",
    "支援 ①": "Pillar ①",
    "支援 ②": "Pillar ②",
    "支援 ③": "Pillar ③",
    "支援 ④": "Pillar ④",
    "支援 ⑤": "Pillar ⑤",
    "支援 ⑥": "Pillar ⑥",
    "小一適應週": "Settling-In Weeks",
    "MATATALAB 啟蒙": "MATATALAB Introduction",
    "大哥哥大姐姐": "Big Buddies Programme",
    "外籍英語閱讀": "Native-English Reading",
    "家長同步": "Parent Sync",
    "情智教育": "Affective Education",
    "開學首兩週減慢進度——熟悉校園、認識老師、適應全日制節奏。":
        "The first two weeks run at a gentler pace — students learn the campus, meet teachers, and ease into whole-day rhythm.",
    "實物編程切入——遊戲方式啟發運算思維，建立學習好奇心。":
        "Tangible coding through play — sparks computational thinking and curiosity.",
    "P5-P6 學長學姐配對 P1 新生——小息陪伴、解答疑問、建立歸屬感。":
        "P5-P6 mentors pair with P1 newcomers — recess company, answers, and belonging.",
    "P1 起接觸英語故事——降低英語畏懼，建立聆聽基礎。":
        "English stories from P1 — eases anxiety and builds listening foundations.",
    "P1 家長日 + AI 工作坊 + 親職講座——家校同心，適應更快。":
        "P1 Parent Day + AI workshops + parenting talks — home and school in sync.",
    "每週情智課堂——學會表達情緒、與同學相處、自我認識。":
        "Weekly Affective Education — expressing emotions, getting along, knowing oneself.",
    "🎯 我們嘅承諾：每位 P1 新生都會喺 8 月開學前收到「升小適應錦囊」 · 9 月有家長日同學長學姐見面會":
        "🎯 Our commitment: every P1 family receives the P1 Onboarding Kit before August · September features Parent Day and the Big Buddies meet-up",

    # P11 + P20 round-3 changes
    "📐 英尖班數學課程": "📐 English Elite Math Class",
    "📐 乘法大師課堂": "📐 Multiplication Master Class",
    "🏆 家長一同參加大型比賽頒獎禮":
        "🏆 Parents joining the major competition award ceremony",
    "🏆 比賽頒獎": "🏆 Award Ceremony",
    "📘 高年級引入「數字素養課程」":
        "📘 Upper-Grade Digital Literacy Curriculum",
    "P4-P6 每學年用 7 節課堂時間系統地教 AI 素養——配合教育局《小學數字素養架構》。":
        "P4-P6 each year, 7 dedicated periods teach AI literacy systematically — aligned with the EDB Primary Digital Literacy Framework.",
    "第 1 節：": "Lesson 1: ",
    "第 2 節：": "Lesson 2: ",
    "第 3 節：": "Lesson 3: ",
    "第 4 節：": "Lesson 4: ",
    "第 5 節：": "Lesson 5: ",
    "第 6 節：": "Lesson 6: ",
    "第 7 節：": "Lesson 7: ",
    "AI 是甚麼 · 生活中的 AI 應用":
        "What is AI · AI in daily life",
    "AI 點解識答問題 · 訓練數據基礎":
        "How AI answers questions · training data basics",
    "有效 Prompt 寫作技巧": "Effective prompt-writing techniques",
    "AI 倫理 · 紅線與責任": "AI ethics · red lines and responsibility",
    "Fact-check 驗證 AI 答案": "Fact-checking AI responses",
    "AI 跨科應用實作": "Cross-subject AI applications",
    "個人 AI 工具 · 自主學習": "Personal AI tools · self-directed learning",

    # P4 (HK AI) round-3
    "教育局智啟學教計劃 · AI for ALL Subjects 課堂實況":
        "EDB SmartLearn Programme · AI for ALL Subjects classroom",
    "「智」啟學教計劃": "SmartLearn Programme",
    "智啟學教": "SmartLearn",
    "公帑資助學校嘅一筆過撥款，推動「AI for ALL Subjects」全科應用，配合教育局《數字素養架構》校本實踐。本校已申請並全面落實。":
        "A one-off government grant supporting an \"AI for ALL Subjects\" rollout, aligned with the EDB's Digital Literacy Framework. We've applied for it and put it fully to work.",
    "港大 QTN-DT 自主學習研究 · 教師參與探討":
        "HKU QTN-DT self-directed learning research · teachers discussing",
    "人工智能年代的自主學習": "Self-directed learning in the AI era",
    "港大統籌嘅優質教育基金網絡計劃，研究 AI 時代嘅自主學習模式。本校為參與校之一，與全港頂尖學校共同實踐。":
        "An HKU-led Quality Education Fund network programme studying self-directed learning in the AI era. We are one of the participating schools, working alongside Hong Kong's leading schools.",
    "70 校網第一間引入企業級 AI · 教師團隊合照":
        "First in District 70 to adopt enterprise AI · staff group photo",
    "第一間引入企業級 AI": "First to Adopt Enterprise AI",
    "全面採用騰訊青少年人工智能教育平台嘅小學——學生使用嘅工具，與業界企業同步。":
        "The first primary school to fully adopt Tencent's youth AI education platform — students use the same tools as industry.",
    "教育局": "EDB",
    "香港大學": "HKU",
    "70 校網": "District 70",

    # P6 (中文) round-3 bottom strip
    "SSR 將軍卡": "SSR General Card",
    "SR 將軍卡": "SR General Card",
    "八位中華武將：UR 岳飛 · 關羽 · 李靖（左圖全套）　·　右為 SSR / SR 單卡細節":
        "Eight Chinese generals: UR Yue Fei, Guan Yu, Li Jing (full set on left) · SSR / SR individual cards on the right",

    # P40 Q&A round-3
    "Q&A · 問答時間": "Q&A · QUESTIONS WELCOME",
    "問答環節 · Q&A SESSION": "Q&A SESSION",
    "問答時間　·　多謝您嘅出席": "Q&A Time · Thank You for Joining Us",
    "歡迎現場提問　·　亦可會後聯絡校長 / 課程統籌主任繼續討論——梁校歡迎家長與我們同心同行。":
        "Take questions now — or reach out to the Principal and Curriculum Coordinator afterwards. LWWF welcomes parents to walk this journey with us.",
    "🏫 LWWF · 香港屯門": "🏫 LWWF · Tuen Mun, Hong Kong",
    "🏫 樂善堂梁黃蕙芳紀念學校":
        "🏫 Lok Sin Tong Leung Wong Wai Fong Memorial School",
    "電郵：": "Email: ",
    "👩‍🏫 PRINCIPAL": "👩‍🏫 PRINCIPAL",
    "👩‍🏫 許敏詩 Carmen Hui 校長": "👩‍🏫 Principal Carmen Hui",
    "整體校政諮詢": "Whole-school policy queries",
    "升小選校面談": "P1 admissions interview",
    "6 月份 A 班面試主理": "Leads the June Class A interview",
    "📱 WHATSAPP": "📱 WHATSAPP",
    "許校長 WhatsApp Business QR code":
        "Principal Hui's WhatsApp Business QR",
    "📱 校長 WhatsApp 聯絡": "📱 Principal's WhatsApp",
    "掃描 QR code 直接聯絡": "Scan the QR code to message directly",
    "蕭蕙欣主任：AI 課程 · 啟潛 · 英尖":
        "Dean Siu: AI curriculum · Talent · English Elite",
    "歡迎提問": "Questions Welcome",
    "THANK YOU · 多謝　·　LWWF · 2025-26 家長講座":
        "THANK YOU · 多謝 · LWWF · 2025-26 Parent Talk",
}


def is_in_skip_zone(node):
    parent = node.parent
    while parent is not None:
        if parent.name in ('script', 'style'):
            return True
        if parent.get('id') == 'lang-switch':
            return True
        parent = parent.parent
    return False


def translate_new_block(block_html, dict_map):
    """Apply translation dict to a raw HTML block (uses BS4 text-node level)."""
    if not block_html:
        return ""
    soup = BeautifulSoup(block_html, 'html.parser')
    text_nodes = list(soup.find_all(string=True))
    for node in text_nodes:
        if isinstance(node, Comment):
            continue
        if is_in_skip_zone(node):
            continue
        s = str(node)
        new_s = s
        for zh, en in sorted(dict_map.items(), key=lambda x: -len(x[0])):
            if zh in new_s:
                new_s = new_s.replace(zh, en)
        if new_s != s:
            node.replace_with(NavigableString(new_s))
    return str(soup)


# Translate the new blocks
opening_en = translate_new_block(opening_block, V5_NATIVE_REWRITES)
new_pages_en = translate_new_block(new_pages_block, V5_NATIVE_REWRITES)
qa_en = translate_new_block(qa_block, V5_NATIVE_REWRITES)

# Inject opening pages (after cover P1, before P2 全球研究 → before original v4 P2)
# v4-en.html had its comments stripped by BS4 — use section attribute instead.
marker_p2 = '<section class="slide" data-section="RESEARCH · GLOBAL" data-slide="2">'
if marker_p2 in v5_en:
    v5_en = v5_en.replace(marker_p2, opening_en + marker_p2)
else:
    print("WARN: marker_p2 not found")

# Inject new pages (P24-P38) BEFORE v4 CTA section
marker_cta = '<section class="slide" data-section="CTA SESSION" data-slide="20">'
if marker_cta in v5_en:
    v5_en = v5_en.replace(marker_cta, new_pages_en + marker_cta)
else:
    # Try alternative section labels
    alt_ctas = [
        '<section class="slide" data-section="CONCLUSION" data-slide="20">',
        '<section class="slide" data-section="CTA · 結語" data-slide="20">',
        '<section class="slide" data-slide="20" data-section="CTA SESSION">',
        '<section class="slide" data-slide="20" data-section="CTA · 結語">',
        '<section class="slide" data-slide="20" data-section="CONCLUSION">',
    ]
    found = False
    for alt in alt_ctas:
        if alt in v5_en:
            v5_en = v5_en.replace(alt, new_pages_en + alt)
            found = True
            break
    if not found:
        print("WARN: marker_cta not found")

# Update CTA data-slide from 20 to 39 (cover all known orderings)
for old in [
    '<section class="slide" data-section="CONCLUSION" data-slide="20">',
    '<section class="slide" data-section="CTA SESSION" data-slide="20">',
    '<section class="slide" data-section="CTA · 結語" data-slide="20">',
    '<section class="slide" data-slide="20" data-section="CTA · 結語">',
    '<section class="slide" data-slide="20" data-section="CTA SESSION">',
    '<section class="slide" data-slide="20" data-section="CONCLUSION">',
]:
    new = old.replace('data-slide="20"', 'data-slide="39"')
    v5_en = v5_en.replace(old, new)

# Inject Q&A (P40) AFTER CTA section (before </section> + <script>)
marker_pre_script = '</section>\n\n<script>'
if marker_pre_script in v5_en:
    v5_en = v5_en.replace(marker_pre_script, '</section>\n\n' + qa_en + '\n<script>', 1)
else:
    # Try alternate spacing
    alt = '</section>\n<script>'
    if alt in v5_en:
        v5_en = v5_en.replace(alt, '</section>\n\n' + qa_en + '\n<script>', 1)
    else:
        print("WARN: cannot find </section><script> boundary for Q&A injection")

# Apply v5 dict to ALL the content (so any string the v4 base didn't catch
# but the v5 dict knows, gets translated globally)
soup_final = BeautifulSoup(v5_en, 'html.parser')
text_nodes = list(soup_final.find_all(string=True))
for node in text_nodes:
    if isinstance(node, Comment):
        continue
    if is_in_skip_zone(node):
        continue
    s = str(node)
    new_s = s
    for zh, en in sorted(V5_NATIVE_REWRITES.items(), key=lambda x: -len(x[0])):
        if zh in new_s:
            new_s = new_s.replace(zh, en)
    if new_s != s:
        node.replace_with(NavigableString(new_s))

v5_en = str(soup_final)

# Translate data-section attribute values for new pages
SECTION_TRANSLATIONS = {
    'data-section="OPENING · 講座流程"': 'data-section="OPENING · AGENDA"',
    'data-section="OPENING · 上下午編排"': 'data-section="OPENING · DAILY RHYTHM"',
    'data-section="OPENING · 校本特色"': 'data-section="OPENING · SCHOOL DNA"',
    'data-section="P1 新分班 · 班別概覽"': 'data-section="P1 STREAMS · OVERVIEW"',
    'data-section="P1 新分班 · 機制細節"': 'data-section="P1 STREAMS · DETAILS"',
    'data-section="英尖班 · 概述"': 'data-section="ENGLISH ELITE · OVERVIEW"',
    'data-section="英尖班 · 三大特色"': 'data-section="ENGLISH ELITE · THREE PILLARS"',
    'data-section="英尖班 · 成果與家長關注"': 'data-section="ENGLISH ELITE · OUTCOMES &amp; FAQ"',
    'data-section="評估革新 · 無考默政策"': 'data-section="ASSESSMENT · NO-DICTATION"',
    'data-section="評估革新 · 學生 + 家長角度"': 'data-section="ASSESSMENT · STUDENT + PARENT"',
    'data-section="評估三軌 · 進階版"': 'data-section="THREE-TRACK ASSESSMENT"',
    'data-section="放學後 · 功輔 vs 課託"': 'data-section="AFTER-SCHOOL CARE"',
    'data-section="啟發潛能 · 理念"': 'data-section="TALENT · PHILOSOPHY"',
    'data-section="啟發潛能 · 6 年發展表"': 'data-section="TALENT · 6-YEAR ROADMAP"',
    'data-section="課外活動 · 6 類概覽"': 'data-section="ECA · 6 CATEGORIES"',
    'data-section="課外活動 · 重點精選"': 'data-section="ECA · SIGNATURE PICKS"',
    'data-section="升小適應 · MATATALAB"': 'data-section="P1 ONBOARDING · MATATALAB"',
    'data-section="升小適應 · 銜接安排"': 'data-section="P1 ONBOARDING · FIVE PILLARS"',
    'data-section="Q&amp;A · 問答時間"': 'data-section="Q&amp;A SESSION"',
    'data-section="Q&A · 問答時間"': 'data-section="Q&A SESSION"',
}
for zh, en in SECTION_TRANSLATIONS.items():
    v5_en = v5_en.replace(zh, en)

DST_EN.write_text(v5_en, encoding="utf-8")
print(f"OK {DST_EN.name} ({DST_EN.stat().st_size/1024:.0f} KB)")

# Diagnostic
visible = re.sub(r'<script[\s\S]*?</script>', '', v5_en)
visible = re.sub(r'<style[\s\S]*?</style>', '', visible)
visible = re.sub(r'<!--[\s\S]*?-->', '', visible)
chinese_count = len(re.findall(r'[一-龥]', visible))
print(f"  Chinese chars remaining: {chinese_count}")
