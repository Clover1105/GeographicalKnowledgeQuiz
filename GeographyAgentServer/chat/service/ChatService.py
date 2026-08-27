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




