# -*- coding: utf-8 -*-
import json

with open("/Volumes/Ext/dev/python/pdf_compressor/web/questions.js", "r", encoding="utf-8") as f:
    raw = f.read()
    json_str = raw.replace("window.QUESTIONS_DATA = ", "").rstrip(";\n ")
    data = json.loads(json_str)

questions = data.get("questions", [])

def add_q(chapter_id, q_type, title, answer, options=None, explanation="", points=None, exam_tag="【模拟】", trap_option="", trap_analysis=""):
    q_id = f"c{chapter_id}_{q_type}_{len(questions)+1}"
    questions.append({
        "id": q_id,
        "chapterId": chapter_id,
        "type": q_type,
        "title": title,
        "options": options or [],
        "answer": answer,
        "explanation": explanation,
        "points": points or [],
        "examTag": exam_tag,
        "trapOption": trap_option,
        "trapAnalysis": trap_analysis
    })

print(f"Current questions: {len(questions)}. Starting full-scale audit across remaining chapters...")
