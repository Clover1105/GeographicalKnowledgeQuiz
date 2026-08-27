import jieba
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from ai import LoadChroma

stop_words = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说",
    "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "那", "他", "她", "它", "们", "这个", "那个",
    "什么", "哪", "怎么", "吗", "呢", "吧", "啊", "哦","还", "被", "把", "让", "对", "与", "但", "而", "或", "成",
    "所","为", "以", "及", "可", "可以", "能", "能够", "应该", "需要", "已经", "虽然", "如果", "因为", "所以", "只是",
    "还是", "不过", "然后","之", "其", "中", "等", "等", "即", "使", "向", "将", "按", "当", "于", "由", "比", "除了",
    "关于", "以及", "并且", "此外", "另外", "过", "着", "来", "去", "做", "作", "像", "如", "如同", "由于","此", "彼",
    "某", "某些", "各", "每", "另", "别", "谁", "何", "哪里", "哪儿", "哪里", "多少", "几", "咱", "咱们", "大家", "跟",
    "同", "给", "替", "向", "往", "朝", "从", "自", "打", "沿", "顺着", "为了", "为着", "因为", "因而", "因此", "从而",
    "并且", "而且", "或者", "或是", "甚至", "无论", "不管", "尽管", "进行", "实施", "开展", "予以", "加以", "通过",
    "利用", "使用", "认为", "觉得", "感到", "希望", "想要", "打算", "准备", "，", "。", "！", "？", "；", "：", "、",
    "“", "”", "‘", "’", "（", "）", "【", "】", "《", "》", "—", "…", ".", ",", "!", "?", ";", ":", "\"", "'",
    "(", ")", "[", "]", "{", "}", "<", ">", "/", "\\", "|", "@", "#", "$", "%", "^", "&", "*", "_", "-", "+",
    "=", "呗", "嘛", "哈", "嘿", "哎", "哇", "咦", "哟", "嗯", "唔", "之乎者也", "等等", "之类", "有关", "如何", "为何"
                ])

# 分词函数
def cut_words(txts):
    txt = jieba.cut(txts)
    return [t for t in txt if t.strip() not in stop_words and len(t.strip()) >= 1]

# 获取bm25对象和文档内容
def build_bm25_index(vector):
    # 获取向量数据库中所有文档
    docs = vector.get()
    # print(docs)
    # print(docs.keys())    # ['ids', 'embeddings', 'documents', 'uris', 'included', 'data', 'metadatas']

    # 取出数据库中的内容
    ids = docs['ids']
    documents = docs['documents']
    metadatas = docs['metadatas']

    # 包装为list[Document]
    docs = [Document(id=ids[i],page_content=documents[i],metadata={"score":metadatas[i]}) for i in range(len(ids))]

    # 文档分词
    docs_cut = [cut_words(doc) for doc in documents]

    # 创建bm25对象
    bm25 = BM25Okapi(docs_cut)

    # 返回bm25对象和文档内容
    return bm25, docs

def bm25_search(bm25, question, docs, k=10):
    # 问题分词
    question_cut = cut_words(question)

    # 获取得分 -- 数组 -- []
    scores = bm25.get_scores(question_cut)

    # 排序
    sort_scores = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

    # 返回文档内容
    return [docs[i] for i in sort_scores]



if __name__ == '__main__':
    vector_db = LoadChroma.load_chroma_conn()
    build_bm25_index(vector_db)