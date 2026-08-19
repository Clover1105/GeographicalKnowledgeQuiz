# 将向量化后的数据集存入向量数据库

import os
import json
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from ai.LoadEmbeddingModel import load_embedding_model

load_dotenv()

# 处理数据集 -- 数据集路径、向量数据库路径、集合名称
database_path = os.getenv("DATABASE_PATH")
chromadb_path = os.getenv("CHROMADB_PATH")
collection_name = os.getenv("COLLECTION_NAME")

# 读取数据
documents = []
with open(database_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip() # 去除换行符
        if not line:
            continue
        item = json.loads(line)
        # 将问题和答案拼接
        content = f"{item['question']}\n{item['answer']}"
        # 转为Document格式
        doc = Document(
            page_content=content,
            metadata = {
                "score": item.get("source",database_path),
                "category":item.get("category",""),
                "question": item["question"]
            }
        )
        documents.append(doc)

# 将数据集存入向量数据库
# 处理好的数据集、向量化模型、向量数据库路径、集合名称、匹配规则（余弦相似度）
try:
    Chroma.from_documents(
        documents,
        embedding= load_embedding_model(),
        persist_directory=chromadb_path,
        collection_name=collection_name,
        collection_metadata={"hnsw:space": "cosine"}
    )
    print("数据集存入向量数据库成功")
except Exception as e:
    print(f"数据集存入向量数据库失败: {e}")