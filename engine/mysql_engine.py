import pymysql
from contextlib import contextmanager


def get_connection(host='10.0.21.142', port=3306, user='root', password='123456', database='xiaochengplay'):
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
        raise e
    finally:
        con.close()