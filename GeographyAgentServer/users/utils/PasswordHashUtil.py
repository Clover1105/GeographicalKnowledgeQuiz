from passlib.context import CryptContext

# 创建密码哈希上下文对象
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 加密
def hash_password(password):
    hash_pwd = bcrypt_context.hash(password)
    return hash_pwd

# 验证
def verify_password(password, hash_pwd):
    ver_result = bcrypt_context.verify(password, hash_pwd)
    return ver_result