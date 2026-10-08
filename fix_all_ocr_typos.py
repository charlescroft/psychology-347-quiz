# -*- coding: utf-8 -*-
import json
import re

# 1. Clean web/questions.js
with open("/Volumes/Ext/dev/python/pdf_compressor/web/questions.js", "r", encoding="utf-8") as f:
    raw = f.read()

# Direct string replacements in questions.js
replacements = [
    ("在一定时快决定", "在一定时刻决定"),
    ("一定时快决定", "一定时刻决定"),
    ("时快决定", "时刻决定"),
    ("时快", "时刻"),
    ("cg：", "eg："),
    ("cg:", "eg:"),
    ("少族民族", "少数民族"),
    ("肖（", "（"),
    ("消（", "（"),
    ("消一", "一"),
    ("简指一", "一"),
    ("驱体", "躯体"),
    ("许遵守", "遵守"),
    ("许周", "四周"),
    ("简谷", "简答"),
    ("的的人类", "的人类"),
    ("E 例如的波形", "EEG的波形"),
    ("動一稳态", "动-稳态"),
]

fixed_count_q = 0
for src, dst in replacements:
    if src in raw:
        cnt = raw.count(src)
        raw = raw.replace(src, dst)
        fixed_count_q += cnt
        print(f"questions.js: Replaced '{src}' -> '{dst}' ({cnt} times)")

# Parse to verify JSON validity
json_str = raw.replace("window.QUESTIONS_DATA = ", "").rstrip(";\n ")
data = json.loads(json_str)

with open("/Volumes/Ext/dev/python/pdf_compressor/web/questions.js", "w", encoding="utf-8") as f:
    f.write("window.QUESTIONS_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")

print(f"Updated web/questions.js with {fixed_count_q} typo fixes!")

# 2. Clean 心理学导论_精校全解版.md
with open("/Volumes/Ext/dev/python/pdf_compressor/心理学导论_精校全解版.md", "r", encoding="utf-8") as f:
    md_raw = f.read()

fixed_count_md = 0
for src, dst in replacements:
    if src in md_raw:
        cnt = md_raw.count(src)
        md_raw = md_raw.replace(src, dst)
        fixed_count_md += cnt
        print(f"MD: Replaced '{src}' -> '{dst}' ({cnt} times)")

# Clean orphan character 峇
if "峇" in md_raw:
    md_raw = md_raw.replace("峇", "")
    print("MD: Removed orphan character '峇'")

with open("/Volumes/Ext/dev/python/pdf_compressor/心理学导论_精校全解版.md", "w", encoding="utf-8") as f:
    f.write(md_raw)

with open("/Users/charles/Downloads/心理学导论_精校全解版.md", "w", encoding="utf-8") as f:
    f.write(md_raw)

print(f"Updated 心理学导论_精校全解版.md with {fixed_count_md} typo fixes!")
