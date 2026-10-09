# -*- coding: utf-8 -*-
import json
import os

with open("/Volumes/Ext/dev/python/pdf_compressor/web/questions.js", "r", encoding="utf-8") as f:
    raw = f.read()
    json_str = raw.replace("window.QUESTIONS_DATA = ", "").rstrip(";\n ")
    data = json.loads(json_str)

existing_questions = data["questions"]
existing_recitations = data.get("recitations", [])
diagrams = data.get("diagrams", {})
chapters = data["chapters"]

print(f"Base: {len(existing_questions)} questions, {len(existing_recitations)} recitations.")
