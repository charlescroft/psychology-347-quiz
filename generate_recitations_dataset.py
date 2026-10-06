# -*- coding: utf-8 -*-
import json

recitations = []

def add_rec(chapter_id, category, title, answer, points, source_tag=""):
    r_id = f"rec_{chapter_id}_{len(recitations)+1}"
    recitations.append({
        "id": r_id,
        "chapterId": chapter_id,
        "category": category, # "名词解释", "简答大题", "概念辨析", "核心理论"
        "title": title,
        "sourceTag": source_tag,
        "answer": answer,
        "points": points or []
    })

print("Compiling authentic recitation flashcards...")
