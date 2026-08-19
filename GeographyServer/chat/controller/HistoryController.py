from fastapi import APIRouter, Depends

from chat.utils.JWTDecodeUtil import decode_token

history_router = APIRouter()

from chat.service import HistoryService
@history_router.get(
    path='/getHistory',
    summary='历史记录接口',
    description="获取历史记录"
)
def get_history(now_user = Depends(decode_token)):
    username = now_user.get("name")
    print(f"接收到查询历史记录的用户：{username}")
    return HistoryService.get_history(username)


@history_router.get(
    path='/historyDialogue',
    summary='历史对话详情接口',
    description="获取历史对话详情"
)
def history_dialogue(historyId: int,now_user = Depends(decode_token)):
    username = now_user.get("name")
    print(f"接收到查询历史对话详情的id：{historyId}")
    return HistoryService.history_dialogue(historyId,username)

@history_router.delete(
    path='/deleteHistory',
    summary='删除历史记录接口',
)
def delete_History(historyId:int,now_user = Depends(decode_token)):
    username = now_user.get("name")
    print(f"接收到要删除的历史记录的父对话id：{historyId}")
    return HistoryService.delete_History(historyId,username)

@history_router.get(
    path='/fuzzySearch',
    summary='模糊搜索接口',
)
def fuzzy_search(searchInput: str,now_user = Depends(decode_token)):
    username = now_user.get("name")
    print(f"接收到模糊查询的参数：{username, searchInput}")
    return HistoryService.fuzzy_search(username, searchInput)


if __name__ == '__main__':
    # get_history("clover")
    # history_dialogue(6)
    # print(delete_History(12))
    print(fuzzy_search("你"))