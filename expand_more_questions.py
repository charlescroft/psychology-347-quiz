# -*- coding: utf-8 -*-
import json

with open("/Volumes/Ext/dev/python/pdf_compressor/web/questions.js", "r", encoding="utf-8") as f:
    raw = f.read()
    json_str = raw.replace("window.QUESTIONS_DATA = ", "").rstrip(";\n ")
    data = json.loads(json_str)

print(f"Current questions: {len(data['questions'])}")
