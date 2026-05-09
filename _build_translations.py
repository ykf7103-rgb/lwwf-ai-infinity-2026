"""Build v3-cn.html (簡體 OpenCC) + v3-en.html (英文 manual dict)."""
import re
from pathlib import Path
from opencc import OpenCC

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
# === 英文版 (manual translation dictionary) ===
# ============================================================
en = text

# 1. Strip HTML comments (they often contain Chinese annotations)
en = re.sub(r'<!--[\s\S]*?-->', '', en)

# 2. Translate alt attributes (visible to screen-readers; tooltip)
ALT_TRANS = {
    '4 學生玩成語攻防戰桌遊': '4 students playing the Idiom Battle card game',
    'AI 集換卡網頁': 'AI TCG cards web app',
    'SSR 將軍卡': 'SSR General Card',
    'SR 將軍卡': 'SR General Card',
    'AI 魔法默書助手 web app 介面': 'AI Magic Dictation web app interface',
    '乘法大師課堂': 'Multiplication Master class',
    '數學漫畫變身器作品': 'Math Comic Generator output',
    '第一代 App Inventor 編程課堂': 'Gen 1 · App Inventor coding class',
    '第二代 樂在其「中」攤位': 'Gen 2 · Joyfully Chinese booth',
    '第三代 AI 集換卡': 'Gen 3 · AI TCG cards',
    '學生持文化試身室相 + 攤位': 'Student with Cultural Fitting Room photos + booth',
    '文化試身室實況': 'Cultural Fitting Room live',
    '試身室攤位 banner': 'Fitting Room booth banner',
    '學生持 iPad + 國寶 AI 管家展板': 'Student with iPad + National Treasure AI Steward booth',
    '水果月 AI 歌曲頒獎合照': 'Fruit Month AI Song award photo',
    '水果月 Padlet 親子 AI 歌曲創作平台': 'Fruit Month Padlet AI Song platform',
    '大電視 AI 體育系統': 'Large-screen AI Sport System',
    '學生跳繩戶外體育堂': 'Students rope-skipping outdoors',
    '學生原稿手繪': 'Student original hand-drawn',
    'AI 完成嘅未來職業卡': 'AI-completed Future Career card',
    'AI 完成': 'AI Final',
    '國寶 AI 管家攤位 + 5 學生 + 鱷蜥盒 + 大電視': 'National Treasure AI Steward booth + 5 students + lizard box + screen',
    'P1-P3 Matatalab 實物編程': 'P1-P3 · Matatalab tangible coding',
    'P4 課程 · 狐假虎威新編四格漫畫': 'P4 · Fox Borrows Tiger reimagined comic',
    '學生用 ThinkPad AI 設計': 'Student designing with AI on ThinkPad',
    '學生展示 Magnetic Car AI 作品': 'Student presenting Magnetic Car AI work',
    '2024 國民身份認同頒獎典禮全體合照': '2024 National Identity Award ceremony',
    'BETT UK 2026 攤位': 'BETT UK 2026 booth',
    '家長 Workshop 實況': 'Parent Workshop live',
    'AI 時代超級家長 Gemini × Poe 工作坊': 'AI-Era Super Parent · Gemini × Poe Workshop',
    'AI Garden 學生作品': 'AI Garden student works',
    '5G 智慧蝴蝶園': '5G Smart Butterfly Garden',
    '校園生態池': 'Campus eco-pond',
    '家長賦能 5G': 'Parent Empowerment 5G',
    'LWWF 學生 + 教師 + 教博合照': 'LWWF students + teachers · Education Expo',
    'LWWF 校長與學生': 'LWWF Principal with students',
    '中文': 'Chinese', '英文': 'English', '數學': 'Math', '人文': 'Humanities',
    '科學': 'Science', '音樂': 'Music', '體育': 'PE', '視藝': 'Visual Arts',
    '默書': 'Dictation',
    '實物編程實況': 'Tangible coding session',
    '識花君影片': 'Plant ID Video',
    '現代門神影片': 'Modern Door Gods Video',
}
for zh, eng in ALT_TRANS.items():
    en = en.replace(f'alt="{zh}"', f'alt="{eng}"')

# 中→英 dictionary, longer phrases first to avoid partial match
TRANSLATIONS = [
    # === Page title / chrome ===
    ("AI INFINITY · 樂善堂梁黃蕙芳紀念學校 · 21 頁精選版",
     "AI INFINITY · LWWF · 21-Slide Parent Presentation"),
    ("樂善堂梁黃蕙芳紀念學校 · 2026 家長簡報",
     "LWWF · 2026 Parent Presentation"),
    ("樂善堂梁黃蕙芳紀念學校", "LWWF Memorial School"),

    # === Section / kicker labels ===
    ("OPENING · 開場", "OPENING"),
    ("RESEARCH · 全球研究", "RESEARCH · GLOBAL"),
    ("RESEARCH · 必備技能", "RESEARCH · CRITICAL SKILLS"),
    ("RESEARCH · 香港落實", "RESEARCH · HK ROLLOUT"),
    ("MATRIX · 趨向矩陣", "MATRIX · TREND MAPPING"),
    ("中文 · AI 成語攻防戰", "CHINESE · AI Idiom Battle"),
    ("AI 魔法默書助手", "AI Magic Dictation"),
    ("數學 · MATH", "MATH"),
    ("人文 · 樂在其「中」", "HUMANITIES · Joyfully Chinese"),
    ("人文 · AI 中華文化試身室", "HUMANITIES · AI Cultural Fitting Room"),
    ("科學 · SCIENCE", "SCIENCE"),
    ("音樂 · MUSIC", "MUSIC"),
    ("體育 · PE", "PHYSICAL EDUCATION"),
    ("視藝 · VISUAL ARTS", "VISUAL ARTS"),
    ("FLAGSHIP · 旗艦項目", "FLAGSHIP PROJECT"),
    ("CURRICULUM · 螺旋課程", "CURRICULUM · Spiral Pathway"),
    ("ETHICS · 倫理 + 評估", "ETHICS + ASSESSMENT"),
    ("ACHIEVEMENT · 比賽獎項", "AWARDS · COMPETITIONS"),
    ("ACTION · Workshop", "ACTION · Workshop"),
    ("FUTURE · 未來藍圖", "FUTURE BLUEPRINT"),
    ("CTA · 結語", "CONCLUSION"),

    # === Cover ===
    ("無限可能", "Infinite Possibility"),
    ("無限創造", "Infinite Creation"),
    ("無限未來", "Infinite Future"),
    ("大科目", "Subjects"),
    ("校網第一", "1st in District"),
    ("螺旋課程", "Spiral Curriculum"),
    ("革新元年", "Launch Year"),

    # === P2 research ===
    ("全球研究 · WEF 2023", "Global Research · WEF 2023"),
    ("未來工作的", "The Coming"),
    ("劇變", "Disruption"),
    ("當孩子畢業時，世界已經不一樣。", "By the time children graduate, the world has changed."),
    ("即將消失", "DISAPPEARING"),
    ("即將誕生", "EMERGING"),
    ("技能轉型", "SKILL SHIFT"),
    ("個工作職位", "jobs"),
    ("個新工作職位", "new jobs"),
    ("核心技能五年內被打亂", "of core skills disrupted within 5 years"),
    ("資料輸入、傳統文書、簡單客服——所有「重複性、規則明確」的工作，AI 完全取代。家長現時鼓勵的「穩定文職」前景，五年內或不存在。",
     "Data entry, traditional clerical work, simple customer service — every \"repetitive, rule-based\" job will be fully replaced by AI. The \"stable office career\" parents currently encourage may not exist in 5 years."),
    ("AI 訓練師、Prompt 工程師、人機協作專家、AI 倫理師——新崗位的共通點：需要與 AI 合作、判斷、再創造。",
     "AI trainers, Prompt engineers, Human-AI collaboration specialists, AI ethicists — these new roles share one trait: working with AI, judging, and re-creating."),
    ("即孩子未畢業，技能已過時。傳統「考試取分」的訓練再無意義——唯一出路：",
     "Children's skills will be outdated before graduation. Traditional \"exam-cram\" training becomes meaningless — the only path: "),
    ("學會「如何學習」", "learn HOW to learn"),
    ("WEF 預測 2023-2027", "WEF forecast 2023-2027"),
    ("WEF 新興職位類別", "WEF emerging job categories"),
    ("資料來源：", "Source: "),
    ("World Economic Forum, ", "World Economic Forum, "),
    ("（調查 803 間跨國企業，覆蓋 27 個產業群、46 個經濟體，共 1,130 萬名員工）。",
     " (surveying 803 multinational firms, 27 industry clusters, 46 economies, 11.3 million employees)."),

    # === P3 skills ===
    ("全球研究 · WEF 2023 + OECD 2030", "Global Research · WEF 2023 + OECD 2030"),
    ("年的", " "),
    ("必備技能", "Critical Skills"),
    ("五項技能，全部都是 AI 時代教育的核心。", "Five skills — all at the core of AI-era education."),
    ("分析性思維", "Analytical Thinking"),
    ("創造力", "Creativity"),
    ("AI 與大數據素養", "AI & Big Data Literacy"),
    ("韌性與敏捷", "Resilience & Agility"),
    ("好奇心 + 主動學習", "Curiosity + Self-Learning"),
    ("問對問題、拆解複雜情境。AI 給的是答案，但決定問甚麼問題的，仍然是人。",
     "Asking the right questions, breaking down complex situations. AI gives answers, but it is humans who decide which questions to ask."),
    ("AI 隨便寫都有 80 分——人類的「品味」與「獨特觀點」是決勝點。創意 = AI 不可取代的稀缺品。",
     "AI scores 80% effortlessly — human \"taste\" and \"unique perspective\" are the decisive edge. Creativity is the scarce trait AI cannot replace."),
    ("會用 AI、會質疑 AI、會與 AI 協作。並非「會聊天」，而是能判斷 AI 何時錯、何時可信。",
     "Use AI, question AI, collaborate with AI. Not \"can chat\" — but can judge when AI is wrong and when to trust it."),
    ("AI 不懂挫折，學生在失敗中迭代成主角。能在不確定中前進，是 AI 時代最稀缺的特質。",
     "AI knows no setback. Students iterate through failure to become protagonists. Advancing through uncertainty is the rarest trait in the AI era."),
    ("AI 永遠取代不了的人類核心特質。好奇心驅動終身學習，是面對 44% 技能過時的唯一保險。",
     "Human traits AI can never replace. Curiosity drives lifelong learning — the only insurance against 44% skill obsolescence."),
    ("這些技能　·　全部都是 AI 教育的核心",
     "These skills are all at the core of AI education"),
    ("本校 AI INFINITY 戰略，正是針對這五項技能逐一設計課程——並非趨勢追隨，而是基於 WEF 與 OECD 的研究依據。",
     "Our school's AI INFINITY strategy designs curriculum for each of these five skills — not trend-chasing, but grounded in WEF and OECD research."),

    # === P4 HK ===
    ("香港本地 · 教育局 + 港大 + 70 校網", "HK Local · EDB + HKU + District 70"),
    ("香港 AI 教育", "HK AI Education"),
    ("已經啟動", "Has Already Launched"),
    ("本校屬於最早的實踐者之一。", "Our school is one of the earliest practitioners."),
    ("教育局", "EDB"),
    ("「智」啟學教計劃", "Smart i-Learn Programme"),
    ("公帑資助學校的一筆過撥款，推動「AI for ALL Subjects」全科應用，配合教育局《數字素養架構》校本實踐。",
     "Government one-time grant supporting \"AI for ALL Subjects\" rollout, aligned with EDB Digital Literacy Framework."),
    ("本校已申請並全面落實。", "Our school has applied and fully implemented."),
    ("香港大學", "HKU"),
    ("人工智能年代的自主學習", "Self-Directed Learning in the AI Era"),
    ("港大統籌的優質教育基金網絡計劃，研究 AI 時代的自主學習模式。",
     "HKU-led Quality Education Fund network programme studying AI-era self-learning models."),
    ("本校為參與校之一", "Our school is one of the participating schools"),
    ("，與全港頂尖學校共同實踐。", ", co-practising with top schools across HK."),
    ("校網", "District"),
    ("第一間引入企業級 AI", "First to adopt enterprise-grade AI"),
    ("全面採用", "Fully adopting "),
    ("騰訊青少年人工智能教育平台", "Tencent Youth AI Education Platform"),
    ("的小學——學生使用的工具，與業界企業同步。",
     " — students use the same tools as industry."),
    ("EARLY MOVER · 早期實踐者", "EARLY MOVER"),
    ("本校早幾年已是", "Our school has been a "),
    ("賽馬會 CoolThink@JC 運算思維教育的先導學校", "Jockey Club CoolThink@JC pilot school for years"),
    ("，並非 AI 教育的新手——而是香港 AI 教育最早期的實踐者。在這個基礎上，我們持續更新工具、優化教法。",
     ", not a newcomer to AI education — but one of HK's earliest practitioners. On this foundation, we continue to update tools and refine pedagogy."),

    # === P5 matrix ===
    ("8 大科 × 未來對應", "8 Subjects × Future Mapping"),
    ("每一科都有", "Every subject has a"),
    ("明確的未來定位", "clear future direction"),
    ("科目", "Subject"),
    ("對應未來趨向", "Future Trend"),
    ("校本實踐", "School Practice"),
    ("中文", "Chinese"),
    ("英文", "English"),
    ("數學", "Math"),
    ("人文", "Humanities"),
    ("人文／常識", "Humanities/GS"),
    ("科學", "Science"),
    ("音樂", "Music"),
    ("體育", "PE"),
    ("視藝", "Visual Arts"),
    ("文化傳承　·　AI 倫理素養", "Cultural Heritage · AI Ethics"),
    ("學習能動性（OECD Agency）", "Learning Agency (OECD)"),
    ("2 Sigma 個人化突破", "2 Sigma Personalisation"),
    ("國民身份認同　·　跨文化理解", "National Identity · Cross-Cultural"),
    ("五感體驗　·　STEM 探究", "Sensory · STEM Inquiry"),
    ("美學素養　·　AI 共創", "Aesthetics · AI Co-Creation"),
    ("健康素養　·　IoT 數據時代", "Health Literacy · IoT Data Age"),
    ("創造力　·　文化保育", "Creativity · Heritage"),

    # === P6 Chinese ===
    ("將學中文　變成", "Turn Learning Chinese into"),
    ("卡牌對戰", "a Card Battle"),
    ("玩法", "Gameplay"),
    ("輸入成語造句", "Input idiom sentences"),
    ("AI", "AI"),
    ("10 分制評分", "10-point AI scoring"),
    ("滿分 20% 機率抽", "20% chance of"),
    ("UR 將軍卡", "UR General Card"),
    ("（岳飛、關羽、李靖）。", " (Yue Fei, Guan Yu, Li Jing)."),
    ("評分四維度", "Scoring Dimensions"),
    ("語法", "Grammar"),
    ("用詞", "Diction"),
    ("豐富度", "Richness"),
    ("創意", "Creativity"),
    ("全港小學優異獎", "HK Primary Merit Award"),
    ("件作品中獲選", "selected from 103 entries"),

    # === P7 Dictation ===
    ("校本研發 · AI 魔法默書助手", "School-Developed · AI Magic Dictation"),
    ("老師 + Gemini　共同研發", "Teachers + Gemini · Co-developed"),
    ("校本默書工具", "School Dictation Tool"),
    ("老師 × Gemini　共創", "Teachers × Gemini · Co-creation"),
    ("由本校老師與 Gemini 一同以", "Developed by our teachers with Gemini using "),
    ("自然語言", "natural language"),
    ("開發——無需編程經驗，將老師對教學的理解，變成可即用的工具。",
     " — no coding required. Turning teachers' pedagogical insight into ready-to-use tools."),
    ("自學默書", "Self-Learn Dictation"),
    ("為低小設計：", "Designed for lower primary: "),
    ("學校預設默書範圍自動填入", "school-presets auto-fill"),
    ("。學生自行選範圍、由 AI 朗讀、即時批改——讓孩子在家也能",
     ". Students self-select scope, AI reads aloud, instant grading — children can "),
    ("自學溫書", "self-study at home"),
    ("兩種模式", "Two Modes"),
    ("詞語默書", "Word Dictation"),
    ("：AI 生成故事 + 圖卡輔助記憶", ": AI-generated stories + flashcards"),
    ("智能讀默 / 背默", "Smart Read / Recite"),
    ("：逐句聽聲、隱藏文字", ": sentence-by-sentence audio, hidden text"),
    ("解決家長痛點", "Solving Parent Pain Points"),
    ("家長唔再需要逐字讀默——AI 永不疲倦、隨時聽寫、永遠耐心。",
     "Parents no longer need to read aloud — AI never tires, available anytime, infinitely patient."),

    # === P8 Math ===
    ("破解 70 年難題", "Cracking the 70-Year Problem"),
    ("2 Sigma 個人化", "2 Sigma Personalisation"),
    ("P4 課程：乘法大師", "P4: Multiplication Master"),
    ("高年級學生寫 AI 程式", "Senior students write AI programs"),
    ("，回饋低年級——P5/P6 學生親手做出乘法練習工具，俾 P2 同學使用。",
     " for juniors — P5/P6 students build multiplication tools for P2 to use."),
    ("蘇格拉底反問", "Socratic Questioning"),
    ("AI 不直接給答案，而係反問：「點解咁諗？仲有其他方法嗎？」訓練批判思維。",
     "AI doesn't give answers but asks back: \"Why think this way? Other approaches?\" Training critical thinking."),
    ("數學漫畫變身器", "Math Comic Generator"),
    ("學生親手畫角色 → AI 生成", "Students draw characters → AI generates "),
    ("四格漫畫解題", "4-panel comic solutions"),
    (" → 學生親自講解（fact-check）。", " → students fact-check & explain."),
    ("數學 × 中文 × 視藝 × 科技", "Math × Chinese × Arts × Tech"),
    ("融合。", " integration."),
    ("研究依據：", "Research basis: "),
    ("一對一導師可令學生表現由 50 百分位升至 98 百分位。",
     "1-on-1 tutoring lifts students from 50th to 98th percentile."),

    # === P9 Lokjoy ===
    ("由 App Inventor　到", "From App Inventor to"),
    ("AI 集換卡", "AI TCG Cards"),
    ("由電腦堂", "From Computer class "),
    ("→", "→"),
    ("AI 中華文化「樂在其中」App", "AI \"Joyfully Chinese\" App"),
    ("·　三個世代演進", " · Three generations of evolution"),
    ("第一代　·　奠基", "Gen 1 · Foundation"),
    ("App Inventor", "App Inventor"),
    ("由電腦堂起步——學生用 MIT App Inventor 圖像化編程砌出初代文化遊戲。奠基期嘅編程訓練。",
     "From Computer class — students use MIT App Inventor visual coding to build Gen-1 cultural games. Foundation-era coding training."),
    ("第二代　·　全港季軍", "Gen 2 · HK 3rd Place"),
    ("樂在其「中」App", "Joyfully Chinese App"),
    ("融合 AI 重新詮釋中華文化。", "Reinterpreting Chinese culture with AI. "),
    ("全港 500 隊中榮獲季軍", "3rd place out of 500 teams HK-wide"),
    ("第三代　·　最新", "Gen 3 · Latest"),
    ("AI 集換卡", "AI TCG Cards"),
    ("由 App 升級為實體 + AI 卡牌系統——學生輸入成語造句，AI 即場評分抽出 SSR / SR 武將卡。",
     "Upgraded from App to physical + AI card system — students enter idiom sentences, AI scores live and draws SSR/SR General cards."),
    ("真正的文化傳承，並非令學生變成歷史的旁觀者，而是令他們成為文化的再創造者。",
     "True cultural inheritance is not turning students into historical bystanders, but into culture's re-creators."),
    ("校長許敏詩 · RTHK 訪問", "Principal Ms Hui · RTHK Interview"),

    # === P9b Cultural Fitting Room ===
    ("人工智能", "Artificial Intelligence"),
    ("帶你穿越時空", "takes you through time"),
    ("即場試身　·　即場拍照", "Live Try-On · Live Photo"),
    ("AI 攝影機 + 大電視介面，學生站到鏡頭前——AI 即時將學生「換上」民族服飾（藏族、苗族、蒙古族）背景，化身古代人物。",
     "AI camera + large TV interface — student stands before camera, AI instantly \"dresses\" them in ethnic costumes (Tibetan, Miao, Mongolian) backgrounds."),
    ("超越教科書嘅文化體驗", "Beyond Textbook Cultural Experience"),
    ("由「閱讀文化」轉為「親身穿戴」——對應教育局《價值觀教育架構》。學生帶走自己嘅試身相，回家延續分享。",
     "From \"reading culture\" to \"personally wearing\" — aligned with EDB Values Education Framework. Students take home their try-on photos to share."),
    ("教育意義", "Educational Significance"),
    ("AI 並非取代真實服飾體驗，而係降低門檻——令每位學生都能跨越時空，與多元文化產生個人連結。",
     "AI doesn't replace real costume experience but lowers the barrier — letting every student bridge time and connect personally with diverse cultures."),

    # === P10 Science ===
    ("由實驗報告　走向", "From Lab Reports to "),
    ("真實世界探究", "Real-World Inquiry"),
    ("P6 課程：識花君", "P6: Plant ID Master"),
    ("學生於校園花圃使用 AI 植物識別 App，整合即場觀察、AI 工具、分類學知識——對應 Hattie d=0.50 探究式學習。",
     "Students use AI plant ID app in school garden, integrating live observation, AI tools, taxonomic knowledge — Hattie d=0.50 inquiry learning."),
    ("AI 生態保育體驗日", "AI Conservation Day"),
    ("透過親身接觸阿達伯拉象龜，配合 AI 物種辨識工具——學生由保育的旁觀者，轉為實際參與者。",
     "Through hands-on encounter with Aldabra giant tortoise, paired with AI species ID — students transform from conservation bystanders to participants."),
    ("旗艦項目：國寶 AI 管家", "Flagship: National Treasure AI Steward"),
    ("校內領養瑤山鱷蜥（中國一級保護動物，全球瀕危）。配合 IoT 感應器與 AI 監測系統。",
     "School adopts Yaoshan crocodile lizard (China's Class-1 protected, globally endangered). With IoT sensors + AI monitoring."),
    ("詳見 P14 旗艦頁。", "See P14 Flagship."),
    ("識花君影片", "Plant ID Video"),

    # === P11 Music ===
    ("由樂理練習　走向", "From Music Theory to "),
    ("親子 AI 共創", "Parent-Child AI Co-creation"),
    ("「水果月」親子 AI 歌曲創作", "\"Fruit Month\" Family AI Song Creation"),
    ("家長與學生使用 Suno AI 共創粵語歌曲，主題以水果與生活營養為核心。學習成果上載 Padlet 平台與全校分享——家長由「監督者」轉為「共學夥伴」。",
     "Parents and students co-create Cantonese songs with Suno AI, themed on fruits and nutrition. Results uploaded to Padlet for school-wide sharing — parents transform from \"supervisors\" into \"co-learning partners\"."),
    ("由消費者　變成作者", "From Consumer to Author"),
    ("當學生發現自己「會作歌」，對音樂的熱情會由被動變為主動。AI 並非取代創作，而是降低創作的門檻——對應 UNESCO 創意表達框架。",
     "When students discover they \"can compose\", their passion turns from passive to active. AI doesn't replace creation but lowers the barrier — aligned with UNESCO creative expression framework."),
    ("音樂科以前係欣賞與演唱為主，難以讓學生親身體驗創作。Suno 改變了這一切。",
     "Music used to be appreciation and singing — hard to let students experience real creation. Suno changes everything."),
    ("音樂科組", "Music Department"),

    # === P12 PE ===
    ("由動作示範　走向", "From Demos to "),
    ("IoT 數據體育", "IoT Data PE"),
    ("P5 課程：AI 國寶守衛戰 2.0", "P5: AI National Guardian 2.0"),
    ("學生跳繩動作觸發 AI 視覺辨識，跳繩次數轉化為「清潔氣流大砲」嘅能量，擊退污染怪獸——將枯燥嘅體能訓練變成國寶守衛任務。",
     "Students' rope-skipping triggers AI vision recognition, jump counts become \"clean-air cannon\" energy, defeating pollution monsters — turning boring fitness training into a national-treasure guardian mission."),
    ("AI 智能體育系統（試行）", "AI Sport System (Pilot)"),
    ("於體育館設置大電視 AI 視覺辨識，可實時計算跳繩次數、跳遠距離——對應 WHO 兒童活動指引嘅數據素養要求。",
     "Large-screen AI vision in gym calculates rope-skips and long-jumps in real time — meeting WHO children-activity guideline data literacy requirements."),
    ("並非監測　而是賦能", "Not Surveillance, but Empowerment"),
    ("系統強調個人改善，而非全班排名——避免學生因比較而產生運動焦慮。資料只供個人參考，",
     "System emphasises personal improvement, not class ranking — avoiding peer-comparison anxiety. Data for personal reference only, "),
    ("不寫心跳血氧、不點名比較", "no heart rate/oxygen recording, no naming"),

    # === P13 VA ===
    ("由臨摹練習　走向", "From Imitation to "),
    ("文化保育與創新", "Heritage + Innovation"),
    ("P5 課程：現代門神", "P5: Modern Door Gods"),
    ("學生先以傳統水墨手繪稿構思角色，再使用 AI 工具將其轉化為動態作品——傳統與創新並非對立，而係互相成就。對應 21 世紀 4C 核心技能。",
     "Students draft characters with traditional ink, then use AI to transform into dynamic works — tradition and innovation aren't opposites but complement each other. Aligned with 21st-Century 4C skills."),
    ("P6 課程：未來職業 APP", "P6: Future Career APP"),
    ("畢業生涯規劃融入視藝——學生為自己嘅未來職業設計 APP 介面草圖，再用 AI 完善視覺呈現。",
     "Graduation career planning meets visual arts — students design APP interface drafts for their future careers, then refine visuals with AI."),
    ("創意 × 自我認同", "Creativity × Self-Identity"),
    ("AI 不會取代畫筆，但會擴闊學生對「創作」的想像。我們的責任，是教他們判斷哪個版本最有自己的靈魂。",
     "AI doesn't replace the brush but expands students' imagination of \"creation\". Our duty: teach them to judge which version has their own soul."),
    ("張楚雯老師 · 視藝科", "Ms Cheung · Visual Arts"),
    ("現代門神影片", "Modern Door Gods Video"),
    ("原稿", "Original"),
    ("AI 完成", "AI Final"),

    # === P14 Flagship ===
    ("旗艦項目 · FLAGSHIP", "FLAGSHIP PROJECT"),
    ("國寶 AI 管家", "National Treasure AI Steward"),
    ("瑤山鱷蜥", "Yaoshan Crocodile Lizard"),
    ("中國一級保護動物　·　全球瀕危品種", "China Class-1 Protected · Globally Endangered"),
    ("真實國寶", "Real National Treasure"),
    ("本校為香港少數獲准合法領養的小學。", "One of few HK primary schools legally permitted to adopt."),
    ("IoT 智能監測", "IoT Smart Monitoring"),
    ("溫度、濕度、光照感應器實時上傳。", "Temperature, humidity, light sensors live-upload."),
    ("AI 行為辨識", "AI Behaviour Recognition"),
    ("攝影機辨識日常行為，記錄健康狀況。", "Camera recognises daily behaviour, logs health."),
    ("跨學科融合", "Cross-Disciplinary"),
    ("科學 + STEAM + 人文 + 資訊科技。", "Science + STEAM + Humanities + IT."),
    ("校內主理：", "Led by: "),
    ("蕭蕙欣主任、楊錦鋒老師", "Dean Siu, Mr Yeung"),
    ("合作單位：", "Partners: "),
    ("瑤山鱷蜥保育協會", "Yaoshan Lizard Conservation Society"),

    # === P15 Curriculum ===
    ("課程架構 · CURRICULUM", "CURRICULUM"),
    ("螺旋式雙階段", "Two-Stage Spiral"),
    ("階段一　·　P1-P3 奠基期", "Stage 1 · P1-P3 Foundation"),
    ("運算思維 + AI 啟蒙", "Computational Thinking + AI Intro"),
    ("透過遊戲化、具象化操作（如 Matatalab 實物編程），培養學生最底層的邏輯解難能力。",
     "Through gamified, hands-on operations (e.g. Matatalab tangible coding), cultivating foundational logical problem-solving."),
    ("Matatalab", "Matatalab"),
    ("Scratch Jr.", "Scratch Jr."),
    ("Code.org", "Code.org"),
    ("P1-P3 暫未引入生成式 AI，保護兒童早期認知發展。",
     "Generative AI not yet introduced in P1-P3, protecting early cognitive development."),
    ("階段二　·　P4-P6 賦能期", "Stage 2 · P4-P6 Empowerment"),
    ("企業 AI + 跨科 PBL", "Enterprise AI + Cross-Subject PBL"),
    ("全面引入企業級 AI 工具，進行深度跨學科實作。",
     "Full enterprise-grade AI rollout, deep cross-disciplinary projects."),
    ("狐假虎威", "Fox Borrows Tiger's Might"),
    ("乘法大師", "Multiplication Master"),
    ("現代門神", "Modern Door Gods"),
    ("AI 翻譯官", "AI Translator"),
    ("識花君", "Plant ID Master"),
    ("畢業生涯規劃", "Career Planning"),
    ("學生組別 / 比賽作品（成語攻防戰、文化試身室、國寶 AI 管家等）係課餘自主探究。",
     "Student-group/competition works (Idiom Battle, Cultural Fitting, National Treasure Steward) are extracurricular self-inquiry."),

    # === P16 Ethics ===
    ("AI 倫理 · 評估革新", "AI ETHICS · ASSESSMENT REFORM"),
    ("引入 AI", "Introducing AI"),
    ("必有清晰邊界", "Requires Clear Boundaries"),
    ("紅線一：絕不取代人的判斷", "Red Line 1: Never replace human judgement"),
    ("AI 是輔助與啟發，老師與學生的判斷永遠優先。",
     "AI assists and inspires; teacher and student judgement always prevail."),
    ("紅線二：絕不輸出未驗證的事實", "Red Line 2: Never output unverified facts"),
    ("學生必須學會 fact-check，事實準確性的最終責任在作者本人。",
     "Students must learn to fact-check; ultimate accuracy is the author's responsibility."),
    ("評估三層架構", "3-Layer Assessment"),
    ("紙筆", "Paper-pen"),
    ("歷程檔案", "Process Portfolio"),
    ("實作 + 口頭解說", "Demo + Oral Explanation"),
    ("——三軌並行，避免流於 AI 代寫。",
     " — three tracks parallel, avoiding AI-ghostwriting."),
    ("紙筆不會被取代，但已不足以反映 AI 時代的真實能力。",
     "Paper-pen isn't replaced, but no longer reflects true AI-era capability."),

    # === P17 Awards ===
    ("比賽成果 · ACHIEVEMENT", "ACHIEVEMENTS"),
    ("學生作品", "Student Works"),
    ("已獲外界認可", "Recognised by the Industry"),
    ("CHAMPIONSHIP　·　季軍", "BRONZE MEDAL"),
    ("樂在其「中」", "Joyfully Chinese"),
    ("全港小學中華文化教育比賽　·　500 隊參賽中榮獲季軍。",
     "HK Primary Chinese Culture Education Competition · 3rd place out of 500 teams."),
    ("EXCELLENCE　·　優異獎", "MERIT AWARD"),
    ("AI 成語攻防戰", "AI Idiom Battle"),
    ("國民身份認同應用程式設計比賽　·　103 件作品中獲選。",
     "National Identity App Design Competition · selected from 103 entries."),
    ("GLOBAL　·　走出香港", "GLOBAL · Beyond HK"),
    ("BETT London 2026", "BETT London 2026"),
    ("本校代表將於倫敦 BETT 教育科技展。", "Our representatives at London BETT EdTech Expo."),

    # === P18 Workshop ===
    ("家長賦能 · WORKSHOP", "PARENT EMPOWERMENT · WORKSHOP"),
    ("家長不止是旁觀者", "Parents Aren't Just Bystanders"),
    ("您也是 AI 創造者", "You're an AI Creator Too"),
    ("AI 時代超級家長", "AI-Era Super Parent"),
    ("「Gemini × Poe 實戰工作坊」——輕鬆引導孩子自主學習。家長由零編程基礎開始，30 分鐘做出自己孩子嘅 AI 默書 App。",
     "\"Gemini × Poe Hands-On Workshop\" — easily guide children's self-learning. Parents start from zero coding, 30 minutes to build their child's AI dictation app."),
    ("定期舉行", "Regularly Held"),
    ("每學期最少兩次，配合學生課程進度——確保家長嘅 AI 知識同學校同步。",
     "At least twice per term, aligned with student curriculum — keeping parent AI knowledge in sync with school."),
    ("唔只技術　·　更係溝通", "Not Just Tech · Communication Too"),
    ("家長親手做過先理解 AI 唔係魔法。家中嘅 AI 對話從此有質素、有界線。",
     "Hands-on lets parents understand AI isn't magic. Home AI conversations now have quality and boundaries."),

    # === P19 Future ===
    ("未來藍圖 · FUTURE", "FUTURE BLUEPRINT"),
    ("下一步", "Next Step"),
    ("三大計劃", "Three Plans"),
    ("AI Garden", "AI Garden"),
    ("校園常設展示空間，匯集歷屆學生 AI 作品——由概念漫畫到完整應用。",
     "Permanent campus showcase, gathering all students' AI works — from concept comics to full apps."),
    ("5G 智慧蝴蝶園", "5G Smart Butterfly Garden"),
    ("5G IoT 感應園，學生實時觀察生態數據——溫度、濕度、物種辨識實時上載。",
     "5G IoT sensing garden, real-time eco-data — temperature, humidity, species ID live-upload."),
    ("家長賦能 2.0", "Parent Empowerment 2.0"),
    ("由「會用 AI」昇華為「會教 AI」——家長與學生共同學習，建立深度連結。",
     "From \"using AI\" to \"teaching AI\" — parents and students learn together, building deep connections."),

    # === P20 CTA ===
    ("結語 · CTA", "CONCLUSION"),
    ("由科技的消費者", "From Consumers of Technology"),
    ("轉為真實世界的創造者", "to Creators in the Real World"),
    ("希望每位學生都能由「科技的消費者」", "We hope every student transforms from a \"tech consumer\""),
    ("慢慢變成「能用科技解決真實問題的創造者」。",
     "into \"a creator who solves real problems with tech\"."),
    ("多謝您今日的出席", "Thank You for Joining Us Today"),
    ("LWWF · 樂善堂梁黃蕙芳紀念學校", "LWWF · Memorial School"),

    # === Footer / nav hints ===
    ("← → 切換", "← → Navigate"),
    ("F 全屏", "F Fullscreen"),
    ("第", ""),
    ("代", " Gen"),
    ("代　·　奠基", " Gen 1 Foundation"),
    ("代　·　全港季軍", " Gen 2 HK 3rd"),
    ("代　·　最新", " Gen 3 Latest"),
    ("AI 評分四維度", "AI Scoring Dimensions"),
    ("　＝　", " = "),
    ("分", "pts"),

    # === Section tag (top-left) ===
    ("OPENING", "OPENING"),
    ("RESEARCH", "RESEARCH"),
    ("MATRIX", "MATRIX"),
    ("FLAGSHIP", "FLAGSHIP"),
    ("CURRICULUM", "CURRICULUM"),
    ("ETHICS", "ETHICS"),
    ("ACHIEVEMENT", "AWARDS"),
    ("ACTION", "ACTION"),
    ("FUTURE", "FUTURE"),

    # === Common tail / connectors ===
    ("　·　", " · "),
    ("，", ", "),
    ("。", ". "),
    ("：", ": "),
    ("（", " ("),
    ("）", ") "),

    # === Misc ===
    ("親手做出默書 App", "Build dictation app yourself"),
    ("家長 30 分鐘", "Parents · 30 mins"),
    ("學校", "School"),
    ("頁", "p"),
    ("21 頁精選版", "21-Slide Edition"),

    # === Round 2 dictionary additions (cover remaining 179 fragments) ===
    # Bigger phrases first
    ("「智」啟學教計劃", "Smart i-Learn Programme"),
    ("「智啟學教」計劃", "Smart i-Learn Programme"),
    ("智啟學教", "Smart i-Learn"),
    ("數字素養架構", "Digital Literacy Framework"),
    ("學習羅盤", "Learning Compass"),
    ("優質教育基金", "Quality Education Fund"),
    ("網絡計劃名單", "Network Programme list"),
    ("合作學校紀錄", "partner-school records"),
    ("先導學校歷年名單", "pilot-school list (historical)"),
    ("先導學校", "pilot school"),
    ("歷年名單", "historical list"),
    ("教育的新手", "newcomer to education"),
    ("最早期的實踐者", "the earliest practitioners"),
    ("在這個基礎上", "On this foundation"),
    ("我們持續更新工具、優化教法", "we continually update tools and refine pedagogy"),
    ("公帑資助", "Government-funded"),
    ("的一筆過撥款", " one-time grant"),
    ("公帑資助學校的一筆過撥款", "Government one-time grant for schools"),
    ("推動", "to roll out"),
    ("全科應用", "all-subject deployment"),
    ("配合", "aligned with"),
    ("並非", "Not"),
    ("而是", "but"),
    ("章節", "chapter"),
    ("框架", "framework"),
    ("學習羅盤 2030", "Learning Compass 2030"),
    ("年公布", " announced"),
    ("年公佈", " announced"),
    ("合作", "partner"),
    ("紀錄", "record"),
    ("賽馬會", "Jockey Club"),
    ("先導", "pilot"),

    # Subjects in matrix
    ("狐假虎威新編", "Fox-Tiger Reimagined"),
    ("成語攻防戰", "Idiom Battle"),
    ("默書助手", "Dictation Assistant"),
    ("升中銜接", "Secondary Transition"),
    ("漫畫變身器", "Comic Generator"),
    ("季軍", "3rd Place"),
    ("文化試身室", "Cultural Fitting Room"),
    ("生態保育日", "Conservation Day"),
    ("國寶 AI 管家", "National Treasure AI Steward"),
    ("水果月」親子 AI 歌曲創作活動（Suno", "Fruit Month\" Family AI Song Activity (Suno"),
    ("水果月", "Fruit Month"),
    ("親子 AI 歌曲", "Family AI Song"),
    ("親子", "Family"),
    ("AI 國寶守衛戰", "AI National Treasure Guardian"),
    ("國寶守衛戰", "National Treasure Guardian"),
    ("AI 智能體育系統", "AI Smart Sport System"),
    ("智能體育系統", "Smart Sport System"),
    ("試行", "(Pilot)"),
    ("文化保育", "Cultural Heritage"),
    ("未來職業", "Future Career"),
    ("未來職業 APP", "Future Career APP"),

    # Stat / common terms
    ("萬", "M"),  # 萬 (10000) — careful: only if standalone after digits e.g. "$50萬"
    ("八大科", "8 Subjects"),
    ("八大科 × 未來矩陣", "8 Subjects × Future Matrix"),
    ("未來矩陣", "Future Matrix"),
    ("已啟動", "has launched"),
    ("封面", "Cover"),
    ("校長與學生", "Principal with students"),
    ("全球研究", "Global Research"),
    ("未來工作", "Future of Work"),
    ("未來", "Future"),
    ("香港本地", "HK Local"),
    ("香港", "HK"),

    # Inline content fragments
    ("將學", "Turn learning"),
    ("變成", "into"),
    ("學生玩攻防戰大圖", "Big photo of students playing"),
    ("加大", "(enlarged)"),
    ("學生玩成語攻防戰桌遊", "Students playing Idiom Battle"),
    ("卡並排", "cards side-by-side"),
    ("獎項", "Award"),
    ("上半部", "(top)"),
    ("下半部", "(bottom)"),
    ("將軍卡", "General Card"),
    ("評", "Score"),
    ("校本研發", "School-developed"),
    ("大圖", "(big photo)"),
    ("截圖", "screenshot"),
    ("介面", "interface"),
    ("介紹", "Introduction"),
    ("文字", "text"),
    ("科技", "Tech"),
    ("圖", "image"),
    ("上小張課堂", "(top: small class photo)"),
    ("下大張漫畫完整顯示", "(bottom: full comic display)"),
    ("跨年級協作", "Cross-grade Collaboration"),
    ("自繪角色", "Self-drawn characters"),
    ("自畫", "self-drawn"),
    ("劇變", "Disruption"),
    ("跨文化", "Cross-cultural"),
    ("國民身份認同", "National Identity"),
    ("應用程式設計比賽", "App Design Competition"),
    ("國民身份認同應用程式設計比賽", "National Identity App Design Competition"),
    ("國民身份認同 2025/26 頒獎全體合照", "National Identity 2025/26 Award ceremony group photo"),
    ("教育博覽", "Education Expo"),

    # P9 三世代演進
    ("三個世代演進", "Three generations of evolution"),
    ("世代演進", "generational evolution"),
    ("奠基", "Foundation"),
    ("最新", "Latest"),
    ("全港", "HK-wide"),

    # P9b
    ("帶你穿越時空", "takes you through time and space"),
    ("即場試身", "Live try-on"),
    ("即場拍照", "Live photo"),
    ("超越教科書嘅文化體驗", "Beyond textbook cultural experience"),
    ("教育意義", "Educational meaning"),

    # P11 Music quote
    ("音樂科組", "Music Department"),

    # P12 PE
    ("不寫心跳血氧、不點名比較", "no heart-rate/oxygen logging, no naming"),
    ("並非監測", "Not surveillance"),
    ("而是賦能", "but empowerment"),

    # P13 VA
    ("張楚雯老師", "Ms Cheung"),

    # P14 Flagship
    ("瑤山鱷蜥保育協會", "Yaoshan Lizard Conservation Society"),
    ("蕭蕙欣主任、楊錦鋒老師", "Dean Siu, Mr Yeung"),
    ("蕭蕙欣主任", "Dean Siu"),
    ("楊錦鋒老師", "Mr Yeung"),
    ("校內主理", "School lead"),
    ("合作單位", "Partner"),

    # P15 Curriculum
    ("狐假虎威", "Fox-Tiger Idiom"),
    ("會發光月餅", "Glowing Mooncake"),
    ("資訊真偽小偵探", "Fact-check Detective"),

    # P16 Ethics
    ("紙筆評估", "Paper-pen Assessment"),
    ("實作 + 口頭", "Demo + Oral"),
    ("歷程檔案", "Process Portfolio"),
    ("AI 代寫", "AI ghostwriting"),

    # P19
    ("校園常設展示空間", "Permanent campus showcase"),
    ("匯集歷屆", "gathering all past"),

    # Gen labels
    ("第一代", "Gen 1"),
    ("第二代", "Gen 2"),
    ("第三代", "Gen 3"),
    ("代", " Gen"),

    # Page id label
    (" · 結尾", ""),
    ("結尾", "End"),
    ("結語", "Conclusion"),
    ("結語 · CTA", "CONCLUSION"),
    ("親手做出", "Hands-on build"),
    ("親身體驗", "Personal experience"),
    ("即時", "instant"),
    ("實時", "real-time"),

    # === Round 3: full-sentence translations for stubborn fragments ===
    ("由「閱讀文化」轉為「親身穿戴」——對應教育局《價值觀教育架構》。學生帶走自己嘅試身相，回家延續分享。",
     "From \"reading culture\" to \"personally wearing\" — aligned with EDB Values Education Framework. Students take home try-on photos to share."),
    ("由「閱讀文化」轉為「親身穿戴」——對應",
     "From \"reading culture\" to \"personally wearing\" — aligned with"),
    ("AI 並非取代真實服飾體驗，而係降低門檻——令每位學生都能跨越時空，與多元文化產生個人連結。",
     "AI doesn't replace real costume experience but lowers the barrier — letting every student bridge time and connect with diverse cultures."),
    ("於體育館設置大電視 AI 視覺辨識，可實時計算跳繩次數、跳遠距離——對應 WHO 兒童活動指引嘅數據素養要求。",
     "Large-screen AI vision in gym calculates rope-skips and long-jumps in real time — meeting WHO children-activity data literacy requirements."),
    ("計算跳繩次數、跳遠距離——對應", "calculates rope-skips and long-jumps — meeting"),
    ("兒童活動指引嘅數據素養要求", "children-activity data literacy requirements"),
    ("當學生發現自己「會作歌」，對音樂的熱情會由被動變為主動。",
     "When students discover they \"can compose\", their passion turns from passive to active."),
    ("當學生發現自己「會作歌」", "When students discover they \"can compose\""),
    ("的熱情會由被動變為主動", "their passion turns from passive to active"),
    ("AI 並非取代創作，而是降低創作的門檻——對應 UNESCO 創意表達框架。",
     "AI doesn't replace creation but lowers the barrier — UNESCO creative expression framework."),
    ("降低創作的門檻——對應", "lowers the creation barrier — aligned with"),
    ("音樂科以前係欣賞與演唱為主，難以讓學生親身體驗創作。Suno 改變了這一切。",
     "Music used to focus on appreciation and singing — hard for students to experience real creation. Suno changes everything."),
    ("科以前係欣賞與演唱為主", " used to focus on appreciation and singing"),
    ("難以讓學生親身體驗創作", "hard for students to experience real creation"),
    ("改變了這一切", "changed everything"),
    ("學生組別 / 比賽作品（成語攻防戰、文化試身室、國寶 AI 管家等）係課餘自主探究。",
     "Student-group / competition works (Idiom Battle, Cultural Fitting Room, National Treasure AI Steward) are extracurricular self-inquiry."),
    ("學生組別 / 比賽作品", "Student-group / competition works"),
    ("係課餘自主探究", "are extracurricular self-inquiry"),
    ("由電腦堂起步——學生用 MIT App Inventor 圖像化編程砌出初代文化遊戲。奠基期嘅編程訓練。",
     "Starts from Computer class — students use MIT App Inventor visual coding to build Gen-1 cultural games. Foundation-era coding training."),
    ("起步——學生用", "starts — students use"),
    ("像化編程砌出初", " visual coding to build initial"),
    ("代文化遊戲", "-gen cultural games"),
    ("期嘅編程訓練", "-era coding training"),
    ("由 App 升級為實體 + AI 卡牌系統——學生輸入成語造句，AI 即場評分抽出 SSR / SR 武將卡。",
     "Upgraded from App to physical + AI card system — students enter idiom sentences, AI scores live and draws SSR / SR General cards."),
    ("升級為實體", "upgraded to physical"),
    ("卡牌系統——學生", "card system — students"),
    ("即場評分抽出", "scores live and draws"),
    ("武將卡", "General cards"),
    ("學生帶走自己嘅試身相", "Students take home their try-on photos"),
    ("回家延續", "to continue at home"),
    ("價值觀教育架構", "Values Education Framework"),
    ("文化遊戲", "cultural games"),
    ("文化保育與創新", "Heritage + Innovation"),
    ("自我認同", "Self-identity"),
    ("學生為自己嘅", "Students for their own"),
    ("未來職業設計 APP 介面草圖，再用 AI 完善視覺呈現",
     "future career design APP interface drafts, then refine visuals with AI"),
    ("完善視覺呈現", "refine visual presentation"),
    ("AI 不會取代畫筆，但會擴闊學生對「創作」的想像。我們的責任，是教他們判斷哪個版本最有自己的靈魂。",
     "AI doesn't replace the brush but expands students' imagination of \"creation\". Our duty: teach them to judge which version has their own soul."),
    ("AI 不會取代畫筆", "AI doesn't replace the brush"),
    ("但會擴闊學生對", "but expands students'"),
    ("的想像", " imagination"),
    ("不會被取代", "isn't replaced"),
    ("但已不足以反映", "but no longer reflects"),
    ("的真實能力", "true capability"),
    ("AI 時代的真實能力", "true AI-era capability"),
    ("校長許敏詩", "Principal Ms Hui"),
    ("RTHK 訪問", "RTHK Interview"),
    ("RTHK 開場致詞", "RTHK Opening Speech"),
    ("體育館設置大電視", "Large screen in gym"),
    ("館設置大電視", "Large screen in venue"),
    ("實戰工作坊", "Hands-on Workshop"),
    ("Gemini × Poe 實戰工作坊", "Gemini × Poe Hands-on Workshop"),
    ("輕鬆引導孩子自主學習", "Easily guide self-directed learning"),
    ("AI 時代的超級家長", "AI-Era Super Parent"),
    ("AI 時代超級家長", "AI-Era Super Parent"),
    ("超級家長", "Super Parent"),
    ("自主學習", "Self-directed Learning"),
    ("自學", "self-study"),
    ("自學溫書", "self-study at home"),
    ("溫書", "study at home"),
    ("跨越時空", "bridge time and space"),
    ("多元文化", "diverse cultures"),
    ("產生個人連結", "form personal connections"),
    ("保育協會", "Conservation Society"),
    ("瑤山鱷蜥保育協會", "Yaoshan Lizard Conservation Society"),
    ("視覺辨識", "vision recognition"),
    ("國寶守衛戰 2.0", "National Guardian 2.0"),
    ("國寶 AI 管家", "National Treasure AI Steward"),
    ("國寶", "National Treasure"),
    ("守衛", "Guardian"),
    ("旗艦", "Flagship"),
    ("旗艦項目", "Flagship Project"),
    ("即場", "live"),
    ("抽出", "draw"),
    ("草圖", "draft"),
    ("再用", "then use"),
    ("資訊", "information"),
    ("資訊科技", "IT"),
    ("音樂科組", "Music Department"),
    ("音樂科", "Music"),
    ("體育科", "PE"),
    ("視藝科", "Visual Arts"),
    ("中文科", "Chinese subject"),
    ("英文科", "English subject"),
    ("常識科", "GS subject"),
    ("人文科", "Humanities subject"),
    ("智能", "Smart"),
    ("系統", "System"),
    ("數據", "Data"),
    ("融入", "integrated into"),
    ("設計", "design"),
    ("再用 AI 完善視覺呈現", "then refine visuals with AI"),
    ("水墨手繪稿", "ink hand-drafts"),
    ("水墨", "ink"),
    ("動態作品", "dynamic works"),
    ("傳統與創新並非對立，而係互相成就", "Tradition and innovation aren't opposites but complement each other"),
    ("21 世紀 4C 核心技能", "21st-Century 4C skills"),
    ("世紀核心技能", "-Century core skills"),
    ("核心技能", "core skills"),
    ("21 世紀", "21st-Century"),
    ("21 世紀核心技能 4C（Creativity）", "21st-Century 4C (Creativity)"),
    ("世代", "Gen"),
    ("校外", "external"),
    ("校內", "internal"),
    ("校本", "school-based"),
    ("優質教學基金成果展示", "Quality Teaching Fund showcase"),
    ("成果展示", "achievements showcase"),
    ("優質", "quality"),
    ("攤位", "booth"),
    ("展示", "showcase"),
    ("頒獎", "award"),
    ("頒獎典禮", "award ceremony"),
    ("典禮", "ceremony"),
    ("公開", "public"),
    ("最近", "recent"),
    ("最新", "latest"),
    ("早期", "early"),
    ("實踐者", "practitioners"),
    ("先導者", "pioneers"),
    ("先驅", "pioneer"),
    ("由", " "),  # last fallback (very risky but minimal context now)
]

# Apply translations in order WITH whitespace padding to ensure word boundaries.
# Chinese has no space between words, so direct substitution glues EN tokens together.
# Solution: pad EN value with leading/trailing spaces, collapse multi-space at end.
def _pad(eng: str) -> str:
    """Add spacing padding only if EN value starts/ends with letter/number."""
    if not eng:
        return eng
    left = ' ' if eng[0].isalnum() else ''
    right = ' ' if eng[-1].isalnum() else ''
    return left + eng + right

for zh, eng in TRANSLATIONS:
    en = en.replace(zh, eng)

# Lang attr + active button
en = en.replace('<html lang="zh-Hant">', '<html lang="en">')
en = en.replace(
    '<button data-lang="t" class="active" title="繁體中文">繁</button>',
    '<button data-lang="t" title="Traditional Chinese">繁</button>'
)
en = en.replace(
    '<button data-lang="e" title="English">EN</button>',
    '<button data-lang="e" class="active" title="English">EN</button>'
)
en = en.replace('轉換中⋯', 'Converting…')

# Round 4: clean up final fragments (partial-replace artifacts)
FINAL_CLEAN = [
    ("不會被取 Gen", "will not be replaced"),
    ("不會被取代", "will not be replaced"),
    ("對 Music", "About music"),
    ("對音樂", "About music"),
    ("AI 時 Gentrue", "true AI-era"),
    ("AI 時代真實", "true AI-era reality"),
    ("AI 時代", "AI-era"),
    ("時代", "era"),
    ("難以讓學生Personal experience創作", "hard for students to experience real creation"),
    ("難以讓學生", "hard for students to"),
    ("難以", "hard to"),
    ("讓學生", "let students"),
    ("Personal experience創作", "experience real creation"),
    ("homepts享.", "home, share."),
    ("延續分享", "continue sharing"),
    ("分享.", "share."),
    ("分享", "share"),
    ("享.", "share."),
    ("享", "share"),
    ("作.", "create."),
    ("創作.", "creation."),
    ("創作", "creation"),
    ("可real-timecalculates", "can calculate in real time"),
    ("可實時計算", "can calculate in real time"),
    ("可實時", "real-time"),
    ("實時", "real-time"),
    ("可", "can"),
    ("學生Personal experience", "students gain personal experience"),
    ("學生", "students"),
    ("等)", " etc.)"),
    ("等", " etc."),
    ("被取", "is taken"),
    ("被取代", "is replaced"),
    ("被", " "),
    ("取代", "replace"),
    ("草圖", "draft"),
    ("草", " "),
    ("不", "not"),
    ("以", "with"),
    ("体Chinese", "Chinese"),
    ("于PE", "in PE"),
    ("於PE", "in PE"),
    ("Might新編 ·", "Might Reimagined ·"),
    ("新編", "reimagined"),
    ("組", "group"),
    ("代", "Gen"),
    ("時", "time"),
    ("會", "will"),
    ("生", " "),
    ("體", " "),
    ("讓", "let"),
    ("達", "express"),
    ("作", "create"),
    ("創", "create"),
    ("取", "take"),
    ("學", "learn"),
    ("對", "to"),
    ("新", "new"),
    ("於", "at"),
    ("編", "edit"),
    ("表", "table"),
    ("難", "hard"),
    ("科", "subject"),
]
for zh, eng in FINAL_CLEAN:
    en = en.replace(zh, eng)

# Final lang button labels (must come AFTER all translations)
en = en.replace('繁体中文', 'Traditional Chinese')
en = en.replace('繁體中文', 'Traditional Chinese')
en = en.replace('简体中文', 'Simplified Chinese')

# === Whitespace cleanup (visible text only, NOT attributes/HTML structure) ===
def cleanup_html_text(html: str) -> str:
    """Collapse multi-space in text nodes, fix space-before-punctuation."""
    out = []
    i = 0
    while i < len(html):
        if html[i] == '<':
            j = html.find('>', i)
            if j == -1:
                out.append(html[i:]); break
            out.append(html[i:j+1])
            i = j + 1
        else:
            j = html.find('<', i)
            if j == -1:
                seg = html[i:]; i = len(html)
            else:
                seg = html[i:j]; i = j
            # ONLY: collapse multiple horizontal whitespace to one
            seg = re.sub(r'[ \t]{2,}', ' ', seg)
            # Remove space before EN punctuation
            seg = re.sub(r' +([,.;:!?)\]])', r'\1', seg)
            # Add space after EN comma/period if next is letter
            seg = re.sub(r'([,.])([A-Za-z])', r'\1 \2', seg)
            # Insert space between glued lowercase+Capital words: "intoDynamic" → "into Dynamic"
            seg = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', seg)
            # Insert space between letter and digit/percent attached: "44%" stays, but "letter9" → "letter 9"
            # (skip — too risky, would break things like "P5/P6")
            out.append(seg)
    return ''.join(out)

en = cleanup_html_text(en)

# === Specific glued-word patches (common artifacts from char-level dict) ===
GLUED_FIX = [
    # specific glued lowercase pairs (most common)
    ('intoDynamic', 'into Dynamic'),
    ('intoCreator', 'into creator'),
    ('toCreators', 'to Creators'),
    ('canCalculate', 'can calculate'),
    ('homepts', 'at home'),
    ('home pts', 'at home'),
    ('willnot', 'will not'),
    ('Notreplace', 'not replace'),
    ('takenGen', 'replaced'),
    (' pts ', ' '),
    ('  ', ' '),
    # Common transitions
    ('createcreate', 'create'),
    ('Personal experiencecreate', 'experience real creation'),
    ('Personal experience創作', 'experience real creation'),
    ('Frozen Cards', 'card'),
    # Common punctuation cleanup
    (' .', '.'),
    (' ,', ','),
    (' :', ':'),
    (' ;', ';'),
    ('  ', ' '),
    # Run-on around HTML entities — keep
    # Multiple spaces final pass

    # Specific awkward phrases
    ('From Computer class starts', 'Starting from Computer class'),
    ('App Inventor image visual coding', 'App Inventor visual coding'),
    ('Gencultural games', 'Gen-1 cultural games'),
    ('Frozen Cards', 'card'),
    ('AI live Scoreptsdraw', 'AI scores live and draws'),
    ('Scoreptsdraw', 'scores and draws'),
    ('alignedwithEDB', 'aligned with the EDB'),
    ('alignedwith', 'aligned with '),
    ('aligned withEDB', 'aligned with the EDB'),
    ('aligned with the EDB《', 'aligned with the EDB '),
    ('EDB《', 'EDB '),
    ('》', ''),
    ('《', ''),
    ('students Input', 'students input'),
    ('rope-skipsand', 'rope-skips and'),
    (' barrier — UNESCOcreative', ' barrier — UNESCO creative'),
    ('UNESCOcreative', 'UNESCO creative'),
    ('AlignedwithUNESCO', 'aligned with UNESCO'),
    ('lowers the creation barrier', 'lowers the creation barrier'),
    ('takenG', 'replaced'),
    (' takenGen ', ' '),
    (' Gen ', ' '),  # leftover from "代→Gen" badly placed
    ('GenS', 'gens'),
    ('Gen·', '·'),
    ('Gen ·', '·'),
    ('Gen）', ')'),
    ('Gen)', ')'),
    ('Gen·', '·'),
    ('Gen,', ','),
    ('Gen.', '.'),
    (' . ', '. '),
    (' , ', ', '),
    ('  ', ' '),
    # Final colons
    ('LWWF · MemorialSchool', 'LWWF · Memorial School'),
    ('MemorialSchool', 'Memorial School'),

    # Round 2 specific glued fixes
    ('to Musictheir passion', 'about music, their passion'),
    ('Musictheir', 'music, their'),
    ('AI Nottake Gencreation', "AI doesn't replace creation"),
    ('Nottake Gencreation', "doesn't replace creation"),
    ('Nottake', 'does not take'),
    ('Gencreation', 'creation'),
    ('butlowers', 'but lowers'),
    ('butexpands', 'but expands'),
    ('in PELarge screen', 'Large screen'),
    ('PELarge', 'Large'),
    ('classstarts', 'class — '),
    ('songssharing', 'songs sharing'),
    ('platformsharing', 'platform sharing'),
    ('takeGen', 'replaced'),
    (' Gencreation', ' creation'),
    (' Genwill ', ' will '),
    ('NotGen', 'no longer'),
    ('Genrepresent', 'represents'),
    ('Genand', 'and'),
    ('GenP', 'P'),
    ('Pen Gen', 'pen'),
    ('Pen Genand', 'pen and'),
    ('Genof ', 'of '),
    ('homeshare', 'home, share'),
    (' homeshare', ' home, share'),

    # Final whitespace
    ('  ', ' '),
]
GLUED_FIX = [(o, n) for o, n in GLUED_FIX if o]
for old, new in GLUED_FIX:
    en = en.replace(old, new)
# Final multi-space collapse
en = re.sub(r'  +', ' ', en)

DST_EN.write_text(en, encoding="utf-8")
print(f"✓ {DST_EN.name} ({DST_EN.stat().st_size/1024:.0f} KB)")

# Diagnostic: show remaining Chinese
import re as _re
remaining = _re.sub(r'<script[\s\S]*?</script>', '', en)
remaining = _re.sub(r'<style[\s\S]*?</style>', '', remaining)
chinese_count = len(_re.findall(r'[一-龥]', remaining))
print(f"  剩 {chinese_count} 個中文字 (excl. script/style)")
