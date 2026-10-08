# -*- coding: utf-8 -*-
with open("/Volumes/Ext/dev/python/pdf_compressor/心理学导论_精校全解版.md", "r", encoding="utf-8") as f:
    text = f.read()

import re
ch4 = re.search(r"# 第四章\s*心理的环境基础.*?(?=# 第五章)", text, re.DOTALL).group(0)

# Print specific raw sections
print("Chapter 4 extracted raw text size:", len(ch4))
