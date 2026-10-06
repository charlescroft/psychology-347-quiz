with open("/Volumes/Ext/dev/python/pdf_compressor/web/app.js", "r", encoding="utf-8") as f:
    text = f.read()

print("Current app.js lines:", len(text.splitlines()))
