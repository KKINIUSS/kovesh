import sqlite3
import datetime
import random
from time import sleep

if __name__ == '__main__':
    conn = sqlite3.connect("kovesh.db")
    cur = conn.cursor()
    sql = ""
    for i in range(0, 377):
        sql += str(random.randint(0, 1)) + ", "
        if i == 376:
            sql +=  str(datetime.datetime.now().second)
        else:
            sql += str(datetime.datetime.now().second) + ", "
        sleep(0.01)

    print(sql)
    sql_q = f"insert into test values ('2', '1', '22/12/2021', {sql})"
    cur.execute(sql_q)
    conn.commit()
    conn.close()