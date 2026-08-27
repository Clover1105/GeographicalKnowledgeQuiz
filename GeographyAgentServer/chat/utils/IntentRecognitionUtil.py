import json
import os
from langchain_ollama import ChatOllama

prompt = """
    角色设定：
        你是一个专业的地理知识意图识别助手。你的任务是分析用户的输入，判断其是否包含地理学科相关的内容或诉求。
    判定标准：
        相关：用户的问题涉及自然地理（如地形地貌、气候气象、水文土壤、植被生态）、人文地理（如人口民族、聚落城市、农业工业、交通旅游）、区域地理（如国家地区概况、行政区划、地理位置）、地理信息技术（如GIS、遥感、地图判读）以及地理现象成因分析等。即使问题表述口语化、模糊或存在错别字，只要核心诉求是寻求地理层面的知识解答、空间分析或地理事物描述，均判定为“相关”。
        不相关：用户的问题仅涉及日常闲聊、纯历史事件（无地理空间要素）、情感倾诉、通用生活常识、娱乐八卦、纯数理化计算（无地理背景）等，不包含任何地理学科要素。
    输出要求：
        仅输出一个JSON对象，不要包含任何其他解释文字：
        {
            "is_geography": true/false,
            "confidence": "high/medium/low"
        }
        不要输出任何解释、标点符号或其他多余的文字。
    示例参考：
        用户输入：为什么青藏高原夏季气温比同纬度地区低？
        输出：{"is_geography": true, "confidence": "high"}
        用户输入：巴西的首都是哪里？主要出口什么农产品？
        输出：{"is_geography": true, "confidence": "high"}
        用户输入：今天心情好差，不想上班。
        输出：{"is_geography": false, "confidence": "high"}
        用户输入：唐朝是怎么灭亡的？
        输出：{"is_geography": false, "confidence": "high"}
        用户输入：那个很有名的山叫什么来着，好像五岳之一？
        输出：{"is_geography": true, "confidence": "medium"}
    待分析的用户输入：
        {question}
    输出：
"""

def intent_recognition(question: str):
    # 创建llm大模型对象 -- 用于识别意图
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL_NAME"),
        base_url=os.getenv("OLLAMA_BASE_URL"),
    )
    # 提示词
    intent_prompt = prompt
    # 角色信息
    role = [
        {"role": "system", "content": intent_prompt},
        {"role": "user", "content": question}
    ]
    # 非流式输出
    result = llm.invoke(role)
    # 输出结果 -- result.content为str类型，要转换为dict类型 -- 不能直接dict()，用json.loads()
    return json.loads(result.content)

# 测试
if __name__ == "__main__":
    re = intent_recognition("感冒了怎么办？")
    print(re)
    print(type(re))
    re = intent_recognition("青藏高原夏季气温比同纬度地区低？")
    print(re)
    print(type(re))

