# -*- coding: utf-8 -*-
import json

with open("/Volumes/Ext/dev/python/pdf_compressor/web/questions.js", "r", encoding="utf-8") as f:
    raw = f.read()
    json_str = raw.replace("window.QUESTIONS_DATA = ", "").rstrip(";\n ")
    data = json.loads(json_str)

questions = data.get("questions", [])
recitations = data.get("recitations", [])

print(f"Base state: {len(questions)} questions, {len(recitations)} recitations.")

def add_r(chapter_id, category, title, answer, points, source_tag=""):
    r_id = f"rec_{chapter_id}_{len(recitations)+1}"
    recitations.append({
        "id": r_id,
        "chapterId": chapter_id,
        "category": category,
        "title": title,
        "sourceTag": source_tag,
        "answer": answer,
        "points": points or []
    })

# Check which chapters currently have 0 or very few cards
from collections import Counter
c_counts = Counter(r["chapterId"] for r in recitations)
print("Current flashcard counts per chapter:")
for cid in range(1, 19):
    print(f"  Ch {cid:2d}: {c_counts.get(cid, 0)} cards")
