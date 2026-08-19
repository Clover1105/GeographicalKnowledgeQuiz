# 加载向量化模型 -- 将数据向量化

from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()

def load_embedding_model():
    return HuggingFaceEmbeddings(
        model_name=os.getenv("EMBEDDING_MODEL_PATH"),
        # 本地加载
        model_kwargs={
            "device": "cuda",
            "local_files_only": True,
        },
    )
