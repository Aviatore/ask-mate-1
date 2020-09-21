import psycopg2 as ps
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import os


class DB:
    def __init__(self):
        self.host = os.environ.get('DATABASE_HOST')
        self.username = os.environ.get('DATABASE_USERNAME')
        self.password = os.environ.get('DATABASE_PASSWORD')
        self.port = os.environ.get('DATABASE_PORT')
        self.name = os.environ.get('DATABASE_NAME')

    def execute_query(self, query):
        try:
            with ps.connect(
                        host=self.host,
                        user=self.username,
                        password=self.password,
                        port=self.port,
                        dbname=self.name
                    ) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as curs:
                    curs.execute(query)

                    return curs.fetchall()
        finally:
            conn.close()



    # def __query(self, mode, data=None):
    #     self.connect()
    #     records = None
    #     error = None
    #
    #     with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
    #         if mode == 'add':
    #             try:
    #                 cur.execute(sql.SQL('''
    #                 insert into stories (title, story, criteria, b_value, estimation, status)
    #                 values (%(title)s, %(story)s, %(criteria)s, %(b_value)s, %(estimation)s, %(status)s)'''), data)
    #
    #                 error = 'You story was added successfully.'
    #             except Exception as e:
    #                 error = f'Something went wrong: {e}'
    #         elif mode == 'get':
    #             try:
    #                 cur.execute(sql.SQL('select * from stories'))
    #                 records = cur.fetchall()
    #                 error = ''
    #             except Exception as e:
    #                 error = f'Something went wrong: {e}'
    #         elif mode == 'edit':
    #             try:
    #                 cur.execute(sql.SQL('update stories set title=%(title)s, story=%(story)s, criteria=%(criteria)s, b_value=%(b_value)s, estimation=%(estimation)s, status=%(status)s where id=%(id)s'), data)
    #
    #                 error = ''
    #             except Exception as e:
    #                 error = f'Something went wrong: {e}'
    #
    #
    #
    #     if mode in ['add', 'edit']:
    #         return error, ''
    #     elif mode == 'get':
    #         return error, records
