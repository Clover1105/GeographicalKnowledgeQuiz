# 加载重排序模型

import os
from dotenv import load_dotenv
load_dotenv()
from FlagEmbedding import FlagReranker

def load_reranker():
    return FlagReranker(
        model_name_or_path=os.getenv("RERANKER_MODEL_PATH"),
        use_fp16=True,
    )