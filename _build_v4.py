"""Build v4-cn.html (OpenCC) + v4-en.html (native idiomatic rewrite) from v4.html."""
import re
from pathlib import Path
from opencc import OpenCC
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = Path(__file__).parent
SRC = ROOT / "AI_INFINITY_精選_20頁_v4.html"
DST_CN = ROOT / "AI_INFINITY_精選_20頁_v4-cn.html"
DST_EN = ROOT / "AI_INFINITY_精選_20頁_v4-en.html"

text = SRC.read_text(encoding="utf-8")

# ============================================================
# 1. Simplified (HK 繁 → 大陸簡)
# ============================================================
cc = OpenCC('hk2s')
cn = cc.convert(text)
cn = cn.replace('<html lang="zh-Hant">', '<html lang="zh-Hans">')
cn = cn.replace('<title>AI INFINITY · LWWF · Editorial v4</title>',
                '<title>AI INFINITY · LWWF · 编辑版 v4</title>')
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
# 2. English — Native Idiomatic Rewrite (sentence-level dict)
# ============================================================
# Use the v3-en build pipeline to start, then apply native rewrites
# Strategy:
#   a. Run all v3 dict translations (BS4 text-node level)
#   b. Apply NATIVE_REWRITES to upgrade to idiomatic English

# Re-use v3 dict: import from sister script
import sys
sys.path.insert(0, str(ROOT))

# Load v3-en.html as starting point (already has v3 translations applied)
v3_en = (ROOT / "AI_INFINITY_精選_20頁_v3-en.html").read_text(encoding="utf-8")

# Replace the title for v4
v3_en = v3_en.replace(
    '<title>AI INFINITY · LWWF · 21-Slide Parent Presentation</title>',
    '<title>AI INFINITY · LWWF · Editorial v4 — Parent Briefing</title>'
)

# Apply v4 CSS layer to v4-en (so it inherits the Editorial polish)
v4_html = SRC.read_text(encoding="utf-8")
# Extract v4 polish CSS
m = re.search(r'<style id="v4-editorial-polish">[\s\S]*?</style>', v4_html)
if m:
    polish = m.group(0)
    # Inject after the existing main <style>...</style> in v3-en
    v3_en = re.sub(
        r'(</style>)\s*</head>',
        r'\1\n' + polish.replace('\\', '\\\\') + '\n</head>',
        v3_en, count=1
    )

soup = BeautifulSoup(v3_en, 'html.parser')

# === NATIVE IDIOMATIC REWRITES (sentence/phrase level) ===
# Each entry: awkward EN from v3-en → native idiomatic EN
NATIVE_REWRITES = {
    # === P1 Cover ===
    "Infinite Possibility · Infinite Creation · Infinite Future":
        "Infinite Possibility · Infinite Creation · Boundless Future",
    "1st in District": "First in District 70",
    "Launch Year": "Programme Launch",

    # === P2 Research ===
    "The Coming": "The Coming",  # part of split title
    "By the time children graduate, the world has changed.":
        "By the time today's children graduate, the world they enter will look nothing like ours.",
    "DISAPPEARING": "VANISHING",
    "EMERGING": "EMERGING",
    "SKILL SHIFT": "SKILL UPHEAVAL",
    "of core skills disrupted within 5 years": "of core skills will be disrupted within five years",
    "Data entry, traditional clerical work, simple customer service — every \"repetitive, rule-based\" job will be fully replaced by AI. The \"stable office career\" parents currently encourage may not exist in 5 years.":
        "Data entry. Routine paperwork. Basic customer service. Every \"repetitive, rule-based\" role will be replaced by AI. The \"stable desk job\" we encourage today may not exist five years from now.",
    "AI trainers, Prompt engineers, Human-AI collaboration specialists, AI ethicists — these new roles share one trait: working with AI, judging, and re-creating.":
        "AI trainers. Prompt engineers. Human-AI collaboration specialists. AI ethicists. What unites them: working alongside AI to judge, refine, and create anew.",
    "Children's skills will be outdated before graduation. Traditional \"exam-cram\" training becomes meaningless — the only path:":
        "Children's skills will be obsolete before they graduate. Exam-driven cramming loses its meaning. There is only one viable path forward:",
    "learn HOW to learn": "to learn how to learn",
    "(surveying 803 multinational firms, 27 industry clusters, 46 economies, 11.3 million employees).":
        " (a survey of 803 multinational firms across 27 industries, 46 economies, and 11.3 million employees).",

    # === P3 Skills ===
    "Five skills — all at the core of AI-era education.":
        "Five skills. Each one sits at the heart of AI-era education.",
    "Asking the right questions and breaking down complex situations. AI gives answers, but humans decide which questions to ask.":
        "Knowing what to ask. Knowing how to break a tangled problem apart. AI hands us answers — but only humans decide which questions are worth asking.",
    "AI scores 80% effortlessly — human \"taste\" and \"unique perspective\" are the decisive edge. Creativity is the scarce trait AI cannot replace.":
        "AI scores eighty percent on autopilot. What separates the great from the merely good is human taste — a point of view AI cannot copy. Creativity becomes the rarest currency.",
    "Use AI, question AI, collaborate with AI. Not \"can chat\" — but can judge when AI is wrong and when to trust it.":
        "Use AI. Question AI. Collaborate with AI. The skill isn't \"chatting\" — it's knowing when AI is wrong, and when its answers can be trusted.",
    "AI knows no setback. Students iterate through failure to become protagonists. Advancing through uncertainty is the rarest trait in the AI era.":
        "AI never knows defeat. Students who can iterate through failure become the protagonists of their own stories. The ability to keep moving through uncertainty is the rarest trait of all.",
    "Human traits AI can never replace. Curiosity drives lifelong learning — the only insurance against 44% skill obsolescence.":
        "Curiosity is the one human trait AI will never replace. It powers lifelong learning — the only real insurance against forty-four percent skill obsolescence.",
    "These skills are all at the core of AI education":
        "Every one of these skills sits at the centre of AI education",
    "Our school's AI INFINITY strategy is built around these five skills — not trend-chasing, but grounded in WEF and OECD research.":
        "Our AI INFINITY strategy is built around these five skills — not because they're trendy, but because WEF and OECD research demands it.",

    # === P4 HK ===
    "HK AI Education": "Hong Kong's AI Education",
    "Has Already Launched": "Is Already Underway",
    "Our school is one of the earliest practitioners.":
        "Our school is among the very first to put it into practice.",
    "Government one-time grant supporting \"AI for ALL Subjects\" rollout, aligned with the EDB Digital Literacy Framework.":
        "A one-off government grant supporting an \"AI for ALL Subjects\" rollout, aligned with the EDB's Digital Literacy Framework.",
    "Our school has applied and fully implemented.":
        "We've applied for it — and put it fully to work.",
    "HKU-led Quality Education Fund network programme studying AI-era self-learning models.":
        "An HKU-led Quality Education Fund network programme studying self-directed learning in the AI era.",
    "Our school is one of the participating schools":
        "We are one of the participating schools",
    ", co-practising with top schools across Hong Kong.":
        ", working alongside Hong Kong's leading schools.",
    "First to adopt enterprise-grade AI": "First in the District to Adopt Enterprise AI",
    "Fully adopting": "We've fully deployed",
    "— students use the same tools as industry.":
        " — our students learn on the same platform industry uses.",
    "Our school has been a":
        "We've already served as a ",
    "Jockey Club CoolThink@JC pilot school for years":
        "Jockey Club CoolThink@JC pilot school for several years",
    ", not a newcomer to AI education — but one of HK's earliest practitioners. On this foundation, we continue to update tools and refine pedagogy.":
        ". We're not newcomers to AI education — we're among Hong Kong's earliest pioneers. On that foundation, we keep refining our tools and our teaching.",

    # === P5 Matrix ===
    "Every subject has": "Every subject has",
    "a clear future direction": "a clear future direction",

    # === P6 Chinese ===
    "Turn Learning Chinese into": "Turning Chinese Class into",
    "a Card Battle": "a Card Battle",
    "Input idiom sentences → AI": "Students write a sentence using a Chinese idiom → AI",
    "(20% chance) to draw": "with a 20% chance of drawing",
    "a UR General Card": "an Ultra-Rare General Card",
    "(Yue Fei, Guan Yu, Li Jing).": " — Yue Fei, Guan Yu, or Li Jing — built around character education.",
    "🏆 HK Primary Merit Award · selected from 103 entries":
        "🏆 HK Primary Merit Award · chosen from 103 entries",

    # === P7 Dictation ===
    "Teachers + Gemini · Co-developed": "Built by Our Teachers, with Gemini",
    "School Dictation Tool": "A school-grown dictation tool",
    "Developed jointly by our teachers and Gemini using":
        "Built by our teachers in dialogue with Gemini, using ",
    "— no coding experience required, turning teachers' pedagogical insight into ready-to-use tools.":
        " — no coding experience needed. We turned teachers' classroom instinct into a tool students can use today.",
    "Designed for lower primary:":
        "Made for our youngest learners:",
    "school-presets auto-fill":
        "school dictation lists auto-fill",
    ". Students self-select scope, AI reads aloud, instant grading — children can":
        ". Students choose their scope, AI reads it aloud, marks them on the spot — so children can ",
    "self-study at home": "study on their own at home",
    "Parents no longer need to read aloud — AI never tires, available anytime, infinitely patient.":
        "Parents no longer have to read words aloud. AI never tires, never loses patience, and is always ready when you are.",

    # === P8 Math ===
    "Cracking the 70-Year Problem": "Cracking a 70-Year-Old Problem",
    "Senior students write AI programs":
        "Senior students build AI programs themselves",
    "for juniors — P5/P6 students build multiplication practice tools for P2 students to use.":
        " — P5 and P6 students design multiplication tools that P2 classmates actually use.",
    "AI doesn't give answers but asks back: \"Why think this way? Any other approaches?\" Training critical thinking.":
        "AI refuses to hand over the answer. Instead it asks back: \"Why that approach? What else could you try?\" — training critical thinking by reflex.",
    "Students draw characters by hand → AI generates":
        "Students hand-draw their own characters → AI generates",
    "→ students explain and fact-check.":
        " → then students explain and fact-check the result themselves.",
    "— 1-on-1 tutoring lifts students from the 50th to 98th percentile.":
        " — one-on-one tutoring lifts students from the 50th to the 98th percentile.",

    # === P9 Joyfully Chinese ===
    "From App Inventor to": "From App Inventor to",
    "AI TCG Cards": "AI Trading Cards",
    "AI \"Joyfully Chinese\" Cultural App": "AI \"Joyfully Chinese\" App",
    "· Three generations of evolution":
        "· Three generations of evolution",
    "Starting from Computer class — students use MIT App Inventor visual coding to build first-generation cultural games. Foundation-era coding training.":
        "It began in Computer class. Students used MIT App Inventor's visual blocks to build the first generation of cultural games — the foundational coding work that started it all.",
    "Reinterpreting Chinese culture with AI.":
        "AI lets students reinterpret Chinese culture in their own voice.",
    "3rd place out of 500 teams HK-wide":
        "Third place across 500 teams Hong Kong-wide",
    "Upgraded from App to physical + AI card system — students input idiom sentences, AI scores live and draws SSR / SR General cards.":
        "The App grew into a physical + AI card system. Students enter idiom sentences, AI scores them live, and SSR / SR General cards are drawn on the spot.",
    "True cultural inheritance is not turning students into historical bystanders, but into culture's re-creators.":
        "Real cultural inheritance isn't about turning students into bystanders of history — it's about turning them into culture's re-creators.",

    # === P9b Cultural Fitting Room ===
    "takes you through time and space": "takes you across time and space",
    "AI camera + large screen interface — student stands before the camera, AI instantly \"dresses\" them in ethnic costumes (Tibetan, Miao, Mongolian) backgrounds.":
        "An AI camera and a large screen. The student stands in front, and AI instantly dresses them in Tibetan, Miao, or Mongolian costumes — placed against the appropriate cultural backdrop.",
    "From \"reading culture\" to \"personally wearing\" — aligned with the EDB Values Education Framework. Students take home their try-on photos to share.":
        "From reading about culture to wearing it. Aligned with the EDB Values Education Framework — and students take their try-on photos home to keep the conversation going.",
    "AI doesn't replace the real costume experience, but lowers the barrier — letting every student bridge time and connect personally with diverse cultures.":
        "AI doesn't replace authentic dress-up — it lowers the barrier so every student can connect personally with cultures across time.",

    # === P10 Science ===
    "From Lab Reports to": "From Lab Reports to",
    "Real-World Inquiry": "Real-World Inquiry",
    "Students use the AI plant ID app in the school garden, integrating live observation, AI tools, and taxonomic knowledge — Hattie d=0.50 inquiry learning.":
        "In the school garden, students use an AI plant-ID app — combining live observation, AI tools, and taxonomy. (Hattie d=0.50 inquiry learning.)",
    "Through hands-on encounter with the Aldabra giant tortoise paired with AI species ID — students transform from conservation bystanders into participants.":
        "A hands-on encounter with the Aldabra giant tortoise, paired with AI species identification. Students stop being conservation spectators — they become participants.",
    "School adopts the Yaoshan crocodile lizard (China's Class-1 protected, globally endangered). Combined with IoT sensors and an AI monitoring system.":
        "We've adopted a Yaoshan crocodile lizard (China's Class-1 protected, globally endangered) — paired with IoT sensors and an AI monitoring system.",
    "See the Flagship page.": "Details on the Flagship page →",

    # === P11 Music ===
    "From Music Theory to": "From Theory to",
    "Family AI Co-creation": "Family AI Co-Creation",
    "Parents and students co-create Cantonese songs with Suno AI, themed on fruits and nutrition. Results uploaded to Padlet for school-wide sharing — parents transform from \"supervisors\" into \"co-learning partners\".":
        "Parents and children co-write Cantonese songs in Suno AI, themed around fruit and nutrition. The results land on Padlet for the whole school. Parents stop being supervisors and become co-learners.",
    "When students discover they \"can compose\", their passion for music turns from passive to active. AI doesn't replace creation but lowers the barrier — aligned with UNESCO's creative expression framework.":
        "The moment students realise they can compose, their relationship with music flips from passive to active. AI isn't replacing creation — it's lowering the barrier (in the spirit of UNESCO's creative expression framework).",
    "Music used to focus on appreciation and singing — hard for students to experience real creation. Suno changes everything.":
        "Music class used to be about appreciation and singing. Real creation was out of reach. Suno changes that overnight.",

    # === P12 PE ===
    "From Demos to": "From Demos to",
    "IoT Data PE": "IoT-Powered PE",
    "Students' rope-skipping triggers AI vision recognition, jump counts become \"clean-air cannon\" energy defeating pollution monsters — turning":
        "Rope-skipping triggers AI vision recognition. Each jump powers a \"clean-air cannon\" that defeats a pollution monster — turning ",
    "fitness training into a national-treasure guardian mission.":
        " a fitness drill into a mission to guard a national treasure.",
    "Large-screen AI vision installed in the gym calculates rope-skips and long-jumps in real time — meeting WHO children-activity guideline data literacy requirements.":
        "Big-screen AI vision in the gym counts rope-skips and long-jump distances live — meeting WHO children-activity data-literacy guidelines.",
    "The system emphasises personal improvement, not class ranking — avoiding peer-comparison anxiety. Data for personal reference only,":
        "The focus is on personal improvement, not class rankings — to avoid peer-comparison anxiety. Data is for the individual student only,",
    "no heart-rate/oxygen logging, no naming":
        "no heart-rate or oxygen logging, no public naming",

    # === P13 Visual Arts ===
    "From Imitation to": "From Imitation to",
    "Heritage + Innovation": "Heritage Meets Innovation",
    "Students first draft characters with traditional ink, then use AI tools to transform them into dynamic works — tradition and innovation aren't opposites but complement each other. Aligned with 21st-Century 4C skills.":
        "Students first draft characters in traditional ink, then use AI to bring them alive as dynamic works. Tradition and innovation aren't enemies — they complete each other. (Aligned with 21st-Century 4C skills.)",
    "Graduation career planning integrated with visual arts — students design APP interface drafts for their future careers, then refine the visuals with AI.":
        "Graduation career planning meets visual arts. Students draft APP interfaces for the careers they imagine — then refine the visuals with AI.",
    "AI doesn't replace the brush but expands students' imagination of \"creation\". Our duty: teach them to judge which version has their own soul.":
        "AI doesn't replace the brush. It widens what \"creation\" can mean. Our job: to help students recognise which version still has their own soul in it.",

    # === P14 Flagship ===
    "China Class-1 Protected · Globally Endangered Species":
        "Class-1 Protected in China · Globally Endangered",
    "One of few HK primary schools legally permitted to adopt.":
        "One of the few primary schools in Hong Kong legally permitted to adopt one.",
    "Temperature, humidity, and light sensors upload in real time.":
        "Temperature, humidity, and light sensors stream live to the cloud.",
    "Cameras recognise daily behaviour, logging health.":
        "Cameras recognise daily behaviour and log health changes automatically.",
    "Science + STEAM + Humanities + IT.":
        "Science · STEAM · Humanities · IT.",

    # === P15 Curriculum ===
    "Two-Stage Spiral": "A Two-Stage Spiral",
    "Computational Thinking + AI Intro": "Computational Thinking · AI Foundations",
    "Through gamified, hands-on operations (e.g. Matatalab tangible coding), cultivating foundational logical problem-solving.":
        "Through gamified, hands-on play — Matatalab tangible coding, for example — students build the foundational logic they'll need for everything else.",
    "Generative AI is not yet introduced in P1-P3, protecting early cognitive development.":
        "We hold back generative AI in P1-P3 — protecting early cognitive development first.",
    "Enterprise AI + Cross-Subject PBL": "Enterprise AI · Cross-Subject PBL",
    "Full enterprise-grade AI rollout with deep cross-disciplinary projects.":
        "Full enterprise-grade AI deployment, anchored in deep cross-disciplinary projects.",
    "Student-group / competition works (Idiom Battle, Cultural Fitting Room, National Treasure Steward) are extracurricular self-inquiry.":
        "Student-group and competition works (Idiom Battle, Cultural Fitting Room, National Treasure Steward) are extracurricular — driven by the students themselves.",

    # === P16 Ethics ===
    "Introducing AI": "Bringing in AI",
    "Requires Clear Boundaries": "Demands Clear Boundaries",
    "🚫 Red Line 1: Never replace human judgement":
        "🚫 Red Line 1: AI Never Replaces Human Judgement",
    "AI assists and inspires; teacher and student judgement always prevail.":
        "AI assists and inspires. Teacher and student judgement always have the final word.",
    "🚫 Red Line 2: Never output unverified facts":
        "🚫 Red Line 2: No Unverified Facts",
    "Students must learn to fact-check; ultimate accuracy is the author's responsibility.":
        "Students learn to fact-check. Ultimate accuracy rests with the author — always.",
    "— three tracks in parallel, avoiding AI ghostwriting.":
        " — three parallel tracks, designed to make AI ghostwriting impossible.",
    "Paper-pen isn't replaced, but no longer reflects true AI-era capability.":
        "Paper and pen aren't replaced — but they no longer measure true ability in the AI era.",

    # === P17 Awards ===
    "Recognised by Industry": "Recognised by the Wider World",
    "HK Primary Chinese Culture Education Competition · 3rd place out of 500 teams.":
        "HK Primary Chinese Culture Education Competition · third place from 500 teams.",
    "National Identity App Design Competition · selected from 103 entries.":
        "National Identity App Design Competition · selected from 103 entries.",
    "Our representatives at the London BETT EdTech Expo.":
        "Our school will represent Hong Kong at the London BETT EdTech Expo.",

    # === P18 Workshop ===
    "Parents Aren't Just Bystanders": "Parents Aren't Just Bystanders",
    "You're an AI Creator Too": "You're an AI Creator Too",
    "\"Gemini × Poe Hands-On Workshop\" — easily guide children's self-learning. Starting from zero coding, parents build their child's AI dictation app in 30 minutes.":
        "Our \"Gemini × Poe Hands-On Workshop\" shows parents how to guide self-learning at home. From zero coding experience to a working AI dictation app — built for your own child, in 30 minutes.",
    "At least twice per term, aligned with student curriculum — keeping parents' AI knowledge in sync with the school.":
        "Held at least twice each term, in lockstep with the student curriculum — so parents stay current with what the school is doing.",
    "Hands-on practice lets parents understand AI isn't magic. Home AI conversations now have quality and boundaries.":
        "Once parents have built something themselves, they understand: AI isn't magic. Conversations about AI at home suddenly have substance — and limits.",

    # === P19 Future ===
    "Next Step": "What Comes Next",
    "Three Plans": "Three Initiatives",
    "Permanent campus showcase gathering all students' AI works — from concept comics to full apps.":
        "A permanent campus exhibit gathering students' AI works across the years — from concept comics to fully working apps.",
    "5G IoT sensing garden, real-time eco-data — temperature, humidity, species ID live-upload.":
        "A 5G IoT sensing garden streaming live ecological data — temperature, humidity, and species ID, in real time.",
    "From \"using AI\" to \"teaching AI\" — parents and students learn together, building deep connections.":
        "From using AI to teaching AI. Parents and children learn side by side — and the relationship deepens.",

    # === P20 CTA ===
    "From Consumers of Technology": "From Consumers of Technology",
    "to Creators in the Real World": "to Creators of the Real World",
    "We hope every student transforms from a \"tech consumer\"":
        "We hope every student moves from being a \"consumer of technology\"",
    "into \"a creator who solves real problems with tech\".":
        "to a creator who uses technology to solve real problems.",
    "Thank You for Joining Us Today": "Thank You for Being Here",

    # Misc connectors
    "Source:": "Source:",
    "Research basis:": "Research basis:",
    "Music Department": "— Music Department",
    "Ms Cheung · Visual Arts": "— Ms Cheung, Visual Arts",
    "Principal Ms Hui · RTHK Interview": "— Principal Ms Hui, RTHK interview",
    "School lead:": "School lead:",
    "Partner:": "Partner:",
    "Dean Siu, Mr Yeung ·": "Dean Siu · Mr Yeung",
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


# Apply NATIVE_REWRITES to text nodes (longest-first)
text_nodes = list(soup.find_all(string=True))
for node in text_nodes:
    if isinstance(node, Comment):
        continue
    if is_in_skip_zone(node):
        continue
    s = str(node)
    new_s = s
    for awkward, native in sorted(NATIVE_REWRITES.items(), key=lambda x: -len(x[0])):
        if awkward in new_s:
            new_s = new_s.replace(awkward, native)
    if new_s != s:
        node.replace_with(NavigableString(new_s))

# Set v4 version badge in lang switcher
for btn in soup.find_all('button', attrs={'data-lang': True}):
    if btn.get('data-lang') == 'e':
        btn['class'] = (btn.get('class', []) + ['active']) if 'active' not in btn.get('class', []) else btn.get('class', [])

# Also update file-mapping for V4 in JS (so cross-version switch goes to V4 files)
en_html = str(soup)
en_html = en_html.replace(
    "'t': 'AI_INFINITY_精選_20頁_v3.html'",
    "'t': 'AI_INFINITY_精選_20頁_v4.html'"
)
en_html = en_html.replace(
    "'s': 'AI_INFINITY_精選_20頁_v3-cn.html'",
    "'s': 'AI_INFINITY_精選_20頁_v4-cn.html'"
)
en_html = en_html.replace(
    "'e': 'AI_INFINITY_精選_20頁_v3-en.html'",
    "'e': 'AI_INFINITY_精選_20頁_v4-en.html'"
)

DST_EN.write_text(en_html, encoding="utf-8")
print(f"✓ {DST_EN.name} ({DST_EN.stat().st_size/1024:.0f} KB)")

# Diagnostic
visible = re.sub(r'<script[\s\S]*?</script>', '', en_html)
visible = re.sub(r'<style[\s\S]*?</style>', '', visible)
chinese_count = len(re.findall(r'[一-龥]', visible))
print(f"  Chinese chars remaining: {chinese_count}")
