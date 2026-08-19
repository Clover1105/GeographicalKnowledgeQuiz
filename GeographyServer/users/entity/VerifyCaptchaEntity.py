from pydantic import BaseModel, Field

class VerifyCaptchaEntity(BaseModel):
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    password: str = Field(..., description="密码")
    captcha: str = Field(..., description="验证码")