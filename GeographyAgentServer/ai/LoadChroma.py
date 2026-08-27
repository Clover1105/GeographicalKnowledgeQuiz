# 连接向量数据库

import os
from langchain_chroma import Chroma
from ai.LoadEmbeddingModel import load_embedding_model

def load_chroma_conn():
    return Chroma(
        persist_directory=os.getenv("CHROMADB_PATH"),
        collection_name=os.getenv("COLLECTION_NAME"),
        embedding_function=load_embedding_model(),
    )