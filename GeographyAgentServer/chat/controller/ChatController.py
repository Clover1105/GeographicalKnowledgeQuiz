from starlette.responses import StreamingResponse
import json
from fastapi import APIRouter, Depends

chat_router = APIRouter()

from chat.service import ChatService
from chat.utils.JWTDecodeUtil import decode_token
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



from chat.entity.saveNewDialogueEntity import saveNewDialogueEntity
@chat_router.post(
    path='/saveNewDialogue',
    summary='存储新对话接口',
)
def save_new_dialogue(save_new_dialogue_entity:saveNewDialogueEntity,now_user = Depends(decode_token)):
    username = now_user.get("name")
    print(f"接收到存储新对话的参数：{save_new_dialogue_entity}")
    return ChatService.save_new_dialogue(save_new_dialogue_entity,username)



if __name__ == '__main__':
    data = saveNewDialogueEntity(
        username='xjj',
        question='你好',
        answer='不好最近好累 ╯︿╰',
        parentId=6
    )
    print(save_new_dialogue(data))