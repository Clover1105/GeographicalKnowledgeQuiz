from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough

from ai import LoadLLM
from ai.LoadChroma import load_chroma_conn
from ai.LoadReranker import load_reranker
from chat.service import HistoryService
from chat.utils import BM25Util, RRFUtil, IntentRecognitionUtil


def chat(question: str, historyId: int, username:str):
    # 判断是否为新对话框
    if historyId == 0:
        history_list = []
    else:
        # 不是新对话，调用查询详细记录函数（包装查询详细历史记录结果函数）
        history_list = HistoryService.history_dialogue(historyId,username)['data']

    # 意图识别，调用意图识别工具，判断是否走RAG检索
    is_geography = IntentRecognitionUtil.intent_recognition(question)["is_geography"]
    print(f"意图识别结果：{is_geography}")

    # 创建LLM对象
    llm = LoadLLM.create_model()

    # 不走RAG检索
    if not is_geography:
        history_list.append({
            "role": "user",
            "content": question
        })
        # 直接调用llm大模型回复
        for chunk in llm.stream(history_list):
            print(f"llm大模型回复：{chunk}")
            if chunk.content:
                yield chunk.content
        return

    # 创建检索器对象（向量数据库连接对象）
    vector = load_chroma_conn()
    # 包装为检索器接口（向量检索）
    v_retriever = vector.as_retriever(search_kwargs={"k": 10})

    # 混合检索
    def rrf():
        # 向量
        v_result = v_retriever.invoke(question)
        zh("向量检索", v_result)
        # BM25
        bm25, docs = BM25Util.build_bm25_index(vector)
        bm_result = BM25Util.bm25_search(bm25, question, docs,10)
        zh("bm25检索", bm_result)
        # rrf
        rrf_result = RRFUtil.rrf(v_result, bm_result)
        zh("rrf检索", rrf_result)     # list[Document(id,metadata,page_content)]
        return rrf_result

    # 打印召回结果
    def zh(t,result):
        print(f"\n{t}到的文档内容：")
        print(result)
        print("*-" * 20)
        for i in result:
            print(i.page_content)
            print("*-" * 20)

    # 重排序
    def re_reranker(data):
        print("\n开始重排：")
        # 创建重排序模型对象
        reranker = load_reranker()
        # 获取检索结果
        cons = data['context']
        # print(f"检索结果：\n{cons}\n")
        # 获取问题
        que = data['question']
        # print(f"问题：\n{que}\n")
        # 获取历史记录
        his = data['history']
        # 问题和召回文档 进行包装 构造reranker输入
        # 因为重排序模型（Reranker / Cross-Encoder）的输入格式就是 (query, document) 这样的"问题-文档对"
        reranker_input = [(que, con.page_content) for con in cons]
        # 调用重排序模型，计算得分
        scores = reranker.compute_score(reranker_input)
        # print(f"重排序后分数：\n{scores}\n")
        # 将文档和分数包装，方便根据分数排序
        con_score = list(zip(cons, scores))
        # 排序
        con_score.sort(key=lambda x: x[1], reverse=True)
        print(f"重排序后文档内容：\n{con_score}\n")
        # 返回排序后的文档
        cons =  [con[0] for con in con_score]

        # 返回结果
        for i,item in enumerate(cons[:10]):
            print(f"【第{i + 1}条】：{item.page_content}")
        print("-*-"*20)
        return {
            "context":cons,
            "history":his,
            "question":que
        }

    # 创建提示词
    template = """
        你是一名知识库问答助手，请结合提供的知识内容回答用户问题。
        回答要求：
            - 仅依据提供的知识内容进行回答，不补充未出现的信息。
            - 若知识内容无法回答问题，请明确说明当前知识不足，避免推测或编造。
            - 对多个知识片段进行综合分析后再作答，避免简单复制原文。
            - 回答应准确、自然、条理清晰，优先直接回答问题，再补充必要说明。
            - 相同信息无需重复描述。
            - 不要提及"根据参考资料"、"根据检索结果"、"根据上下文"等描述。
            - 若未提供任何知识内容或知识为空，请友好告知暂时无法回答，并建议用户补充信息或换个问题。
        历史记录：
            {history}
        知识内容：
            {context}
        用户问题：
            {question}
        回答：
    """

    # 创建提示词对象
    prompt = PromptTemplate(
        template=template,
        input_variables=["history","context", "question"]
    )


    # 自定义问答链
    chain = (
        # 并行执行器
        RunnableParallel(
            {
                "context":RunnableLambda(lambda _:rrf()),
                "history":RunnableLambda(lambda _:history_list),
                "question":RunnablePassthrough()
            }
        )
        | RunnableLambda(re_reranker)
        | prompt
        | llm
        | StrOutputParser()
    )
    for chunk in chain.stream(question):
        if chunk:
            yield chunk



from chat.dao import ChatDao
def save_new_dialogue(save_new_dialogue_entity,username):
    # 取出信息
    question = save_new_dialogue_entity.question
    answer = save_new_dialogue_entity.answer
    parent_id = save_new_dialogue_entity.parentId
    # 保存新对话
    result = ChatDao.save_new_dialogue(username, question, answer, parent_id)
    # 返回结果
    return result


# if __name__ == '__main__':
#     for chunk in chat("中国有哪些省级行政区？", 1):
#         print(chunk)


