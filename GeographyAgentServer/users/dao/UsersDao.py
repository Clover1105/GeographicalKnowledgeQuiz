from common import MySQLUtil

def check_user(username, email):
    # 创建连接对象
    conn = MySQLUtil.get_mysql_conn()
    # 创建游标对象，执行数据库相关操作
    cur = conn.cursor()
    # MySQL操作
    if email:
        sql = "select * from users where email = %s;"
        # 执行操作
        cur.execute(sql, email)
    if username:
        sql = "select * from users where name = %s;"
        # 执行操作
        cur.execute(sql, username)
    # 获取结果
    result = cur.fetchone()
    # print(f"查询用户信息结果：{type(result)}")
    # 关闭连接
    MySQLUtil.close_mysql_conn(cur, conn)
    return result

def verify_user(username, email):
    # 创建连接对象
    conn = MySQLUtil.get_mysql_conn()
    # 创建游标对象，执行数据库相关操作
    cur = conn.cursor()
    # MySQL操作
    sql = "select * from users where name = %s or email = %s;"
    # 执行操作
    cur.execute(sql,[username, email])
    # 获取结果
    result = cur.fetchone()
    print(f"数据库查询用户信息结果（注册）：{result}")
    # 关闭连接
    MySQLUtil.close_mysql_conn(cur, conn)
    return result

def add_user(username, email, password):
    # 创建连接对象
    conn = MySQLUtil.get_mysql_conn()
    # 创建游标对象，执行数据库相关操作
    cur = conn.cursor()
    try:
        # MySQL操作
        sql = "insert into users values(null, %s, %s, %s, now());"
        # 执行操作
        cur.execute(sql,[username, email, password])
        # 提交事务
        conn.commit()
        return {
            "code": 200,
            "msg": "数据库添加用户信息成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "msg": f"数据库添加用户信息失败：{e}"
        }
    finally:
        # 关闭连接
        MySQLUtil.close_mysql_conn(cur, conn)

def token_user(user_id):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    sql = "select * from users where id = %s;"
    cur.execute(sql,[user_id])
    result = cur.fetchone()
    print(f"数据库查询用户信息结果（token）：{result}")
    MySQLUtil.close_mysql_conn(cur, conn)
    return result

def delete_user(username):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    try:
        sql = "delete from users where name = %s;"
        cur.execute(sql,[username])
        conn.commit()
        return {
            "code": 200,
            "msg": f"数据库删除用户信息成功，共删除{cur.rowcount}个用户"
        }
    except Exception as e:
        conn.rollback()
        return {
            "code": 500,
            "msg": f"数据库删除用户信息失败：{e}"
        }
    finally:
        MySQLUtil.close_mysql_conn(cur, conn)

if __name__ == '__main__':
    print(check_user("clover", "2920242909@qq.com"))
    # # {'id': 1, 'name': 'clover', 'email': 'clover@qq.com', 'password': '123456', 'create_time': datetime.datetime(2026, 8, 12, 15, 38, 22)}
    # print(add_user("song", "s@qq.com", "78910"))


