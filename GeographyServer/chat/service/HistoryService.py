from fastapi import HTTPException

from chat.dao import HistoryDao


# 获取历史记录
def get_history(username):
    result = HistoryDao.get_history(username)
    history_list = []
    for i in result:
        # 添加进去的内容为字典格式
        history_list.append({
            "historyId": i['history_id'],
            "question": i['question'],
            "createTime": i['create_time'].strftime("%Y-%m-%d %H:%M:%S"),
            'parentId': i['parent_id']
        })
    # print(f"历史记录列表：{history_list}")
    # print(type(history_list[0]))
    return {
        "code": 200,
        "msg": "获取历史记录成功",
        "data": history_list
    }

# 获取历史对话详情
def history_dialogue(historyId,username):
    result = HistoryDao.history_dialogue(historyId)
    # print(f"历史对话详情：{result}")
    print(result)
    print(result[0]['username'])
    if result[0]['username'] != username:
        raise HTTPException(status_code=403, detail="无权访问该对话详情")
    message = []
    for i in result:
        message.append({
            'role':'user',
            'content':i['question']
        })
        message.append({
            'role':'system',
            'content':i['answer']
        })
    return {
        "code": 200,
        "msg": "获取历史对话详情成功",
        "data": message
    }

# 删除历史记录
def delete_History(historyId,username):
    result = HistoryDao.delete_History(historyId,username)
    return result

# 模糊搜索
def fuzzy_search(username, searchInput):
    result = HistoryDao.fuzzy_search(username, searchInput)
    history_list = []
    for i in result:
        history_list.append({
            "historyId": i['history_id'],
            "question": i['question'],
            "answer": i['answer'],
            "createTime": i['create_time'].strftime("%Y-%m-%d %H:%M:%S"),
            'parentId': i['parent_id']
        })
    return {
        'code': 200,
        'msg': '模糊搜索成功',
        'data': history_list
    }

# if __name__ == '__main__':
    # get_history("clover")
    # history_dialogue(6)



