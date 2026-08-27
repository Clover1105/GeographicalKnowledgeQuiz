from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from users.dao import UsersDao
from users.utils import JWTTokenUtil

# 创建从请求头获取 token 的对象工具
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/verifyCaptcha")

# 解码 token
def decode_token(token: str = Depends(oauth2_scheme)):
    # 只有验证通过才能继续往下执行代码
    result = JWTTokenUtil.verify_token(token)
    user_id = result.get("data").get("id")
    if user_id is None:
        raise  HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="获取用户失败，无法验证凭据，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_user = UsersDao.token_user(user_id)
    print(token_user)
    return token_user

if __name__ == '__main__':
    token = JWTTokenUtil.save_token_to_redis({'id': '4'})['data']
    # token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IjI5MjAyNDI5MDlAcXEuY29tIiwiZXhwIjoxNzg2ODcwODIzLCJpYXQiOjE3ODY4NjkwMjN9.3nS7vOBOEyGxWN1tKVGnQtf6B29dE6S9H-ihGhidTJ4'
    print(token)
    decode_token(token)