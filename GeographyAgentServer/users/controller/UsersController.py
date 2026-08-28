print("这里是：UsersController.py")

from fastapi import APIRouter
users_router = APIRouter()

from users.entity.CaptchaEmailEntity import CaptchaEmailEntity
from users.service import UsersService

# 创建发送验证码邮箱接口
@users_router.post(
    path='/captchaEmail',
    summary='发送验证码邮箱'
)
def captcha_email(captcha_email_entity: CaptchaEmailEntity):
    print(f"接收到用户信息（发送邮件）：{captcha_email_entity}")
    return UsersService.captcha_email(captcha_email_entity)


# 创建验证密码接口
from users.entity.VerifyPasswordEntity import VerifyPasswordEntity
@users_router.post(
    path='/verifyPassword',
    summary='验证密码'
)
def verify_password(verify_password_entity: VerifyPasswordEntity):
    print(f"接收到用户信息（验证密码）：{verify_password_entity}")
    return UsersService.verify_password(verify_password_entity)

# 创建验证验证码接口
from users.entity.VerifyCaptchaEntity import VerifyCaptchaEntity
@users_router.post(
    path='/verifyCaptcha',
    summary='验证验证码'
)
def verify_captcha(verify_captcha_entity: VerifyCaptchaEntity):
    print(f"接收到用户信息（验证验证码）：{verify_captcha_entity}")
    return UsersService.verify_captcha(verify_captcha_entity)


# 创建注册用户的接口
from users.entity.SignUpEntity import SignUpEntity
@users_router.post(
    path='/signup',
    summary='注册用户'
)
def sign_up(sign_up_entity: SignUpEntity):
    print(f"接收到用户信息（注册用户）：{sign_up_entity}")
    return UsersService.sign_up(sign_up_entity)

# 删除用户接口
from fastapi import Depends
from chat.utils.JWTDecodeUtil import decode_token
@users_router.delete(
    path='/deleteUser',
    summary='删除用户'
)
def delete_user(now_user = Depends(decode_token)):
    username = now_user.get("name")
    email = now_user.get("email")
    print(f"接收到用户信息（删除用户）：{username}")
    return UsersService.delete_user(username,email)

# 测试
if __name__ == '__main__':
    print("这里是测试：")
    data = VerifyCaptchaEntity(
        username='clover',
        email='2920242909@qq.com',
        password='256837',
        captcha='1234'
    )
    result = verify_captcha(data)
    print(result)
    # data = SignUpEntity(
    #     username='c',
    #     email='clo',
    #     password='123456'
    # )
    # print(sign_up(data))
