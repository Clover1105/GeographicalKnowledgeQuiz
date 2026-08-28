import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough

from ai.LoadChroma import load_chroma_conn
from ai.LoadReranker import load_reranker
from chat.utils import BM25Util, RRFUtil
import main

# 创建查询地理知识工具
from langchain.tools import tool
@tool(
    name_or_callable="query_geo",
    description="""
        当用户提出与地理相关的问题时调用此工具，包括但不限于：
        地理位置、地形地貌、气候水文、行政区划、人口民族、
        自然资源、地理历史等。非地理问题请勿调用。
        参数说明：question为用户原始问题；
        username为当前登录用户名。"
    """,
)
def query_geo(question: str):
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
        # print(result)
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
        print(f"重排序前获取所有检索结果：\n{cons}\n")

        # 获取问题
        que = data['question']
        # print(f"问题：\n{que}\n")

        # 问题和召回文档 进行包装 构造reranker输入
        # 因为重排序模型（Reranker / Cross-Encoder）的输入格式就是 (query, document) 这样的"问题-文档对"
        # 重排序输入仍用 page_content（问题）与 query 匹配
        reranker_input = [(que, con.page_content) for con in cons]

        # 调用重排序模型，计算得分
        scores = reranker.compute_score(reranker_input)
        # print(f"重排序后分数：\n{scores}\n")

        # 将文档和分数包装，方便根据分数排序
        con_score = list(zip(cons, scores))

        # 排序
        con_score.sort(key=lambda x: x[1], reverse=True)
        print(f"重排序后文档内容：")
        # print(con_score)
        # 返回排序后的文档（向量数据库中的问题）
        cons =  [con[0] for con in con_score]
        print(cons)

        # 返回给 LLM 的 context 改为从 metadata 中取答案
        cons_with_answer = [con.metadata.get("answer", con.page_content) for con in cons]

        # 返回结果
        for i,item in enumerate(cons[:10]):
            print(f"【第{i + 1}条】\n问题：{item.page_content}")
            print(f"答案：{item.metadata.get('answer', 'N/A')}")
        print("-*-"*20)
        return {
            "context":cons_with_answer,
            "question":que
        }

    # 创建提示词
    template = """
        你是一名地理知识库问答助手，请结合提供的知识内容回答用户问题。
        回答要求：
            - 仅依据提供的知识内容进行回答，不补充未出现的信息。
            - 若知识内容无法回答问题，请明确说明当前知识不足，避免推测或编造。
            - 对多个知识片段进行综合分析后再作答，避免简单复制原文。
            - 回答应准确、自然、条理清晰，优先直接回答问题，再补充必要说明。
            - 相同信息无需重复描述。
            - 不要提及"根据参考资料"、"根据检索结果"、"根据上下文"等描述。
            - 若未提供任何知识内容或知识为空，请友好告知暂时无法回答，并建议用户补充信息或换个问题。
        知识内容：
            {context}
        用户问题：
            {question}
        回答：
    """

    # 创建提示词对象
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )


    # 自定义问答链
    chain = (
        # 并行执行器
        RunnableParallel(
            {
                "context":RunnableLambda(lambda _:rrf()),
                "question":RunnablePassthrough()
            }
        )
        | RunnableLambda(re_reranker)
        | prompt
        | main.llm
        | StrOutputParser()
    )

    # 加重试，应对内容审核的偶发拦截
    last_err = None
    for attempt in range(3):
        try:
            result = chain.invoke(question)
            return result
        except Exception as e:
            last_err = e
            print(f"第{attempt + 1}次调用LLM失败：{e}")
            time.sleep(1)
    # 三次都失败，返回友好提示，而不是让接口崩掉
    return "当前问题暂时无法回答（内容安全校验未通过），请换个问法或稍后再试。"