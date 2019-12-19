import pymysql
from DBUtils.PooledDB import PooledDB
from contextlib import contextmanager
import traceback

poolDB = PooledDB(creator=pymysql,
                  mincached=10,
                  maxcached=10,
                  maxshared=100,
                  maxconnections=500,
                  blocking=True,
                  maxusage=0,
                  setsession=None,
                  host='127.0.0.1',
                  port=3306,
                  user='root',
                  passwd='123',
                  db='orm_test',
                  use_unicode=False,
                  charset='utf8'
        )


@contextmanager
def connection():
    con = poolDB.connection()
    try:
        yield con
        con.commit()
    except Exception as e:
        con.rollback()
        traceback.print_exc()
        raise e
    finally:
        con.close()