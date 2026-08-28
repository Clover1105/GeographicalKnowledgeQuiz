from pydantic import BaseModel, Field

class VerifyPasswordEntity(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")