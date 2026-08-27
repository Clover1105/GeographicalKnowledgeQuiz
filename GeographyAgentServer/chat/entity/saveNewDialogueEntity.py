from pydantic import BaseModel, Field

class saveNewDialogueEntity(BaseModel):
    question:str = Field(..., description="问题")
    answer:str = Field(..., description="回答")
    parentId:int = Field(..., description="父对话ID")