from common import MySQLUtil

def save_new_dialogue(username, question, answer, parent_id):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    try:
        sql = "insert into history values(null, %s, %s, %s, %s, now());"
        cur.execute(sql, [question, username, parent_id,answer])
        conn.commit()
        return {
            "code": 200,
            "msg": "保存新对话成功",
            "data": cur.lastrowid
        }
    except Exception as e:
        print(f"保存新对话失败：{e}")
        conn.rollback()
        return {
            "code": 500,
            "msg": "保存新对话失败",
            "data": None
        }
    finally:
        # print("关闭数据库连接")
        MySQLUtil.close_mysql_conn(cur, conn)


