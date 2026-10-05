# -*- coding: utf-8 -*-
import json
import os

with open("/Volumes/Ext/dev/python/pdf_compressor/web/questions.js", "r", encoding="utf-8") as f:
    raw = f.read()
    json_str = raw.replace("window.QUESTIONS_DATA = ", "").rstrip(";\n ")
    data = json.load(json_str)

def add_extra_q(chapter_id, q_type, title, answer, options=None, explanation="", points=None, exam_tag="", trap_option="", trap_analysis=""):
    q_id = f"c{chapter_id}_{q_type}_{len(data['questions'])+1}"
    data["questions"].append({
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

print(f"Starting expansion from {len(data['questions'])} questions...")
