import main
from langchain_core.messages import AIMessageChunk
from chat.service import HistoryService
from chat.utils import OptimizationProblemUtil,ContextCompressionUtil

def chat(question: str,historyId:int,username:str):
    # 判断是否为新对话框
    if historyId == 0:
        history_list = []
    else:
        # 不是新对话，调用查询详细记录函数（包装查询详细历史记录结果函数）
        history_list = HistoryService.history_dialogue(historyId, username)['data']
    print(f"历史记录：\n{history_list}")

    # 多轮对话
    # 工具里面已经将数据处理好了，问题和回答已经分开了，可以直接用
    messages = history_list

    # 上下文压缩处理
    if len(messages) > 12:
        messages = ContextCompressionUtil.compress_context(history_list,main.llm)
        print(f"压缩后消息：\n{messages}")

    # 优化用户问题
    print(f"原始问题: {question}")
    question = OptimizationProblemUtil.optimize_problem(question,history_list,main.llm)
    print(f"重写后问题: {question}")

    # 将【重写后的问题】追加到消息列表中
    messages.append({'role':'user','content':question})

    # 调用智能体工具
    print("调用智能体工具")

    for chunk,metadata in main.agent.stream({"messages":messages},stream_mode='messages'):
        # print(type(chunk))  # <class 'langchain_core.messages.ai.AIMessageChunk'>

        # 筛选有效数据
        if not isinstance(chunk,AIMessageChunk):    # 不是AIMessageChunk类型，跳过
            continue
        if getattr(chunk,'tool_call_chunks',None):   # tool_call_chunks属性有值，跳过
            continue
        if chunk.content:   # content属性有值，返回结果
            # print(f"-*--*-chunk-*--*-:{chunk}")
            yield chunk.content




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


if __name__ == '__main__':
    from ai import LoadLLM
    llm = LoadLLM.create_model()
    from chat.utils import AgentUtil
    agent = AgentUtil.agent_util(llm)
    re = chat("重庆今天的天气如何?",31,"clover")
    print(re)




