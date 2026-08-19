import os
import random
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

from common import RedisUtil
from users.dao import UsersDao
from users.utils import PasswordHashUtil, JWTTokenUtil

load_dotenv()

""" ===== 发送邮件 ===== """
# 验证用户是否存在
def check_user(username, email):
    # isinstance(a,b)：返回布尔，判断a是不是b类型（b的实例）
    flag = False
    result = UsersDao.check_user(username, email)
    if isinstance(result, dict):
        flag = True
        print(f"用户是否存在：{flag}")
        return flag, result
    else:
        print(f"用户是否存在：{flag}")
        return flag, None

# 生成验证码
def create_captcha():
    captcha = ""
    for i in range(4):
        captcha += str(random.randint(0, 9))
    return captcha

# 生成邮件信息
def email_message(sql_email, captcha):
    # 配置发送信息：发件方、授权码（从.env文件读取）、主题、邮件内容
    sender = os.getenv("SENDER_EMAIL")
    # sender_pwd = os.getenv("SENDER_EMAIL_PASSWORD")
    subject = "主题为：发送验证码"
    content = f"验证码为：{captcha},请在5分钟内使用"

    # 创建邮件对象 -- 将要发送的信息写在这个对象里面
    message = MIMEText(content, "plain", "utf-8")
    # print(f"创建的邮件对象为：\n{message}")

    # 添加内容在 message对象中
    message["From"] = sender  # 发件人
    message["To"] = sql_email  # 收件人
    message["Subject"] = subject  # 主题
    # print(f"添加内容后的邮件对象为：\n{message}")
    return message

# 将验证码存储到redis中
def save_captcha_to_redis(sql_id, captcha):
    try:
        conn = RedisUtil.get_redis_conn()
        conn.delete(sql_id)  # 清除可能存在的旧验证码
        conn.setex(sql_id, 300, captcha)
        RedisUtil.close_redis_conn(conn)
        return {
            "code": 200,
            "msg": "验证码存储到redis中成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "msg": f"验证码存储到redis中失败：{e}"
        }

# 发送验证码邮件
def captcha_email(captcha_email_entity):
    print("这里是发送邮件 -- UsersService")
    # 取出用户信息
    username = captcha_email_entity.username
    email = captcha_email_entity.email
    password = captcha_email_entity.password
    # print(f"用户信息：{username}, {email}, {password}")

    # 验证用户是否存在
    flag,result = check_user(username, email)
    print(f"验证用户是否存在结果：{flag}\n查询数据库返回信息：{result}")

    # 如果用户不存在，则返回结果
    if not flag:
        return {
            "code": 500,
            "msg": f"用户{username}不存在"
        }

    # 提取信息
    sql_id = result.get("id")
    sql_email = result.get("email")
    sql_password = result.get("password")

    # 如果用户存在，则进行以下操作

    # 判断密码是否正确
    result = PasswordHashUtil.verify_password(password, sql_password)
    print(f"判断密码是否正确结果：{result}")

    # 密码不正确
    if not result:
        return {
            "code": 500,
            "msg": f"密码不正确"
        }

    # 生成验证码
    captcha = create_captcha()
    print(f"验证码：{captcha}")

    # 将验证码存储到redis中
    save_result = save_captcha_to_redis(sql_id, captcha)
    print(f"将验证码存储到redis中结果：{save_result}")
    if save_result.get("code") != 200:
        return save_result

    # 发送邮件
    sender = os.getenv("SENDER_EMAIL")
    sender_pwd = os.getenv("SENDER_EMAIL_PASSWORD")
    print(f"【调试】程序读到的 sender 是: [{sender}]")
    print(f"【调试】程序读到的 email(收件人) 是: [{sql_email}]")
    try:
        # 创建邮件发送服务配置
        smtp = smtplib.SMTP(
            host=os.getenv("SMTP_HOST"),
            port=int(os.getenv("SMTP_PORT"))
        )
        # print(f"创建邮件发送服务配置：{smtp}")

        # 开启邮件发送服务
        smtp.starttls()
        print("开启邮件发送服务")

        # 验证发送方和发送方的授权码是否能对上
        smtp.login(sender, sender_pwd)
        print("验证发送方和发送方的授权码成功")

        # 发送邮件 -- 方法：sendmail(发送方，接收方，邮件对象)
        message = email_message(sql_email, captcha)
        smtp.sendmail(sender, sql_email, message.as_string())
        print(f"发送邮件成功")

        # 关闭邮件发送服务
        smtp.quit()

        # 返回结果
        return {
            "code": 200,
            "msg": f"发送邮件到{email}成功",
            "data": username
        }

    except Exception as e:
        print(f"发送邮件失败：{e}")
        return {
            "code": 500,
            "msg": f"发送邮件失败：{e}"
        }



""" ===== 验证验证码 ===== """
# 从redis中取出验证码
def get_captcha_from_redis(sql_id):
    try:
        conn = RedisUtil.get_redis_conn()
        captcha = conn.get(sql_id)
        RedisUtil.close_redis_conn(conn)
        # print(f"从redis中取出验证码：{captcha}")    # b'1234'
        return captcha.decode('utf-8')
    except Exception as e:
        print(f"从redis中取出验证码失败：{e}")
        return {
            "code": 500,
            "msg": f"从redis中取出验证码失败：{e}"
        }


# 验证验证码
def verify_captcha(verify_captcha_entity):
    print("这里是验证验证码 -- UsersService")
    # 取出用户信息
    username = verify_captcha_entity.username
    email = verify_captcha_entity.email
    captcha = verify_captcha_entity.captcha
    # print(f"验证验证码--用户信息：{username}, {email}, {password},{captcha}")

    # 获取用户信息
    result = check_user(username, email)[1]
    # print(f"验证验证码，获取用户所有信息：{result}\n信息返回类型{type(result)}")
    sql_id = result.get("id")
    sql_username = result.get("name")


    # 从redis中取出验证码
    redis_captcha = get_captcha_from_redis(sql_id)
    print(f"从redis中取出验证码：{redis_captcha}")  # 1234

    # 验证码不存在
    if redis_captcha is None:
        print("验证码已过期")
        return {
            "code": 500,
            "msg": "验证码已过期"
        }
    # 验证码存在，但不一致
    if redis_captcha != captcha:
        print("验证码不一致")
        return {
            "code": 500,
            "msg": "验证码不一致"
        }
    # 验证码存在且一致
    print("验证码验证成功")

    # 生成 token
    payload = {"id": sql_id}
    jwt_result = JWTTokenUtil.save_token_to_redis(payload)
    if jwt_result.get("code") != 200:
        return jwt_result
    token = jwt_result.get("data")
    print(f"生成 token 成功：{token}")

    return {
        "code": 200,
        "msg": "验证码验证成功",
        "data": {
            "token": token,
            "username": sql_username,
        }
    }


""" ===== 注册账号 ===== """

# 注册账号
def sign_up(sign_up_entity):
    print("这里是注册账号 -- UsersService")
    # 取出用户信息
    username = sign_up_entity.username
    email = sign_up_entity.email
    password = sign_up_entity.password
    print(f"注册账号--用户信息：{username}, {email}, {password}")

    # 验证用户是否存在
    result = UsersDao.verify_user(username, email)
    print(f"验证用户是否存在结果：{result}")

    # 账号存在
    if result is not None:
        print(f"账号{username}或邮箱{email}已存在")
        return {
            "code": 500,
            "msg": "账号已存在"
        }

    # 账号不存在
    try:
        password = PasswordHashUtil.hash_password(password)
        result = UsersDao.add_user(username, email, password)
        print(f"添加用户信息结果：{result}")
        return {
            "code": 200,
            "msg": "注册账号成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "msg": f"注册账号失败：{e}"
        }

""" ===== 删除用户 ===== """
# 从 redis 中删除用户的 token
def delete_token_from_redis(sql_id):
    try:
        conn = RedisUtil.get_redis_conn()
        conn.delete(sql_id)
        RedisUtil.close_redis_conn(conn)
        print(f"删除 token 成功")
        return {
            "code": 200,
            "msg": "删除 token 成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "msg": f"删除 token 失败：{e}"
        }
def delete_user(username,email):
    sel_result = UsersDao.check_user(username, email)
    # print(f"查询到用户信息：{sel_result}")
    sql_id = sel_result.get("id")
    # print(f"要删除的用户id：{sql_id}")
    del_result = UsersDao.delete_user(username)
    print(f"删除用户信息结果：{del_result}")
    delete_token_from_redis(sql_id)
    return {
        "code": 200,
        "msg": "删除用户成功"
    }