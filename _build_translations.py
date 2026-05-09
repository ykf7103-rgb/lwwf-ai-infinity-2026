"""Build v3-cn.html (簡體 OpenCC) + v3-en.html (英文 BS4 text-node level)."""
import re
from pathlib import Path
from opencc import OpenCC
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = Path(__file__).parent
SRC = ROOT / "AI_INFINITY_精選_20頁_v3.html"
DST_CN = ROOT / "AI_INFINITY_精選_20頁_v3-cn.html"
DST_EN = ROOT / "AI_INFINITY_精選_20頁_v3-en.html"

text = SRC.read_text(encoding="utf-8")

# ============================================================
# === 簡體版 (HK 繁體 → 大陸簡體) ===
# ============================================================
cc = OpenCC('hk2s')
cn = cc.convert(text)
cn = cn.replace('<html lang="zh-Hant">', '<html lang="zh-Hans">')
cn = cn.replace('21 頁精選版', '21 页精选版')
cn = cn.replace(
    '<button data-lang="t" class="active" title="繁體中文">繁</button>',
    '<button data-lang="t" title="繁体中文">繁</button>'
)
cn = cn.replace(
    '<button data-lang="s" title="简体中文">简</button>',
    '<button data-lang="s" class="active" title="简体中文">简</button>'
)
DST_CN.write_text(cn, encoding="utf-8")
print(f"✓ {DST_CN.name} ({DST_CN.stat().st_size/1024:.0f} KB)")

# ============================================================
# === 英文版 (BS4 text-node level translation) ===
# ============================================================

# Translation dictionary (phrase-level only, no single chars)
# Format: Chinese phrase → English phrase
TRANSLATIONS = {
    # === Title / Cover ===
    "AI INFINITY · 樂善堂梁黃蕙芳紀念學校 · 21 頁精選版": "AI INFINITY · LWWF · 21-Slide Parent Presentation",
    "樂善堂梁黃蕙芳紀念學校 · 2026 家長簡報": "LWWF · 2026 Parent Presentation",
    "樂善堂梁黃蕙芳紀念學校": "Lok Sin Tong Leung Wong Wai Fong Memorial School",
    "21 頁精選版": "21-Slide Edition",
    "21 页精选版": "21-Slide Edition",
    "無限可能": "Infinite Possibility",
    "無限創造": "Infinite Creation",
    "無限學習": "Infinite Learning",
    "無限未來": "Infinite Future",
    "大科目": "Subjects",
    "校網第一": "1st in District",
    "螺旋課程": "Spiral Curriculum",
    "革新元年": "Launch Year",
    "中文": "Chinese",
    "英文": "English",
    "數學": "Math",
    "人文／常識": "Humanities/GS",
    "人文": "Humanities",
    "科學": "Science",
    "音樂": "Music",
    "體育": "PE",
    "視藝": "Visual Arts",

    # === Section / kicker labels ===
    "OPENING · 開場": "OPENING",
    "RESEARCH · 全球研究": "RESEARCH · GLOBAL",
    "RESEARCH · 必備技能": "RESEARCH · CRITICAL SKILLS",
    "RESEARCH · 香港落實": "RESEARCH · HK ROLLOUT",
    "MATRIX · 趨向矩陣": "MATRIX · TREND MAPPING",
    "中文 · AI 成語攻防戰": "CHINESE · AI Idiom Battle",
    "AI 魔法默書助手": "AI Magic Dictation",
    "校本研發 · AI 魔法默書助手": "School-Developed · AI Magic Dictation",
    "數學 · MATH": "MATH",
    "數學 · MATHEMATICS": "MATHEMATICS",
    "人文 · 樂在其「中」": "HUMANITIES · Joyfully Chinese",
    "人文 · AI 中華文化試身室": "HUMANITIES · AI Cultural Fitting Room",
    "科學 · SCIENCE": "SCIENCE",
    "音樂 · MUSIC": "MUSIC",
    "體育 · PE": "PHYSICAL EDUCATION",
    "體育 · PHYSICAL EDUCATION": "PHYSICAL EDUCATION",
    "視藝 · VISUAL ARTS": "VISUAL ARTS",
    "FLAGSHIP · 旗艦項目": "FLAGSHIP PROJECT",
    "CURRICULUM · 螺旋課程": "CURRICULUM · Spiral Pathway",
    "ETHICS · 倫理 + 評估": "ETHICS + ASSESSMENT",
    "ACHIEVEMENT · 比賽獎項": "AWARDS · COMPETITIONS",
    "ACTION · Workshop": "ACTION · Workshop",
    "FUTURE · 未來藍圖": "FUTURE BLUEPRINT",
    "CTA · 結語": "CONCLUSION",

    # === P2 Research ===
    "全球研究 · WEF 2023": "Global Research · WEF 2023",
    "未來工作的": "The Coming",
    "劇變": "Disruption",
    "當孩子畢業時，世界已經不一樣。": "By the time children graduate, the world has changed.",
    "即將消失": "DISAPPEARING",
    "即將誕生": "EMERGING",
    "技能轉型": "SKILL SHIFT",
    "個工作職位": "jobs",
    "個新工作職位": "new jobs",
    "核心技能五年內被打亂": "of core skills disrupted within 5 years",
    "資料輸入、傳統文書、簡單客服——所有「重複性、規則明確」的工作，AI 完全取代。家長現時鼓勵的「穩定文職」前景，五年內或不存在。":
        "Data entry, traditional clerical work, simple customer service — every \"repetitive, rule-based\" job will be fully replaced by AI. The \"stable office career\" parents currently encourage may not exist in 5 years.",
    "AI 訓練師、Prompt 工程師、人機協作專家、AI 倫理師——新崗位的共通點：需要與 AI 合作、判斷、再創造。":
        "AI trainers, Prompt engineers, Human-AI collaboration specialists, AI ethicists — these new roles share one trait: working with AI, judging, and re-creating.",
    "即孩子未畢業，技能已過時。傳統「考試取分」的訓練再無意義——唯一出路：":
        "Children's skills will be outdated before graduation. Traditional \"exam-cram\" training becomes meaningless — the only path: ",
    "學會「如何學習」": "learn HOW to learn",
    "WEF 預測 2023-2027": "WEF forecast 2023-2027",
    "WEF 新興職位類別": "WEF emerging job categories",
    "WEF Skills Stability Index": "WEF Skills Stability Index",
    "資料來源：": "Source: ",
    "（調查 803 間跨國企業，覆蓋 27 個產業群、46 個經濟體，共 1,130 萬名員工）。":
        " (surveying 803 multinational firms, 27 industry clusters, 46 economies, 11.3 million employees).",
    "World Economic Forum": "World Economic Forum",

    # === P3 Skills ===
    "全球研究 · WEF 2023 + OECD 2030": "Global Research · WEF 2023 + OECD 2030",
    "必備技能": "Critical Skills",
    "五項技能，全部都是 AI 時代教育的核心。":
        "Five skills — all at the core of AI-era education.",
    "分析性思維": "Analytical Thinking",
    "創造力": "Creativity",
    "AI 與大數據素養": "AI & Big Data Literacy",
    "韌性與敏捷": "Resilience & Agility",
    "好奇心 + 主動學習": "Curiosity + Self-Learning",
    "問對問題、拆解複雜情境。AI 給的是答案，但決定問甚麼問題的，仍然是人。":
        "Asking the right questions and breaking down complex situations. AI gives answers, but humans decide which questions to ask.",
    "AI 隨便寫都有 80 分——人類的「品味」與「獨特觀點」是決勝點。創意 = AI 不可取代的稀缺品。":
        "AI scores 80% effortlessly — human \"taste\" and \"unique perspective\" are the decisive edge. Creativity is the scarce trait AI cannot replace.",
    "會用 AI、會質疑 AI、會與 AI 協作。並非「會聊天」，而是能判斷 AI 何時錯、何時可信。":
        "Use AI, question AI, collaborate with AI. Not \"can chat\" — but can judge when AI is wrong and when to trust it.",
    "AI 不懂挫折，學生在失敗中迭代成主角。能在不確定中前進，是 AI 時代最稀缺的特質。":
        "AI knows no setback. Students iterate through failure to become protagonists. Advancing through uncertainty is the rarest trait in the AI era.",
    "AI 永遠取代不了的人類核心特質。好奇心驅動終身學習，是面對 44% 技能過時的唯一保險。":
        "Human traits AI can never replace. Curiosity drives lifelong learning — the only insurance against 44% skill obsolescence.",
    "這些技能　·　全部都是 AI 教育的核心":
        "These skills are all at the core of AI education",
    "本校 AI INFINITY 戰略，正是針對這五項技能逐一設計課程——並非趨勢追隨，而是基於 WEF 與 OECD 的研究依據。":
        "Our school's AI INFINITY strategy is built around these five skills — not trend-chasing, but grounded in WEF and OECD research.",
    "WEF": "WEF",
    "OECD": "OECD",
    "Future of Jobs 2023": "Future of Jobs 2023",
    "，第 38–43 頁「Skills Outlook」章節": ", pp. 38–43 \"Skills Outlook\" chapter",
    "Future of Education and Skills 2030": "Future of Education and Skills 2030",
    "（學習羅盤 2030）": " (Learning Compass 2030)",

    # === P4 HK ===
    "香港本地 · 教育局 + 港大 + 70 校網": "HK Local · EDB + HKU + District 70",
    "香港 AI 教育": "HK AI Education",
    "已經啟動": "Has Already Launched",
    "本校屬於最早的實踐者之一。": "Our school is one of the earliest practitioners.",
    "教育局": "EDB",
    "「智」啟學教計劃": "Smart i-Learn Programme",
    "公帑資助學校的一筆過撥款，推動「AI for ALL Subjects」全科應用，配合教育局《數字素養架構》校本實踐。":
        "Government one-time grant supporting \"AI for ALL Subjects\" rollout, aligned with the EDB Digital Literacy Framework.",
    "本校已申請並全面落實。": "Our school has applied and fully implemented.",
    "香港大學": "The University of Hong Kong",
    "人工智能年代的自主學習": "Self-Directed Learning in the AI Era",
    "港大統籌的優質教育基金網絡計劃，研究 AI 時代的自主學習模式。":
        "HKU-led Quality Education Fund network programme studying AI-era self-learning models.",
    "本校為參與校之一": "Our school is one of the participating schools",
    "，與全港頂尖學校共同實踐。": ", co-practising with top schools across Hong Kong.",
    "70 校網": "District 70",
    "校網": "District",
    "第一間引入企業級 AI": "First to adopt enterprise-grade AI",
    "全面採用": "Fully adopting ",
    "騰訊青少年人工智能教育平台": "Tencent Youth AI Education Platform",
    "的小學——學生使用的工具，與業界企業同步。":
        " — students use the same tools as industry.",
    "EARLY MOVER · 早期實踐者": "EARLY MOVER",
    "本校早幾年已是": "Our school has been a ",
    "賽馬會 CoolThink@JC 運算思維教育的先導學校": "Jockey Club CoolThink@JC pilot school for years",
    "，並非 AI 教育的新手——而是香港 AI 教育最早期的實踐者。在這個基礎上，我們持續更新工具、優化教法。":
        ", not a newcomer to AI education — but one of HK's earliest practitioners. On this foundation, we continue to update tools and refine pedagogy.",
    "香港教育局「智啟學教」計劃（2024 年公布）": "HK EDB \"Smart i-Learn\" Programme (announced 2024)",
    "香港大學優質教育基金 QTN-DT 網絡計劃名單": "HKU Quality Education Fund QTN-DT Network list",
    "騰訊青少年人工智能教育平台合作學校紀錄": "Tencent Youth AI Education Platform partner-school records",
    "賽馬會 CoolThink@JC 先導學校歷年名單": "Jockey Club CoolThink@JC pilot-school list",

    # === P5 Matrix ===
    "8 大科 × 未來對應": "8 Subjects × Future Mapping",
    "每一科都有": "Every subject has",
    "明確的未來定位": "a clear future direction",
    "科目": "Subject",
    "對應未來趨向": "Future Trend",
    "校本實踐": "School Practice",
    "文化傳承 + AI 倫理素養": "Cultural Heritage + AI Ethics",
    "UNESCO 以人為本 + Critical Thinking": "UNESCO Human-centred + Critical Thinking",
    "P4 狐假虎威新編（課程）；成語攻防戰（組別作）": "P4 Fox-Tiger Reimagined (curriculum); Idiom Battle (group)",
    "全球溝通 + 個人化學習普及": "Global Communication + Personalised Learning",
    "OECD 學習能動性（Agency）": "OECD Learning Agency",
    "AI 默書助手（家長 Workshop）；升中銜接": "AI Dictation Assistant (Parent Workshop); Secondary Transition",
    "系統思維 + 數據素養": "Systems Thinking + Data Literacy",
    "Bloom 2 Sigma 個人化突破": "Bloom 2 Sigma Personalisation",
    "乘法大師（P4 課程）；漫畫變身器（組別作）；蘇格拉底反問": "Multiplication Master (P4); Comic Generator (group); Socratic Questioning",
    "國民身份認同 + 跨文化理解": "National Identity + Cross-Cultural",
    "教育局《價值觀教育架構》": "EDB Values Education Framework",
    "一帶一路 fact-check（課程）；樂在其「中」（季軍）；文化試身室": "Belt & Road fact-check; Joyfully Chinese (3rd place); Cultural Fitting Room",
    "五感體驗 + STEM 探究": "Sensory Experience + STEM Inquiry",
    "Hattie d=0.50 探究式學習": "Hattie d=0.50 inquiry learning",
    "識花君（P6 課程）；生態保育體驗日；國寶 AI 管家": "Plant ID (P6); Conservation Day; National Treasure AI Steward",
    "美學素養 + AI 共創": "Aesthetics + AI Co-Creation",
    "UNESCO 創意表達 + 親子協作": "UNESCO Creative Expression + Family Collaboration",
    "「水果月」親子 AI 歌曲創作活動（Suno + Padlet）": "Fruit Month Family AI Song (Suno + Padlet)",
    "健康素養 + IoT 數據時代": "Health Literacy + IoT Data Age",
    "WHO 兒童活動指引 + 數據分析": "WHO Children-Activity Guidelines + Data Analytics",
    "AI 國寶守衛戰（P5 課程）；AI 智能體育系統（試行）": "AI National Guardian (P5); AI Sport System (Pilot)",
    "創造力 + 文化保育": "Creativity + Heritage",
    "21 世紀核心技能 4C（Creativity）": "21st-Century 4C (Creativity)",
    "現代門神（P5 課程）；未來職業 APP（P6 畢業生涯規劃）": "Modern Door Gods (P5); Future Career APP (P6 Graduation Planning)",

    # === P6 Chinese ===
    "中文 · AI 成語攻防戰": "Chinese · AI Idiom Battle",
    "將學中文　變成": "Turn Learning Chinese into",
    "卡牌對戰": "a Card Battle",
    "玩法": "Gameplay",
    "學生輸入成語造句 → AI": "Students input idiom sentences → AI",
    "10 分制評分": "10-point scoring",
    "→ 滿分 20% 機率抽出": "→ 20% chance of drawing",
    "UR 將軍卡": "a UR General Card",
    "（岳飛、關羽、李靖），結合品德教育。": " (Yue Fei, Guan Yu, Li Jing), combined with character education.",
    "評分四維度": "Scoring Dimensions",
    "語法 3": "Grammar 3",
    "用詞 3": "Diction 3",
    "豐富度 2": "Richness 2",
    "創意 2": "Creativity 2",
    "= 10 分": "= 10 pts",
    "🏆 全港小學優異獎　·　103 件作品中獲選": "🏆 HK Primary Merit Award · selected from 103 entries",

    # === P7 Dictation ===
    "校本研發 · AI 魔法默書助手": "School-Developed · AI Magic Dictation",
    "老師 + Gemini　共同研發": "Teachers + Gemini · Co-developed",
    "校本默書工具": "School Dictation Tool",
    "老師 × Gemini　共創": "Teachers × Gemini · Co-creation",
    "由本校老師與 Gemini 一同以": "Developed jointly by our teachers and Gemini using ",
    "自然語言": "natural language",
    "開發——無需編程經驗，將老師對教學的理解，變成可即用的工具。":
        " — no coding experience required, turning teachers' pedagogical insight into ready-to-use tools.",
    "P2-P4 自學默書": "P2-P4 Self-Learn Dictation",
    "為低小設計：": "Designed for lower primary: ",
    "學校預設默書範圍自動填入": "school-presets auto-fill",
    "。學生自行選範圍、由 AI 朗讀、即時批改——讓孩子在家也能":
        ". Students self-select scope, AI reads aloud, instant grading — children can ",
    "自學溫書": "self-study at home",
    "兩種模式": "Two Modes",
    "詞語默書": "Word Dictation",
    "：AI 生成故事 + 圖卡輔助記憶": ": AI-generated stories + flashcards",
    "智能讀默 / 背默": "Smart Read / Recite",
    "：逐句聽聲、隱藏文字": ": sentence-by-sentence audio, hidden text",
    "解決家長痛點": "Solving Parent Pain Points",
    "家長唔再需要逐字讀默——AI 永不疲倦、隨時聽寫、永遠耐心。":
        "Parents no longer need to read aloud — AI never tires, available anytime, infinitely patient.",
    "家長 30 分鐘": "Parents · 30 mins",
    "親手做出默書 App": "Build dictation app yourself",

    # === P8 Math ===
    "破解 70 年難題": "Cracking the 70-Year Problem",
    "2 Sigma 個人化": "2 Sigma Personalisation",
    "P4 課程：乘法大師": "P4 Curriculum: Multiplication Master",
    "高年級學生寫 AI 程式": "Senior students write AI programs",
    "，回饋低年級——P5/P6 學生親手做出乘法練習工具，俾 P2 同學使用。":
        " for juniors — P5/P6 students build multiplication practice tools for P2 students to use.",
    "蘇格拉底反問": "Socratic Questioning",
    "AI 不直接給答案，而係反問：「點解咁諗？仲有其他方法嗎？」訓練批判思維。":
        "AI doesn't give answers but asks back: \"Why think this way? Any other approaches?\" Training critical thinking.",
    "數學漫畫變身器": "Math Comic Generator",
    "學生親手畫角色 → AI 生成": "Students draw characters by hand → AI generates ",
    "四格漫畫解題": "4-panel comic solutions",
    " → 學生親自講解（fact-check）。": " → students explain and fact-check.",
    "數學 × 中文 × 視藝 × 科技": "Math × Chinese × Arts × Tech",
    "融合。": " integration.",
    "研究依據：": "Research basis: ",
    "Bloom (1984)": "Bloom (1984)",
    "The 2 Sigma Problem": "The 2 Sigma Problem",
    "——一對一導師可令學生表現由 50 百分位升至 98 百分位。":
        " — 1-on-1 tutoring lifts students from the 50th to 98th percentile.",

    # === P9 Lokjoy ===
    "由 App Inventor　到": "From App Inventor to",
    "AI 集換卡": "AI TCG Cards",
    "由電腦堂": "From Computer class ",
    "AI 中華文化「樂在其中」App": "AI \"Joyfully Chinese\" Cultural App",
    "·　三個世代演進": " · Three generations of evolution",
    "第一代　·　奠基": "Gen 1 · Foundation",
    "App Inventor": "App Inventor",
    "由電腦堂起步——學生用 MIT App Inventor 圖像化編程砌出初代文化遊戲。奠基期嘅編程訓練。":
        "Starting from Computer class — students use MIT App Inventor visual coding to build first-generation cultural games. Foundation-era coding training.",
    "第二代　·　全港季軍": "Gen 2 · HK 3rd Place",
    "樂在其「中」App": "Joyfully Chinese App",
    "融合 AI 重新詮釋中華文化。": "Reinterpreting Chinese culture with AI. ",
    "全港 500 隊中榮獲季軍": "3rd place out of 500 teams HK-wide",
    "第三代　·　最新": "Gen 3 · Latest",
    "由 App 升級為實體 + AI 卡牌系統——學生輸入成語造句，AI 即場評分抽出 SSR / SR 武將卡。":
        "Upgraded from App to physical + AI card system — students input idiom sentences, AI scores live and draws SSR / SR General cards.",
    "真正的文化傳承，並非令學生變成歷史的旁觀者，而是令他們成為文化的再創造者。":
        "True cultural inheritance is not turning students into historical bystanders, but into culture's re-creators.",
    "校長許敏詩 · RTHK 訪問": "Principal Hui · RTHK Interview",
    "校長許敏詩": "Principal Ms Hui",
    "RTHK 訪問": "RTHK Interview",
    "RTHK 開場致詞": "RTHK Opening Speech",

    # === P9b Cultural Fitting Room ===
    "人工智能": "Artificial Intelligence",
    "帶你穿越時空": "takes you through time and space",
    "即場試身　·　即場拍照": "Live Try-On · Live Photo",
    "AI 攝影機 + 大電視介面，學生站到鏡頭前——AI 即時將學生「換上」民族服飾（藏族、苗族、蒙古族）背景，化身古代人物。":
        "AI camera + large screen interface — student stands before the camera, AI instantly \"dresses\" them in ethnic costumes (Tibetan, Miao, Mongolian) backgrounds.",
    "超越教科書嘅文化體驗": "Beyond Textbook Cultural Experience",
    "由「閱讀文化」轉為「親身穿戴」——對應教育局《價值觀教育架構》。學生帶走自己嘅試身相，回家延續分享。":
        "From \"reading culture\" to \"personally wearing\" — aligned with the EDB Values Education Framework. Students take home their try-on photos to share.",
    "教育意義": "Educational Significance",
    "AI 並非取代真實服飾體驗，而係降低門檻——令每位學生都能跨越時空，與多元文化產生個人連結。":
        "AI doesn't replace the real costume experience, but lowers the barrier — letting every student bridge time and connect personally with diverse cultures.",

    # === P10 Science ===
    "由實驗報告　走向": "From Lab Reports to ",
    "真實世界探究": "Real-World Inquiry",
    "P6 課程：識花君": "P6 Curriculum: Plant ID Master",
    "學生於校園花圃使用 AI 植物識別 App，整合即場觀察、AI 工具、分類學知識——對應 Hattie d=0.50 探究式學習。":
        "Students use the AI plant ID app in the school garden, integrating live observation, AI tools, and taxonomic knowledge — Hattie d=0.50 inquiry learning.",
    "AI 生態保育體驗日": "AI Conservation Day",
    "透過親身接觸阿達伯拉象龜，配合 AI 物種辨識工具——學生由保育的旁觀者，轉為實際參與者。":
        "Through hands-on encounter with the Aldabra giant tortoise paired with AI species ID — students transform from conservation bystanders into participants.",
    "旗艦項目：國寶 AI 管家": "Flagship: National Treasure AI Steward",
    "校內領養瑤山鱷蜥（中國一級保護動物，全球瀕危）。配合 IoT 感應器與 AI 監測系統。":
        "School adopts the Yaoshan crocodile lizard (China's Class-1 protected, globally endangered). Combined with IoT sensors and an AI monitoring system.",
    "詳見 P14 旗艦頁。": "See the Flagship page.",
    "識花君影片": "Plant ID Video",

    # === P11 Music ===
    "由樂理練習　走向": "From Music Theory to ",
    "親子 AI 共創": "Family AI Co-creation",
    "「水果月」親子 AI 歌曲創作": "\"Fruit Month\" Family AI Song",
    "家長與學生使用 Suno AI 共創粵語歌曲，主題以水果與生活營養為核心。學習成果上載 Padlet 平台與全校分享——家長由「監督者」轉為「共學夥伴」。":
        "Parents and students co-create Cantonese songs with Suno AI, themed on fruits and nutrition. Results uploaded to Padlet for school-wide sharing — parents transform from \"supervisors\" into \"co-learning partners\".",
    "由消費者　變成作者": "From Consumer to Author",
    "當學生發現自己「會作歌」，對音樂的熱情會由被動變為主動。AI 並非取代創作，而是降低創作的門檻——對應 UNESCO 創意表達框架。":
        "When students discover they \"can compose\", their passion for music turns from passive to active. AI doesn't replace creation but lowers the barrier — aligned with UNESCO's creative expression framework.",
    "音樂科以前係欣賞與演唱為主，難以讓學生親身體驗創作。Suno 改變了這一切。":
        "Music used to focus on appreciation and singing — hard for students to experience real creation. Suno changes everything.",
    "音樂科組": "Music Department",

    # === P12 PE ===
    "由動作示範　走向": "From Demos to ",
    "IoT 數據體育": "IoT Data PE",
    "P5 課程：AI 國寶守衛戰 2.0": "P5 Curriculum: AI National Guardian 2.0",
    "學生跳繩動作觸發 AI 視覺辨識，跳繩次數轉化為「清潔氣流大砲」嘅能量，擊退污染怪獸——將枯燥嘅體能訓練變成國寶守衛任務。":
        "Students' rope-skipping triggers AI vision recognition, jump counts become \"clean-air cannon\" energy defeating pollution monsters — turning fitness training into a national-treasure guardian mission.",
    "AI 智能體育系統（試行）": "AI Smart Sport System (Pilot)",
    "於體育館設置大電視 AI 視覺辨識，可實時計算跳繩次數、跳遠距離——對應 WHO 兒童活動指引嘅數據素養要求。":
        "Large-screen AI vision installed in the gym calculates rope-skips and long-jumps in real time — meeting WHO children-activity guideline data literacy requirements.",
    "並非監測　而是賦能": "Not Surveillance, but Empowerment",
    "系統強調個人改善，而非全班排名——避免學生因比較而產生運動焦慮。資料只供個人參考，":
        "The system emphasises personal improvement, not class ranking — avoiding peer-comparison anxiety. Data for personal reference only, ",
    "不寫心跳血氧、不點名比較": "no heart-rate/oxygen logging, no naming",

    # === P13 VA ===
    "由臨摹練習　走向": "From Imitation to ",
    "文化保育與創新": "Heritage + Innovation",
    "P5 課程：現代門神": "P5 Curriculum: Modern Door Gods",
    "學生先以傳統水墨手繪稿構思角色，再使用 AI 工具將其轉化為動態作品——傳統與創新並非對立，而係互相成就。對應 21 世紀 4C 核心技能。":
        "Students first draft characters with traditional ink, then use AI tools to transform them into dynamic works — tradition and innovation aren't opposites but complement each other. Aligned with 21st-Century 4C skills.",
    "P6 課程：未來職業 APP": "P6 Curriculum: Future Career APP",
    "畢業生涯規劃融入視藝——學生為自己嘅未來職業設計 APP 介面草圖，再用 AI 完善視覺呈現。":
        "Graduation career planning integrated with visual arts — students design APP interface drafts for their future careers, then refine the visuals with AI.",
    "創意 × 自我認同": "Creativity × Self-Identity",
    "AI 不會取代畫筆，但會擴闊學生對「創作」的想像。我們的責任，是教他們判斷哪個版本最有自己的靈魂。":
        "AI doesn't replace the brush but expands students' imagination of \"creation\". Our duty: teach them to judge which version has their own soul.",
    "張楚雯老師 · 視藝科": "Ms Cheung · Visual Arts",
    "現代門神影片": "Modern Door Gods Video",
    "原稿　·　手繪": "Original · Hand-drawn",
    "AI　·　未來職業": "AI · Future Career",
    "原稿": "Original",
    "AI 完成": "AI Final",

    # === P14 Flagship ===
    "旗艦項目 · FLAGSHIP": "FLAGSHIP PROJECT",
    "國寶 AI 管家": "National Treasure AI Steward",
    "瑤山鱷蜥": "Yaoshan Crocodile Lizard",
    "中國一級保護動物　·　全球瀕危品種": "China Class-1 Protected · Globally Endangered Species",
    "真實國寶": "Real National Treasure",
    "本校為香港少數獲准合法領養的小學。": "One of few HK primary schools legally permitted to adopt.",
    "IoT 智能監測": "IoT Smart Monitoring",
    "溫度、濕度、光照感應器實時上傳。": "Temperature, humidity, and light sensors upload in real time.",
    "AI 行為辨識": "AI Behaviour Recognition",
    "攝影機辨識日常行為，記錄健康狀況。": "Cameras recognise daily behaviour, logging health.",
    "跨學科融合": "Cross-Disciplinary",
    "科學 + STEAM + 人文 + 資訊科技。": "Science + STEAM + Humanities + IT.",
    "校內主理：": "School lead: ",
    "蕭蕙欣主任、楊錦鋒老師": "Dean Siu, Mr Yeung",
    "合作單位：": "Partner: ",
    "瑤山鱷蜥保育協會": "Yaoshan Lizard Conservation Society",

    # === P15 Curriculum ===
    "課程架構 · CURRICULUM": "CURRICULUM",
    "P1-P6": "P1-P6",
    "螺旋式雙階段": "Two-Stage Spiral",
    "階段一　·　P1-P3 奠基期": "Stage 1 · P1-P3 Foundation",
    "運算思維 + AI 啟蒙": "Computational Thinking + AI Intro",
    "透過遊戲化、具象化操作（如 Matatalab 實物編程），培養學生最底層的邏輯解難能力。":
        "Through gamified, hands-on operations (e.g. Matatalab tangible coding), cultivating foundational logical problem-solving.",
    "P1-P3 暫未引入生成式 AI，保護兒童早期認知發展。":
        "Generative AI is not yet introduced in P1-P3, protecting early cognitive development.",
    "階段二　·　P4-P6 賦能期": "Stage 2 · P4-P6 Empowerment",
    "企業 AI + 跨科 PBL": "Enterprise AI + Cross-Subject PBL",
    "全面引入企業級 AI 工具，進行深度跨學科實作。":
        "Full enterprise-grade AI rollout with deep cross-disciplinary projects.",
    "狐假虎威 ·": "Fox-Tiger Idiom · ",
    "狐假虎威": "Fox-Tiger Idiom",
    "乘法大師": "Multiplication Master",
    "現代門神": "Modern Door Gods",
    "AI 翻譯官": "AI Translator",
    "識花君": "Plant ID Master",
    "畢業生涯規劃": "Career Planning",
    "學生組別 / 比賽作品（成語攻防戰、文化試身室、國寶 AI 管家等）係課餘自主探究。":
        "Student-group / competition works (Idiom Battle, Cultural Fitting Room, National Treasure Steward) are extracurricular self-inquiry.",

    # === P16 Ethics ===
    "AI 倫理 · 評估革新": "AI ETHICS · ASSESSMENT REFORM",
    "引入 AI": "Introducing AI",
    "必有清晰邊界": "Requires Clear Boundaries",
    "紅線一：絕不取代人的判斷": "Red Line 1: Never replace human judgement",
    "AI 是輔助與啟發，老師與學生的判斷永遠優先。":
        "AI assists and inspires; teacher and student judgement always prevail.",
    "紅線二：絕不輸出未驗證的事實": "Red Line 2: Never output unverified facts",
    "學生必須學會 fact-check，事實準確性的最終責任在作者本人。":
        "Students must learn to fact-check; ultimate accuracy is the author's responsibility.",
    "評估三層架構": "3-Layer Assessment",
    "紙筆": "Paper-pen",
    "歷程檔案": "Process Portfolio",
    "實作 + 口頭解說": "Demo + Oral Explanation",
    "——三軌並行，避免流於 AI 代寫。":
        " — three tracks in parallel, avoiding AI ghostwriting.",
    "紙筆不會被取代，但已不足以反映 AI 時代的真實能力。":
        "Paper-pen isn't replaced, but no longer reflects true AI-era capability.",

    # === P17 Awards ===
    "比賽成果 · ACHIEVEMENT": "ACHIEVEMENTS",
    "學生作品": "Student Works",
    "已獲外界認可": "Recognised by Industry",
    "CHAMPIONSHIP　·　季軍": "BRONZE MEDAL",
    "樂在其「中」": "Joyfully Chinese",
    "全港小學中華文化教育比賽　·　500 隊參賽中榮獲季軍。":
        "HK Primary Chinese Culture Education Competition · 3rd place out of 500 teams.",
    "EXCELLENCE　·　優異獎": "MERIT AWARD",
    "AI 成語攻防戰": "AI Idiom Battle",
    "國民身份認同應用程式設計比賽　·　103 件作品中獲選。":
        "National Identity App Design Competition · selected from 103 entries.",
    "GLOBAL　·　走出香港": "GLOBAL · Beyond HK",
    "BETT London 2026": "BETT London 2026",
    "本校代表將於倫敦 BETT 教育科技展。": "Our representatives at the London BETT EdTech Expo.",

    # === P18 Workshop ===
    "家長賦能 · WORKSHOP": "PARENT EMPOWERMENT · WORKSHOP",
    "家長不止是旁觀者": "Parents Aren't Just Bystanders",
    "您也是 AI 創造者": "You're an AI Creator Too",
    "AI 時代超級家長": "AI-Era Super Parent",
    "「Gemini × Poe 實戰工作坊」——輕鬆引導孩子自主學習。家長由零編程基礎開始，30 分鐘做出自己孩子嘅 AI 默書 App。":
        "\"Gemini × Poe Hands-On Workshop\" — easily guide children's self-learning. Starting from zero coding, parents build their child's AI dictation app in 30 minutes.",
    "定期舉行": "Held Regularly",
    "每學期最少兩次，配合學生課程進度——確保家長嘅 AI 知識同學校同步。":
        "At least twice per term, aligned with student curriculum — keeping parents' AI knowledge in sync with the school.",
    "唔只技術　·　更係溝通": "Not Just Tech · It's Communication",
    "家長親手做過先理解 AI 唔係魔法。家中嘅 AI 對話從此有質素、有界線。":
        "Hands-on practice lets parents understand AI isn't magic. Home AI conversations now have quality and boundaries.",

    # === P19 Future ===
    "未來藍圖 · FUTURE": "FUTURE BLUEPRINT",
    "下一步": "Next Step",
    "三大計劃": "Three Plans",
    "AI Garden": "AI Garden",
    "校園常設展示空間，匯集歷屆學生 AI 作品——由概念漫畫到完整應用。":
        "Permanent campus showcase gathering all students' AI works — from concept comics to full apps.",
    "5G 智慧蝴蝶園": "5G Smart Butterfly Garden",
    "5G IoT 感應園，學生實時觀察生態數據——溫度、濕度、物種辨識實時上載。":
        "5G IoT sensing garden, real-time eco-data — temperature, humidity, species ID live-upload.",
    "家長賦能 2.0": "Parent Empowerment 2.0",
    "由「會用 AI」昇華為「會教 AI」——家長與學生共同學習，建立深度連結。":
        "From \"using AI\" to \"teaching AI\" — parents and students learn together, building deep connections.",

    # === P20 CTA ===
    "結語 · CTA": "CONCLUSION",
    "由科技的消費者": "From Consumers of Technology",
    "轉為真實世界的創造者": "to Creators in the Real World",
    "希望每位學生都能由「科技的消費者」": "We hope every student transforms from a \"tech consumer\"",
    "慢慢變成「能用科技解決真實問題的創造者」。":
        " into \"a creator who solves real problems with tech\".",
    "多謝您今日的出席": "Thank You for Joining Us Today",
    "LWWF · 樂善堂梁黃蕙芳紀念學校": "LWWF · Memorial School",

    # === Nav / chrome ===
    "← → 切換": "← → Navigate",
    "F 全屏": "F Fullscreen",
    "繁體中文": "Traditional Chinese",
    "繁体中文": "Traditional Chinese",
    "簡體中文": "Simplified Chinese",
    "简体中文": "Simplified Chinese",
    "封面": "Cover",
    "預告": "Preview",
    "課程架構": "Curriculum",
    "倫理": "Ethics",
    "評估": "Assessment",
    "比賽": "Competitions",
    "未來": "Future",
    "結語": "Conclusion",

    # Section tag fragments
    "OPENING": "OPENING",
    "RESEARCH": "RESEARCH",
    "MATRIX": "MATRIX",

    # Common short tokens
    "稍後": "later",
    "稍後補相": "(photos coming later)",
    "稍後補照片": "(photos coming later)",

    # === Short phrases (cover leftover fragments) ===
    "國民身份認同　·　跨文化理解": "National Identity · Cross-Cultural",
    "國民身份認同": "National Identity",
    "國民身份認同頒獎典禮全體合照": "National Identity Award Ceremony group photo",
    "默書助手　·　升中銜接": "Dictation Assistant · Secondary Transition",
    "默書助手": "Dictation Assistant",
    "升中銜接": "Secondary Transition",
    "季軍）　·　文化試身室": "3rd place) · Cultural Fitting Room",
    "季軍": "3rd Place",
    "新編　·　成語攻防戰": "Reimagined · Idiom Battle",
    "新編": "Reimagined",
    "成語攻防戰": "Idiom Battle",
    "學生玩成語攻防戰桌遊": "Students playing Idiom Battle",
    "學生持文化試身室相": "Student with Cultural Fitting Room photos",
    "岳飛、關羽、李靖": "Yue Fei, Guan Yu, Li Jing",
    "文化試身室實況": "Cultural Fitting Room live",
    "文化試身室": "Cultural Fitting Room",
    "水果月」親子": "Fruit Month\" Family",
    "水果月": "Fruit Month",
    "輸入成語造句": "Input idiom sentences",
    "歌曲頒獎合照": "Song award photo",
    "歌曲創作平台": "Song creation platform",
    "歌曲": "Songs",
    "學生跳繩戶外": "Students rope-skipping outdoors",
    "校長與學生": "Principal with students",
    "學習能動性": "Learning Agency",
    "漫畫變身器": "Comic Generator",
    "生態保育日": "Conservation Day",
    "國寶守衛戰": "National Guardian",
    "試身室攤位": "Fitting Room booth",
    "試身室": "Fitting Room",
    "實戰工作坊": "Hands-on Workshop",
    "工作坊": "Workshop",
    "文化傳承": "Cultural Heritage",
    "五感體驗": "Sensory Experience",
    "美學素養": "Aesthetics",
    "健康素養": "Health Literacy",
    "數據時代": "Data Age",
    "文化保育": "Heritage",
    "編程課堂": "Coding class",
    "實物編程": "Tangible coding",
    "學生展示": "Students presenting",
    "教博合照": "Education Expo group photo",
    "將軍卡": "General Card",
    "機率抽": "chance to draw",
    "第一代": "Gen 1",
    "第二代": "Gen 2",
    "第三代": "Gen 3",
    "學生持": "Student with",
    "大電視": "Large screen",
    "鱷蜥盒": "Lizard box",
    "學生用": "Student using",
    "年的": " ",
    "框架": "framework",
    "素養": "literacy",
    "突破": "breakthrough",
    "探究": "inquiry",
    "共創": "Co-creation",
    "BETT UK 2026 攤位": "BETT UK 2026 booth",
    "AI 集換卡網頁": "AI TCG cards web app",
    "SSR 將軍卡": "SSR General Card",
    "SR 將軍卡": "SR General Card",
    "AI 魔法默書助手 web app 介面": "AI Magic Dictation web app interface",
    "乘法大師課堂": "Multiplication Master class",
    "數學漫畫變身器作品": "Math Comic Generator output",
    "第一代 App Inventor 編程課堂": "Gen 1 · App Inventor coding class",
    "第二代 樂在其「中」攤位": "Gen 2 · Joyfully Chinese booth",
    "第三代 AI 集換卡": "Gen 3 · AI TCG cards",
    "學生持文化試身室相 + 攤位": "Student with Cultural Fitting Room photos + booth",
    "學生持 iPad + 國寶 AI 管家展板": "Student with iPad + National Treasure AI Steward booth",
    "水果月 AI 歌曲頒獎合照": "Fruit Month AI Song award photo",
    "水果月 Padlet 親子 AI 歌曲創作平台": "Fruit Month Padlet Family AI Song platform",
    "大電視 AI 體育系統": "Large-screen AI Sport System",
    "學生跳繩戶外體育堂": "Students rope-skipping outdoors",
    "學生原稿手繪": "Student original hand-drawn",
    "AI 完成嘅未來職業卡": "AI-completed Future Career card",
    "國寶 AI 管家攤位 + 5 學生 + 鱷蜥盒 + 大電視": "National Treasure AI Steward booth + 5 students + lizard box + screen",
    "P1-P3 Matatalab 實物編程": "P1-P3 · Matatalab tangible coding",
    "P4 課程 · 狐假虎威新編四格漫畫": "P4 · Fox-Tiger Reimagined comic",
    "學生用 ThinkPad AI 設計": "Student designing with AI on ThinkPad",
    "學生展示 Magnetic Car AI 作品": "Student presenting Magnetic Car AI work",
    "2024 國民身份認同頒獎典禮全體合照": "2024 National Identity Award Ceremony",
    "BETT UK 2026 攤位": "BETT UK 2026 booth",
    "家長 Workshop 實況": "Parent Workshop live",
    "AI 時代超級家長 Gemini × Poe 工作坊": "AI-Era Super Parent · Gemini × Poe Workshop",
    "AI 時代超級家長 Gemini × Poe 實戰工作坊": "AI-Era Super Parent · Gemini × Poe Hands-on Workshop",
    "AI Garden 學生作品": "AI Garden student works",
    "校園生態池": "Campus eco-pond",
    "家長賦能 5G": "Parent Empowerment 5G",
    "LWWF 學生 + 教師 + 教博合照": "LWWF students + teachers · Education Expo",
    "LWWF 校長與學生": "LWWF Principal with students",
    "Gemini × Poe 實戰工作坊": "Gemini × Poe Hands-on Workshop",
    "親子 AI 歌曲": "Family AI Songs",
    "親子": "Family",
    "親手": "Hands-on",
    "親自": "personally",
    "即場": "live",
    "抽出": "draw",
    "草圖": "draft",
    "資訊科技": "IT",
    "資訊": "Information",
    "智能": "Smart",
    "系統": "System",
    "數據": "Data",
    "融入": "integrated",
    "設計": "design",
    "再用": "then use",
    "視覺辨識": "vision recognition",
    "保育協會": "Conservation Society",
    "蕭蕙欣主任": "Dean Siu",
    "楊錦鋒老師": "Mr Yeung",
    "張楚雯老師": "Ms Cheung",
    "校內主理": "School lead",
    "合作單位": "Partner",
    "歷年名單": "historical list",
    "先導學校": "pilot school",
    "中央": "centre",
    "中華文化": "Chinese culture",
    "中華": "Chinese",
    "教育的": "education's ",
    "新手": "newcomer",
    "最早期": "earliest",
    "實踐者": "practitioner",
    "持續更新工具": "continually update tools",
    "優化教法": "refine pedagogy",
    "我們": "We",
    "公帑資助": "Government-funded",
    "一筆過撥款": "one-time grant",
    "全科應用": "all-subject deployment",
    "推動": "to promote",
    "配合": "aligned with",
    "並非": "Not",
    "而是": "but",
    "章節": "chapter",
    "公布": "announced",
    "公佈": "announced",
    "合作": "partnership",
    "紀錄": "records",
    "賽馬會": "Jockey Club",
    "先導": "pilot",
    "教育博覽": "Education Expo",
    "學生作品": "student works",
    "比賽攤位": "competition booth",
    "獎座": "trophy",
    "頒獎禮": "award ceremony",
    "簡報": "presentation",
    "21 世紀": "21st-Century",
    "核心技能": "core skills",
    "校外": "external",
    "校內": "internal",
    "校本": "school-based",
    "成果展示": "achievements showcase",
    "優質": "quality",
    "攤位": "booth",
    "展示": "showcase",
    "頒獎": "award",
    "頒獎典禮": "award ceremony",
    "典禮": "ceremony",
    "公開": "public",
    "最近": "recent",
    "最新": "latest",
    "早期": "early",
    "先驅": "pioneer",
    "滿分": "Full marks",
    "職業": "Career",
    "未來職業": "Future Career",
    "未來職業 APP": "Future Career APP",
    "默書": "Dictation",
    "萬": "0,000",
    "代": "Gen",
    "由": "From ",
    "係": " ",
    "嘅": " ",
    "唔": "not ",
    "嗰": "that",
    "呢": "this",
    "畀": "give",
    "啱": "right",
    "嗰陣": "when",
    "返": " ",
    "睇": "see",
}


# === BS4 walk ===
soup_en = BeautifulSoup(text, 'html.parser')

# Update lang attribute and title
if soup_en.html and soup_en.html.get('lang') == 'zh-Hant':
    soup_en.html['lang'] = 'en'
if soup_en.title:
    soup_en.title.string = "AI INFINITY · LWWF · 21-Slide Parent Presentation"

# Mark "EN" lang button as active and remove "繁" active
for btn in soup_en.find_all('button', attrs={'data-lang': True}):
    classes = btn.get('class', [])
    if btn['data-lang'] == 't':
        btn['class'] = [c for c in classes if c != 'active']
        btn['title'] = 'Traditional Chinese'
    elif btn['data-lang'] == 'e':
        if 'active' not in classes:
            classes.append('active')
        btn['class'] = classes
        btn['title'] = 'English'

# Translate alt attributes
for img in soup_en.find_all('img'):
    alt = img.get('alt')
    if alt and alt in TRANSLATIONS:
        img['alt'] = TRANSLATIONS[alt]
    elif alt:
        # Try partial matches
        translated = alt
        for zh, eng in sorted(TRANSLATIONS.items(), key=lambda x: -len(x[0])):
            if zh in translated:
                translated = translated.replace(zh, eng)
        img['alt'] = translated.strip()

# Translate data-section attributes
for tag in soup_en.find_all(attrs={'data-section': True}):
    sec = tag['data-section']
    if sec in TRANSLATIONS:
        tag['data-section'] = TRANSLATIONS[sec]
    else:
        translated = sec
        for zh, eng in sorted(TRANSLATIONS.items(), key=lambda x: -len(x[0])):
            if zh in translated:
                translated = translated.replace(zh, eng)
        tag['data-section'] = translated.strip()


# Get the slide container only — skip script/style/lang-switch button text
def is_in_skip_zone(node):
    """Don't translate text inside script/style/lang-switch."""
    parent = node.parent
    while parent is not None:
        if parent.name in ('script', 'style'):
            return True
        if parent.get('id') == 'lang-switch':
            return True
        parent = parent.parent
    return False


def translate_text_node(text):
    """Apply translations to a single text node."""
    if not text or not text.strip():
        return text
    # Apply longest-first to avoid partial-match clobbering
    for zh, eng in sorted(TRANSLATIONS.items(), key=lambda x: -len(x[0])):
        text = text.replace(zh, eng)
    return text


# Walk all NavigableString nodes
text_nodes = list(soup_en.find_all(string=True))
for node in text_nodes:
    if isinstance(node, Comment):
        node.extract()  # remove HTML comments (they often have Chinese)
        continue
    if is_in_skip_zone(node):
        continue
    new_text = translate_text_node(str(node))
    if new_text != str(node):
        node.replace_with(NavigableString(new_text))


# === Final cleanup: collapse whitespace + fix punctuation in text nodes ===
text_nodes = list(soup_en.find_all(string=True))
for node in text_nodes:
    if isinstance(node, Comment):
        continue
    if is_in_skip_zone(node):
        continue
    s = str(node)
    # Collapse multiple spaces
    s = re.sub(r'[ \t]{2,}', ' ', s)
    # Remove space before EN punctuation
    s = re.sub(r' +([,.;:!?)\]])', r'\1', s)
    # Add space after EN punctuation if next is letter/digit
    s = re.sub(r'([,.])([A-Za-z0-9])', r'\1 \2', s)
    # Insert space between glued lowercase+Capital (skip acronyms like WEF)
    s = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', s)
    # Trim leading/trailing space inside isolated text
    if s != str(node):
        node.replace_with(NavigableString(s))


# Lang button labels (final pass on innerText)
for btn in soup_en.find_all('button', attrs={'data-lang': True}):
    if btn['data-lang'] == 't':
        btn.string = 'TC'
    elif btn['data-lang'] == 's':
        btn.string = 'SC'
    elif btn['data-lang'] == 'e':
        btn.string = 'EN'

# Update lang-loading text
for tag in soup_en.find_all(id='lang-loading'):
    tag.string = 'Converting…'

# Write file
en_html = str(soup_en)
DST_EN.write_text(en_html, encoding="utf-8")
print(f"✓ {DST_EN.name} ({DST_EN.stat().st_size/1024:.0f} KB)")

# Diagnostic: show remaining Chinese in visible content
visible_chinese = re.sub(r'<script[\s\S]*?</script>', '', en_html)
visible_chinese = re.sub(r'<style[\s\S]*?</style>', '', visible_chinese)
chinese_count = len(re.findall(r'[一-龥]', visible_chinese))
print(f"  剩 {chinese_count} 個中文字 (excl. script/style)")
