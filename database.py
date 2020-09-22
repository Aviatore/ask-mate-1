import psycopg2 as ps
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import os


DATABASE_HOST = "localhost"
DATABASE_NAME = "askmate"
DATABASE_PASSWORD = "wojtek19842041"
DATABASE_PORT = 5432
DATABASE_USERNAME = "wojtek"


class Queries:
    def __init__(self):
        self.read_questions_all = 'SELECT id, title, message, view_number, vote_number, submission_time, image FROM question'
        self.read_questions_by_id = 'SELECT id, title, message, view_number, vote_number, submission_time, image FROM question WHERE id = %(id)s'
        self.write_question_by_id = 'UPDATE question ' \
                                    'SET title=%(title)s, ' \
                                    'message=%(message)s, ' \
                                    'view_number=%(view_number)s, ' \
                                    'vote_number=%(vote_number)s, ' \
                                    'submission_time=%(submission_time)s, ' \
                                    'image=%(image)s WHERE id=%(id)s'
        self.read_answers_by_id = 'SELECT id, question_id, message, vote_number, submission_time, image FROM answer WHERE question_id = %(question_id)s'


class DB:
    def __init__(self):
        self.host = DATABASE_HOST
        self.username = DATABASE_USERNAME
        self.password = DATABASE_PASSWORD
        self.port = DATABASE_PORT
        self.name = DATABASE_NAME

    def execute_query(self, query, params=None):
        try:
            with ps.connect(
                        host=self.host,
                        user=self.username,
                        password=self.password,
                        port=self.port,
                        dbname=self.name
                    ) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as curs:
                    curs.execute(sql.SQL(query), params)

                    try:
                        output = curs.fetchall()
                    except ps.ProgrammingError:
                        output = None

                    return output
        finally:
            conn.close()


db = DB()
queries = Queries()

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
