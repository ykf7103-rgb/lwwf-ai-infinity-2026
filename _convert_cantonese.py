import sys

path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

orig_len = len(text)

phrase_repl = [
    ('我哋', '我們'), ('你哋', '你們'), ('佢哋', '他們'),
    ('而家', '現在'), ('點解', '為何'), ('點樣', '怎樣'),
    ('真係', '真的'), ('唔係', '不是'), ('唔再', '不再'),
    ('唔好', '不要'), ('唔識', '不懂'), ('鍾意', '喜歡'),
    ('即係', '即是'), ('一齊', '一起'),
    ('就係', '就是'), ('都係', '都是'), ('而係', '而是'),
    ('但係', '但是'), ('之但係', '但是'),
    ('主要係', '主要是'), ('真正係', '真正是'),
    ('係嘅', '是的'), ('係咪', '是否'), ('係時候', '是時候'),
    ('多咗', '多了'), ('少咗', '少了'),
    ('話畀', '告訴'),
    ('知唔知', '知不知'),
    ('搞掂', '完成'),
    ('教唔到', '教不到'),
    ('做緊', '正在做'),
    ('嗰陣', '那時候'), ('嗰個', '那個'), ('嗰啲', '那些'),
    ('嗰度', '那裏'), ('呢個', '這個'), ('呢啲', '這些'),
    ('呢度', '這裏'), ('好似', '好像'),
    ('簡單啲', '簡單些'),
]

char_repl = [
    ('嘅', '的'), ('喺', '在'),
    ('唔', '不'), ('啲', '些'),
    ('嗰', '那'), ('咁', '這樣'),
    ('攰', '累'), ('揀', '選擇'),
    ('諗', '想'), ('拎', '拿'),
    ('慳', '節省'), ('畀', '給'),
    ('嚟', '來'), ('噏', '說'),
    ('啱', '對'), ('咗', '了'),
    ('哋', '們'), ('佢', '他'),
    ('睇', '看'), ('呢', '這'),
]

for old, new in phrase_repl:
    text = text.replace(old, new)

for old, new in char_repl:
    text = text.replace(old, new)

text = text.replace('係', '是')

# Restore false positives where 係 is part of legitimate written Chinese
text = text.replace('關是', '關係')
text = text.replace('體是', '體系')
text = text.replace('世是', '世系')
text = text.replace('派是', '派系')
text = text.replace('的的', '的')
text = text.replace('們們', '們')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print(f"Original {orig_len} chars -> New {len(text)} chars (diff {len(text) - orig_len:+d})")
