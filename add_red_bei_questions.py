# -*- coding: utf-8 -*-
import json

with open("/Volumes/Ext/dev/python/pdf_compressor/web/questions.js", "r", encoding="utf-8") as f:
    raw = f.read()
    json_str = raw.replace("window.QUESTIONS_DATA = ", "").rstrip(";\n ")
    data = json.load(json_str)

questions = data["questions"]
recitations = data.get("recitations", [])

# 1. Page 4: 心理学的任务 (红色手写 "背")
questions.append({
    "id": f"c1_choice_{len(questions)+1}",
    "chapterId": 1,
    "type": "choice",
    "title": "从质和量上记录心理现象的存在状态，作为心理学家进行系统实证研究的第一项任务与最基本目的是（ ）。",
    "options": [
        "A. 描述心理事件",
        "B. 揭示心理规律",
        "C. 探明心理机制",
        "D. 调控心理行为"
    ],
    "answer": "A",
    "explanation": "原笔记第4页红色手写【背】重点标注：心理学的任务包括描述、解释、预测和控制。其中‘从质和量上描述心理事件’是实证研究的第一项任务与最基础目的。",
    "points": [],
    "examTag": "【学姐红色手写“背”】",
    "trapOption": "B. 揭示心理规律",
    "trapAnalysis": "‘揭示心理规律’是在描述基础上的解释深化（第二项任务）；第一项最基础的实证任务必然是客观的‘描述心理事件’。"
})

recitations.append({
    "id": f"rec_1_{len(recitations)+1}",
    "chapterId": 1,
    "category": "简答大题",
    "title": "【学姐红色手写“背”】简述心理学的四大基本任务及其层级关系",
    "sourceTag": "【学姐红色手写“背”·核心必背】",
    "answer": "原笔记第4页红色手写必背要点：\n1. 描述心理事件：从质和量上客观记录心理现象的存在状态，是实证研究的第一项任务与最基本目的；\n2. 揭示心理规律：阐明各种心理现象发生、发展、变化的内在必然联系；\n3. 探明心理机制：深入神经生理、脑机制和认知加工算法解释心理现象为什么会发生；\n4. 确定心理机能与调控：根据心理规律对未来的心理和行为进行科学预测，并对异常不良行为进行有效调控与干预。",
    "points": [
        "1. 描述心理事件：质与量客观记录（实证研究第一任务与最基本目的）",
        "2. 揭示心理规律：阐明心理现象发生发展的内在必然联系",
        "3. 探明心理机制：深入神经生理与内部信息加工机制解释机理",
        "4. 调控心理行为：根据规律进行科学预测与行为干预引导"
    ]
})

# 2. Page 34: 玛西亚青少年自我同一性四种状态 (红色手写 "直接背" + 【2024选】)
questions.append({
    "id": f"c5_choice_{len(questions)+1}",
    "chapterId": 5,
    "type": "choice",
    "title": "某大一学生从未经历过对自己未来职业方向的独立探索与怀疑，从小到大完全按照父母的严厉规划报考了军校，坚信‘父母给我选的路永远是最好的’。根据玛西亚（Marcia）的自我同一性理论，该学生的自我同一性状态属于（ ）。",
    "options": [
        "A. 同一性获得（Identity Achievement）",
        "B. 同一性拒斥 / 同一性早闭（Identity Foreclosure）",
        "C. 同一性延缓（Identity Moratorium）",
        "D. 同一性混乱 / 同一性弥散（Identity Diffusion）"
    ],
    "answer": "B",
    "explanation": "原笔记第34页红色手写标注【直接背】【2024选真题】：玛西亚依据‘是否经历探索’和‘是否做出承诺’将同一性分为四种状态。‘未经历自主探索，却提前对父母或权威安排做出无条件承诺’的状态被称为同一性拒斥（早闭）。",
    "examTag": "【2024选·红色手写“直接背”】",
    "trapOption": "A. 同一性获得",
    "trapAnalysis": "‘同一性获得’必须经历过自主危机探索之后做出的成熟承诺；没有探索过程直接继承父母安排属于‘同一性早闭/拒斥’（Foreclosure）；正在探索但未做承诺属于‘延缓’；既不探索也不承诺属于‘弥散’。"
})

recitations.append({
    "id": f"rec_5_{len(recitations)+1}",
    "chapterId": 5,
    "category": "简答大题",
    "title": "【2024选·学姐红色手写“直接背”】简述玛西亚（Marcia）提出的青少年自我同一性的四种状态及其特征",
    "sourceTag": "【2024选·红色手写“直接背”】",
    "answer": "原笔记第34页红色手写必背要点：玛西亚依据‘是否经历同一性探索危机’和‘是否确立明确承诺’两个维度，将青少年自我同一性划分为四种状态：\n1. 同一性获得（Identity Achievement）：既经历了深思熟虑的自主危机探索，又确立了坚定的人生目标与职业承诺。是最高度成熟的同一性状态；\n2. 同一性延缓（Identity Moratorium）：当前正处于激烈的危机探索与尝试过程中，但尚未确立固定的最终承诺（处于心理社会的延缓期）；\n3. 同一性拒斥 / 早闭（Identity Foreclosure）：从未经历过自主探索和怀疑危机，但盲目接受了父母、权威或社会的预先安排并做出承诺；\n4. 同一性弥散 / 混乱（Identity Diffusion）：既没有经历探索的动力，也从未做出任何人生承诺，随波逐流无所事事，表现为退缩与角色混乱。",
    "points": [
        "划分维度：是否经历危机探索 ＋ 是否确立个人承诺",
        "1. 同一性获得：有探索 ＋ 有承诺（成熟统合状态）",
        "2. 同一性延缓：有探索 ＋ 无承诺（正处于积极探寻期）",
        "3. 同一性拒斥/早闭：无探索 ＋ 有承诺（盲从父母权威安排）",
        "4. 同一性弥散/混乱：无探索 ＋ 无承诺（随波逐流角色混乱）"
    ]
})

# 3. Page 20: 勒温生活空间理论与公式 (红色手写标J)
questions.append({
    "id": f"c4_choice_{len(questions)+1}",
    "chapterId": 4,
    "type": "choice",
    "title": "格式塔心理学家勒温（Lewin）提出的著名行为公式为 B = f(P, E)，该公式表明个体的外显行为（B）是下列哪两者的函数？（ ）",
    "options": [
        "A. 生理成熟（P）与社会文化（E）",
        "B. 个体内在人格与心理（P）与生活空间中可感知到的环境情境（E）",
        "C. 物理环境（P）与客观事实（E）",
        "D. 刺激变量（P）与反应变量（E）"
    ],
    "answer": "B",
    "explanation": "原笔记第20页红色手写重点公式：B = f(P, E) = f(Ls)。B代表行为，P代表个体的人（Person），E代表环境（Environment），二者交互作用构成了决定个体行为的全部事实总和——生活空间（Life space）。",
    "examTag": "【学姐红色手写“背”】",
    "trapOption": "C. 物理环境与客观事实",
    "trapAnalysis": "勒温特别强调环境必须是‘准物理/心理环境’（个体主观感知到的生活空间），而非客观物理事实。"
})

data["questions"] = questions
data["recitations"] = recitations

with open("/Volumes/Ext/dev/python/pdf_compressor/web/questions.js", "w", encoding="utf-8") as f:
    f.write("window.QUESTIONS_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")

print(f"Added exact red '背' questions & recitations! Total questions: {len(questions)}, Total recitations: {len(recitations)}")
