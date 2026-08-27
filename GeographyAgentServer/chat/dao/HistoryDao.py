from common import MySQLUtil

# 获取历史记录 -- 第一条
def get_history(username):
    # 连接数据库
    conn = MySQLUtil.get_mysql_conn()
    # 游标对象
    cur = conn.cursor()
    # sql操作
    sql = "select * from history where username = %s and parent_id = 0;"
    # 执行操作
    cur.execute(sql, [username])
    # 获取结果
    result = cur.fetchall()
    # 关闭连接
    MySQLUtil.close_mysql_conn(cur, conn)
    return result

# 获取历史对话详情 -- 父对话（第一条）与其子对话
def history_dialogue(historyId):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    sql = "select username, question, answer from history where parent_id = %s or history_id = %s;"
    cur.execute(sql, [historyId, historyId])
    result = cur.fetchall()
    MySQLUtil.close_mysql_conn(cur, conn)
    return result

# 删除历史记录
def delete_History(historyId,username):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    try:
        sql = "delete from history where (parent_id = %s or history_id = %s) and username = %s;"
        cur.execute(sql, [historyId, historyId, username])
        conn.commit()
        return {
            "code": 200,
            "msg": f"删除历史记录成功，共删除{cur.rowcount}行",
            "data": None
        }
    except Exception as e:
        print(f"删除历史记录失败：{e}")
        conn.rollback()
        return {
            "code": 500,
            "msg": f"删除历史记录失败：{e}",
            "data": None
        }
    finally:
        # print("关闭数据库连接")
        MySQLUtil.close_mysql_conn(cur, conn)

# 模糊搜索
def fuzzy_search(username, searchInput):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    sql = "select * from history where username = %s and (question like %s or answer like %s);"
    cur.execute(sql, [username, f"%{searchInput}%", f"%{searchInput}%"])
    result = cur.fetchall()
    MySQLUtil.close_mysql_conn(cur, conn)
    return result