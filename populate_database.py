# -*- coding: utf-8 -*-
import json
import os
from make_upgraded_bank import CHAPTER_DIAGRAMS

data = {
    "chapters": [
        {"id": 1, "title": "第一章 绪论", "desc": "心理学性质、心理现象划分、研究方法与历史学派"},
        {"id": 2, "title": "第二章 心理的起源和本性", "desc": "反映特性、感应性、动物心理演变与意识源起"},
        {"id": 3, "title": "第三章 心理的生物基础", "desc": "神经元、中枢神经系统、大脑皮层与三大机能系统"},
        {"id": 4, "title": "第四章 心理的环境基础", "desc": "环境与情境、生态系统理论、自然与社会文化环境"},
        {"id": 5, "title": "第五章 人的毕生发展", "desc": "天性与教养、研究设计、皮亚杰认知阶段与埃里克森八阶段"},
        {"id": 6, "title": "第六章 意识状态", "desc": "意识水平、睡眠阶段与功能、梦的理论与催眠机制"},
        {"id": 7, "title": "第七章 动机", "desc": "动机功能、耶克斯-多德森定律、生物动机与成就动机理论"},
        {"id": 8, "title": "第八章 注意", "desc": "注意特征、无意/有意/有意后注意、注意品质与认知理论"},
        {"id": 9, "title": "第九章 感觉", "desc": "感觉编码、感觉阈限定律、视听觉机制与经典色听理论"},
        {"id": 10, "title": "第十章 知觉", "desc": "知觉四大特征、格式塔组织原则、空间与深度知觉、错觉"},
        {"id": 11, "title": "第十一章 学习", "desc": "经典条件作用、操作条件作用强化程序、社会观察学习"},
        {"id": 12, "title": "第十二章 记忆", "desc": "三级加工系统、工作记忆模型、艾宾浩斯曲线与遗忘机制"},
        {"id": 13, "title": "第十三章 思维", "desc": "思维特征、概念形成、问题解决策略与影响心理因素"},
        {"id": 14, "title": "第十四章 言语", "desc": "语言与言语、言语中枢与失语症、言语感知麦格克效应"},
        {"id": 15, "title": "第十五章 情绪", "desc": "情绪成分与功能、经典情绪理论(詹-兰/坎-巴/沙-辛/阿诺德)"},
        {"id": 16, "title": "第十六章 意志", "desc": "意志特征、动机冲突类型、意志行动阶段与四大意志品质"},
        {"id": 17, "title": "第十七章 智力", "desc": "智力定义、比纳/韦克斯勒量表、二因素/多元/三元智力理论"},
        {"id": 18, "title": "第十八章 人格", "desc": "人格特性、气质与性格、特质论(奥尔波特/卡特尔/大五)、精神分析"}
    ],
    "diagrams": CHAPTER_DIAGRAMS,
    "questions": []
}

def add_q(chapter_id, q_type, title, answer, options=None, explanation="", points=None, exam_tag="", trap_option="", trap_analysis=""):
    q_id = f"c{chapter_id}_{q_type}_{len(data['questions'])+1}"
    data["questions"].append({
        "id": q_id,
        "chapterId": chapter_id,
        "type": q_type, # 'choice', 'judge', 'blank', 'short'
        "title": title,
        "options": options or [],
        "answer": answer,
        "explanation": explanation,
        "points": points or [],
        "examTag": exam_tag,
        "trapOption": trap_option,
        "trapAnalysis": trap_analysis
    })

print("Writing chapters...")
