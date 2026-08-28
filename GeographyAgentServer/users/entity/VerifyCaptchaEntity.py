from pydantic import BaseModel, Field

class VerifyCaptchaEntity(BaseModel):
    email: str = Field(..., description="邮箱")
    captcha: str = Field(..., description="验证码")