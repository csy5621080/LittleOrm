import pymysql
from contextlib import contextmanager
import traceback


def get_connection(host='127.0.0.1', port=3306, user='root', password='123', database='orm_test'):
    connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset='utf8')
    return connection


@contextmanager
def cursor():
    con = get_connection()
    cursor = con.cursor()
    try:
        yield cursor
        con.commit()
    except Exception as e:
        con.rollback()
        traceback.print_exc()
        raise e
    finally:
        con.close()