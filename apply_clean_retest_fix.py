# -*- coding: utf-8 -*-

# Let us verify the file read
with open("/Volumes/Ext/dev/python/pdf_compressor/web/app.js", "r", encoding="utf-8") as f:
    text = f.read()

print("Original app.js read successfully, length:", len(text))
