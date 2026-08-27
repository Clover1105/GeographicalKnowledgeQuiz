import pymysql
import os

# 获取连接
def get_mysql_conn():
    return pymysql.connect(
        # IP地址
        host=os.getenv("MYSQL_HOST"),
        # 端口号 -- 类型为 int
        # os.getenv("MYSQL_PORT") -- 类型为 str，需要转换为 int
        port=int(os.getenv("MYSQL_PORT")),
        # 数据库账户
        user=os.getenv("MYSQL_USER"),
        # 数据库账户对应的密码
        password=os.getenv("MYSQL_PASSWORD"),
        # 数据库名称
        database=os.getenv("MYSQL_DATABASE"),
        # 字符集
        charset=os.getenv("MYSQL_CHARSET"),
        # 以 dict 的方式返回查询结果
        cursorclass=pymysql.cursors.DictCursor
    )

# 关闭连接
def close_mysql_conn(cursor,conn):
    cursor.close()
    conn.close()