import os
from dotenv import load_dotenv
from fastapi import HTTPException, status

from common import RedisUtil

load_dotenv()
from datetime import datetime, timezone, timedelta

from jose import jwt, JWSError


# 创建 token
def create_token(payload:dict):
    try:
        # 生成 token
        copy_payload = payload.copy()
        shelf_life = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))  # 保质期
        stop_time = datetime.now(timezone.utc)+timedelta(minutes=shelf_life)    # 到期时间
        copy_payload.update({'exp':stop_time,'iat':datetime.now(timezone.utc)})
        token = jwt.encode(
            claims=copy_payload,
            key=os.getenv('SECURITY_KEY'),
            algorithm=os.getenv('ALGORITHM')
        )
        # 返回 token
        return {
            "code": 200,
            "msg": "token生成成功",
            "data": {
                "token": token,
                "shelf_life": shelf_life
            }
        }
    except Exception as e:
        return {
            "code": 500,
            "msg": f"token生成失败或存储到redis中失败：{e}"
        }

# 将 token 存储到 redis 中
def save_token_to_redis(payload:dict):
    result = create_token(payload)
    if result.get("code") != 200:
        return result
    token = result.get("data").get("token")
    shelf_life = result.get("data").get("shelf_life")
    try:
        # 将 token 存储到 redis 中
        shelf_life = shelf_life * 60
        redis_conn = RedisUtil.get_redis_conn()
        redis_conn.delete(payload['id'])
        redis_conn.setex(payload['id'], shelf_life, token)
        redis_conn.close()
        return {
            "code": 200,
            "msg": "token存储到redis中成功",
            'data': token
        }
    except Exception as e:
        return {
            "code": 500,
            "msg": f"token存储到redis中失败：{e}"
        }

# 验证 token
def verify_token(token):
    try:
        # 验证通过后返回原始的 Payload 数据，字典类型
        payload = jwt.decode(
            token = token,
            key = os.getenv('SECURITY_KEY'),
            algorithms = [os.getenv('ALGORITHM')]
        )
        print(payload)
        print(type(payload))
        return {
            "code": 200,
            "msg": "token验证成功",
            "data": payload
        }
    except JWSError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token错误或已过期，验证失败，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )




if __name__ == '__main__':
    token = save_token_to_redis({'id': '4'})['data']
    print(token)
    print(verify_token(token))