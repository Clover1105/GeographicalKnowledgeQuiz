# 一、嵌入智能体（agent）实现数据分流

### 启动项目执行

```python
# 启动和关闭要执行的操作
from contextlib import asynccontextmanager
from ai import LoadLLM
from chat.utils import AgentUtil
llm = None
agent = None
@asynccontextmanager
async def start_and_stop(app):
    global llm, agent
    app.state.username = "clover"
    print("启动项目")
    print("正在初始化大模型...")
    llm = LoadLLM.create_model()
    print("正在初始化智能体...")
    agent = AgentUtil.agent_util(llm)
    yield
    print("关闭项目")
```

### 创建智能体

`AgentUtil.py`

```python
# 调用工具
from chat.utils import MedicalCypherTool,WeatherTool,ChromadbTool

# 创建智能体对象
from langchain.agents import create_agent

def agent_util(llm):
    return create_agent(
        model=llm,
        system_prompt="""你是一个智能助手，能够根据用户问题选择合适的处理方式。
    
            ## 工具使用规则
            1. **天气查询**：当用户询问天气相关信息（如"今天北京天气怎么样"、"明天会下雨吗"）时，必须调用 `get_weather` 工具获取实时数据，不要自行编造天气信息。
            2. **医疗信息查询**：当用户询问医疗、健康、疾病、药品、症状、医院等相关信息时，必须调用 `execute_cypher` 工具从知识库中检索，不要凭记忆回答医疗问题。
            3. **地理知识查询**：当用户询问地理位置、城市、国家、地形、河流、行政区划等地理相关信息时，必须调用 `query_geo` 工具从知识库中检索，不要凭记忆回答地理问题。
            4. **其他问题**：对于不属于上述三类的普通问题（如闲聊、常识、写作、翻译等），直接生成回复，不要调用任何工具。
    
            ## 注意事项
            - 每次只选择最匹配的一个工具，不要同时调用多个工具。
            - 如果用户的问题模糊，无法判断是否需要工具，优先直接回复并引导用户澄清。
            - 工具返回的结果需要你用自然语言整理后回复给用户，不要直接输出原始数据。
            - 调用工具时，请把用户的指代/省略补全为独立完整的问题再传入 question 参数。
            """,
        # 工具列表
        tools=[MedicalCypherTool.execute_cypher, WeatherTool.get_weather, ChromadbTool.query_geo],
        # 打印信息
        debug=True,
    )
```

### 连接图数据库

```python
from langchain_neo4j import Neo4jGraph

def get_neo4j_conn():
    return Neo4jGraph(
        url="bolt://127.0.0.1:7687",
        username="neo4j",
        password="12345678",
        database="neo4j"
    )

if __name__ == '__main__':
    conn = get_neo4j_conn()
    print(f"连接成功：{conn}")
```

### 工具 -- 医疗CQL命令

`MedicalCypherTool.py`

```python
# medical 医疗

# 连接图数据库
from common import Neo4jUtil
conn = Neo4jUtil.get_neo4j_conn()

# 参数校验
from pydantic import BaseModel, Field
class CypherTool(BaseModel):
    cypher: str = Field(..., description="Cypher语句")


# 创建执行cql命令的工具
from langchain_core.tools import tool
@tool(
    name_or_callable="execute_cypher",
    description="""
        Task:Generate Cypher statement to query a graph database.
        Instructions:
        Use only the provided relationship types and properties in the schema.
        Do not use any other relationship types or properties that are not provided.
        数据库的信息定义如下：
        # 节点标签及含义
        | 节点标签     | 含义             |
        |--------------|------------------|
        | Disease      | 疾病（核心节点） |
        | Symptom      | 症状             |
        | Check        | 检查项目         |
        | Cureway      | 治疗方式         |
        | Drug         | 药物             |
        | Department   | 就诊科室         |
        | Food         | 食物             |
        | Dishes       | 菜肴             |
        | Category     | 疾病分类         |

        # 关系类型及含义
        | 关系类型             | 含义              | 起始节点 | 目标节点    |
        |----------------------|-------------------|----------|-------------|
        | DISEASE_SYMPTOM      | 疾病症状          | Disease  | Symptom     |
        | DISEASE_CHECK        | 相关检查项目      | Disease  | Check       |
        | DISEASE_CUREWAY      | 治疗方式          | Disease  | Cureway     |
        | DISEASE_DRUG         | 治疗或相关药物    | Disease  | Drug        |
        | DISEASE_DEPARTMENT   | 就诊科室          | Disease  | Department  |
        | DISEASE_DO_EAT       | 推荐进食的食物    | Disease  | Food        |
        | DISEASE_NOT_EAT      | 不推荐进食的食物  | Disease  | Food        |
        | DISEASE_DISHES       | 适合疾病的菜肴    | Disease  | Dishes      |
        | DISEASE_ACOMPANY     | 并发症 / 伴随疾病 | Disease  | Disease     |
        | DISEASE_CATEGORY     | 疾病所属类别      | Disease  | Category    |

        # 查询示例
        # 问：高血压有哪些症状？
        MATCH (d:Disease {{name:"高血压"}})-[:DISEASE_SYMPTOM]->(s:Symptom) RETURN s.name AS symptom

        # 问：感冒吃什么药？
        MATCH (d:Disease {{name:"感冒"}})-[:DISEASE_DRUG]->(dr:Drug) RETURN dr.name AS drug

        # 问：糖尿病不宜吃什么？
        MATCH (d:Disease {{name:"糖尿病"}})-[:DISEASE_NOT_EAT]->(f:Food) RETURN f.name AS food

        # 问：肺炎需要做什么检查？
        MATCH (d:Disease {{name:"肺炎"}})-[:DISEASE_CHECK]->(c:Check) RETURN c.name AS check_item

        # 问：高血压挂什么科？
        MATCH (d:Disease {{name:"高血压"}})-[:DISEASE_DEPARTMENT]->(dep:Department) RETURN dep.name AS department

        # 问：感冒的并发症有哪些？
        MATCH (d:Disease {{name:"感冒"}})-[:DISEASE_ACOMPANY]->(a:Disease) RETURN a.name AS complication

        # 问：糖尿病属于哪类疾病？
        MATCH (d:Disease {{name:"糖尿病"}})-[:DISEASE_CATEGORY]->(c:Category) RETURN c.name AS category

        # 问：高血压可以吃什么菜？
        MATCH (d:Disease {{name:"高血压"}})-[:DISEASE_DISHES]->(dishes:Dishes) RETURN dishes.name AS dishes

        # 问：哪些疾病会有头痛症状？
        MATCH (d:Disease)-[:DISEASE_SYMPTOM]->(s:Symptom {{name:"头痛"}}) RETURN d.name AS disease

        Note: Do not include any explanations or apologies in your responses.
        Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
        Do not include any text except the generated Cypher statement.

        参数：
            cql: 查询命令
    """,
)
def execute_cypher(cql: str) -> dict:
    result = conn.query(cql)
    print(f"执行cql命令结果：\n{result}")
    return {"result": result}
```

### 工具 -- 天气查询

`WeatherTool.py`

```python
# 连接图数据库
from common import Neo4jUtil
conn = Neo4jUtil.get_neo4j_conn()

# 参数校验
from pydantic import BaseModel, Field
class WeatherTool(BaseModel):
    city: str = Field(..., description="城市名称")

# 创建工具
from langchain_core.tools import tool

# 创建查询天气的工具
import requests
@tool(
    name_or_callable="get_weather",
    description="""
        当用户需要查询某个城市的天气时，调用此工具
        参数：
            city：字符串类型，表示城市名称
    """
)
def get_weather(city: str):
    print(f"查询天气的城市：{city}")
    # 引入天气查询接口 --- 第三方api【高德、心知】
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": "be2c23df0824437362ed4948ecfb50d9",
        "city": city,
    }
    # 通过requests发送get请求
    result = requests.get(url=url, params=params)
    result = result.json()
    # 拼接天气数据
    live = result["lives"][0]
    return {
        "result": (
            f"{live['province']}{live['city']}当前天气{live['weather']}，"
            f"气温{live['temperature_float']}℃，湿度{live['humidity_float']}%，"
            f"{live['winddirection']}风{live['windpower']}级，"
            f"数据更新时间为{live['reporttime']}。"
        )
    }
```

### 工具 -- 地理知识RAG

`ChromadbTool.py`

```
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
        # for i in result:
        #     print(i.page_content)
        #     print("*-" * 20)

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
        print(f"重排序后文档内容：")
        # print(con_score)
        # 返回排序后的文档
        cons =  [con[0] for con in con_score]

        # 返回结果
        for i,item in enumerate(cons[:10]):
            print(f"【第{i + 1}条】：{item.page_content}")
        print("-*-"*20)
        return {
            "context":cons,
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
```

### 聊天接口

`ChatController.py`

```
@chat_router.get(
    path='/chat',
    summary='聊天接口',
    description="SSE流式输出"
)
def chat(question:str,historyId:int,now_user = Depends(decode_token)):
    username = now_user.get("name")
    print(f"这里是chat接口\n接收到问题和id：{question},{historyId}")
    def generator():
        for item in ChatService.chat(question,historyId,username):
            yield f"data:{json.dumps({'content': item}, ensure_ascii=False)}\n\n"
        yield f"data:{json.dumps({'content': 'end_end'})}\n\n"
    return StreamingResponse(
        generator(),
        media_type="text/event-stream"
    )
```

### 调用智能体分流：

`ChatService.py`

```
import main
from langchain_core.messages import AIMessageChunk
from chat.service import HistoryService

def chat(question: str,historyId:int,username:str):
    # 判断是否为新对话框
    if historyId == 0:
        history_list = []
    else:
        # 不是新对话，调用查询详细记录函数（包装查询详细历史记录结果函数）
        history_list = HistoryService.history_dialogue(historyId, username)['data'][-6:]
    print(f"历史记录\n：{history_list}")

    # 多轮对话
    message = []
    for i in history_list:
        message.append({'role':'user','content':i.get('question')})
        message.append({'role':'system','content':i.get('answer')})
    message.append({'role':'user','content':question})

    # 调用智能体工具
    print("调用智能体工具")

    for chunk,metadata in main.agent.stream({"messages":message},stream_mode='messages'):
        # print(type(chunk))  # <class 'langchain_core.messages.ai.AIMessageChunk'>

        # 筛选有效数据
        if not isinstance(chunk,AIMessageChunk):    # 不是AIMessageChunk类型，跳过
            continue
        if getattr(chunk,'tool_call_chunks',None):   # tool_call_chunks属性有值，跳过
            continue
        if chunk.content:   # content属性有值，返回结果
            # print(f"-*--*-chunk-*--*-:{chunk}")
            yield chunk.content
```
