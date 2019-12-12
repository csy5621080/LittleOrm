import pymysql
from DBUtils.PersistentDB import PersistentDB
from contextlib import contextmanager
import traceback

db_config = dict(host='127.0.0.1', port=3306, user='root', password='123', database='orm_test')

poolDB = PersistentDB(
            creator=pymysql,
            maxusage=1000,
            **db_config
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