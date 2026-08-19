# 创建llm大模型对象

from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

# 好像是直接在模型下载网站复制的
def create_model():
    return ChatOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model=os.getenv("LLM_MODEL_NAME"),
        streaming=True,
    )