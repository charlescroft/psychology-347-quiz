# -*- coding: utf-8 -*-
import json

with open("/Volumes/Ext/dev/python/pdf_compressor/web/questions.js", "r", encoding="utf-8") as f:
    raw = f.read()
    json_str = raw.replace("window.QUESTIONS_DATA = ", "").rstrip(";\n ")
    data = json.loads(json_str)

questions = data.get("questions", [])
recitations = data.get("recitations", [])

# 1. Update Chapter 6 recitations to include full Section 一 and Section 二 verbatim
# Find existing rec_6_1 and rec_6_4
for r in recitations:
    if r["chapterId"] == 6:
        # Check if it is the level of consciousness card
        if "意识的四种水平" in r["title"] or "意识水平" in r["title"]:
            r["title"] = "【2025选·学姐红色手写“背”】简述意识的五种水平及其特征（简答）"
            r["sourceTag"] = "【2025选·学姐红色手写“背”】"
            r["answer"] = (
                "原笔记第38页红色手写必背要点：\n"
                "意识并非只有一种水平，人们对信息的加工可以在不同的觉知水平上进行。不同的意识水平主要有五种：\n"
                "1. 焦点意识：人们集中注意而获得的清晰意识。任何时候，人们总是忽略一些刺激，选择一些刺激并屏蔽一些刺激；\n"
                "2. 下意识（与焦点意识相对应）【2019选】：未被注意的信息也是被登记和评估的，在觉知的下意识水平上起作用。边缘意识属于下意识（如鸡尾酒会现象）；\n"
                "3. 前意识【2017选】（承上启下）：人脑中许多当前不在意识之中的记忆和思维，在必要时可以把它带到意识中。如果想回忆的话就可以回忆起来，这时这些记忆便成为意识中清晰的组成部分；\n"
                "4. 潜意识：弗洛伊德创造的概念。某些痛苦记忆、冲动和欲望被压抑无法进入意识并继续影响人们的行为，是内省不能达到的心理现象（记忆和心理）；\n"
                "5. 非意识：身体内部由自主神经系统所支配的一些生理变化（如脑电活动、心跳、血压调节等生理活动），在正常情况下完全不被意识觉察。"
            )
            r["points"] = [
                "1. 焦点意识：集中注意获得的清晰意识（选择与屏蔽）",
                "2. 下意识（2019选）：未被注意的信息被登记评估，边缘意识（鸡尾酒会）",
                "3. 前意识（2017选）：承上启下，当前未觉知但随时可提取回忆入意识",
                "4. 潜意识：弗洛伊德概念，被压抑的痛苦欲望创伤，内省不能达到",
                "5. 非意识：自主神经支配的生理活动（脑电/心跳），正常不被意识觉知"
            ]

        # Check if it is the concept and characteristics card
        if "意识的三大基本特征" in r["title"]:
            r["category"] = "简答大题"
            r["title"] = "【学姐红色手写“背”】简述意识的概念及其三大基本特征（简答）"
            r["sourceTag"] = "【学姐红色手写“背”·核心必背】"
            r["answer"] = (
                "原笔记第38页第一节红色手写【背】字大题：\n"
                "1. 意识的概念：指个体的觉知状态，即对人们自身、对外界的环境事件以及自己与外界环境事件关系的觉知状态。意识对个体的身心系统起统合、管理和调控的作用。\n"
                "2. 意识的三大基本特征：\n"
                "① 主观性：每个人的意识世界都是专有的、独一无二的，人们可以直接觉知到自己的思想、情感和心境，却只能通过观察和聆听间接地理解他人的意识经验；\n"
                "② 统一性：人们意识到的经验是一个统一的整体。各种觉知形式都被整合为一个独特的、连贯的意识经验；\n"
                "③ 流动性：个人的意识经验是一个统一的整体，但意识的内容是不断变化的，从来不会静止不动。美国机能主义心理学的先驱詹姆斯创造出‘意识流’的概念来表示意识这一特征。"
            )
            r["points"] = [
                "意识概念：个体的觉知状态（对自身、外界及二者关系觉知），统合管理调控身心",
                "特征1 主观性：专有独一无二的主观私人经验，只能间接理解他人",
                "特征2 统一性：各种觉知形式整合为独特的、连贯统一的心智表象",
                "特征3 流动性：意识内容不断变化演进，詹姆斯提出‘意识流’"
            ]

# 2. Add specific objective questions covering Section 一 and Section 二
# Check if "非意识" is in questions
has_nonconscious = any("非意识" in q.get("title", "") for q in questions if q.get("chapterId") == 6)
if not has_nonconscious:
    questions.append({
        "id": f"c6_choice_{len(questions)+1}",
        "chapterId": 6,
        "type": "choice",
        "title": "身体内部的生理活动（如脑电波节律震荡、胃肠平滑肌蠕动、心跳与血压自律调节等），受自主神经系统支配，正常情况下完全不被主体所意识觉知。这种心理学觉知状态属于（ ）。",
        "options": [
            "A. 焦点意识",
            "B. 前意识",
            "C. 潜意识",
            "D. 非意识（Non-conscious）"
        ],
        "answer": "D",
        "explanation": "原笔记第38页第二节【意识水平】第五类：非意识指身体内部由自主神经支配的生理活动（如脑电、心跳），正常情况下无法被主观觉知。注意区分于潜意识（潜意识指受心理压抑的愿望创伤）。",
        "examTag": "【学姐红色手写“背”】",
        "trapOption": "C. 潜意识",
        "trapAnalysis": "考生极易混淆潜意识与非意识！‘潜意识’是心理动力学概念，包含被压抑的痛苦欲望、创伤经验，会间接通过梦或口误外显；‘非意识’是纯生理机制，心跳脑电血压正常情况下完全不能被意识感知。"
    })

# Check if 前意识承上启下 is in questions
has_preconscious = any("承上启下" in q.get("title", "") or "前意识" in q.get("title", "") for q in questions if q.get("chapterId") == 6)
if not has_preconscious:
    questions.append({
        "id": f"c6_choice_{len(questions)+1}",
        "chapterId": 6,
        "type": "choice",
        "title": "人脑中许多记忆和思维当前并不处于觉知中心，但在必要时或经过适当提示就可以立刻回忆起来，成为意识中清晰的组成部分。在意识水平划分中起到‘承上启下’过渡作用的是（ ）。",
        "options": [
            "A. 下意识",
            "B. 前意识（Preconscious）",
            "C. 潜意识",
            "D. 盲视"
        ],
        "answer": "B",
        "explanation": "原笔记第38页第二节【2017选真题】：前意识具有承上启下的枢纽作用，指当前不在意识之中，但想回忆的话就能回忆起来的记忆和思维（如被问到小学母校名字）。",
        "examTag": "【2017选真题·红色手写“背”】",
        "trapOption": "A. 下意识",
        "trapAnalysis": "下意识是边缘意识（如边听课边感知窗外）；前意识是处于潜意识与意识之间的信息，经检索线索激活可瞬间进入焦点意识。"
    })

data["questions"] = questions
data["recitations"] = recitations

with open("/Volumes/Ext/dev/python/pdf_compressor/web/questions.js", "w", encoding="utf-8") as f:
    f.write("window.QUESTIONS_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")

print(f"Updated Chapter 6 recitations and questions! Total questions: {len(questions)}, Total recitations: {len(recitations)}")
