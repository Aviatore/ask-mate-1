import psycopg2 as ps
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import os


# DATABASE_HOST = "localhost"
# DATABASE_NAME = "askmate"
# DATABASE_PASSWORD = ""
# DATABASE_PORT = 5432
# DATABASE_USERNAME = "wojtek"

class Queries:
    def __init__(self):
        self.read_questions_all = 'SELECT id, title, message, view_number, vote_number, submission_time, image FROM question'
        self.read_question_by_id = 'SELECT id, title, message, view_number, vote_number, submission_time, image FROM question WHERE id = %(id)s'
        self.update_question_by_id = 'UPDATE question ' \
                                     'SET title=%(title)s, ' \
                                     'message=%(message)s, ' \
                                     'view_number=%(view_number)s, ' \
                                     'vote_number=%(vote_number)s, ' \
                                     'submission_time=%(submission_time)s, ' \
                                     'image=%(image)s WHERE id=%(id)s'
        self.read_answers_by_question_id = 'SELECT id, question_id, message, vote_number, submission_time, image FROM answer WHERE question_id = %(question_id)s'
        self.update_answer_by_id = 'UPDATE answer ' \
                                   'SET message=%(message)s, ' \
                                   'vote_number=%(vote_number)s, ' \
                                   'submission_time=%(submission_time)s, ' \
                                   'image=%(image)s WHERE id=%(id)s'
        self.add_new_question = 'INSERT INTO question (submission_time, view_number, vote_number, title, message, image) ' \
                                'VALUES(%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s)'
        self.add_new_answer = 'INSERT INTO answer (submission_time, vote_number, question_id, message, image) ' \
                              'VALUES(%(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s, %(image)s)'
        self.get_last_id = 'SELECT id FROM {table} ORDER BY id desc limit 1'
        self.delete_answer_by_id = 'DELETE FROM answer WHERE id = %(id)s'
        self.delete_question_by_id = 'DELETE FROM question WHERE id = %(id)s'
        self.read_answer_by_id = 'SELECT id, question_id, message, vote_number, submission_time, image FROM answer WHERE id = %(id)s'
        self.add_comment_to_question = 'INSERT INTO comment (question_id, message, submission_time, edited_count)' \
                                       'VALUES (%(question_id)s, %(message)s, %(submission_time)s, %(edited_count)s)'
        self.read_comments_by_question_id = 'SELECT * FROM comment WHERE question_id=%(question_id)s'

class DB:
    def __init__(self):
        self.host = os.environ.get("DATABASE_HOST")
        self.username = os.environ.get("DATABASE_USERNAME")
        self.password = os.environ.get("DATABASE_PASSWORD")
        self.port = os.environ.get("DATABASE_PORT")
        self.name = os.environ.get("DATABASE_NAME")

    def execute_query(self, query, params=None, **formats):
        try:
            with ps.connect(
                        host=self.host,
                        user=self.username,
                        password=self.password,
                        port=self.port,
                        dbname=self.name
                    ) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as curs:
                    if formats is None:
                        curs.execute(sql.SQL(query), params)
                    else:
                        # The double star (**) expands the dictionary (returned by the function make_identifier())
                        # as an argument name and value as the value of the argument
                        curs.execute(sql.SQL(query).format(**self.make_identifier(formats)), params)
                    try:
                        output = curs.fetchall()
                    except ps.ProgrammingError:
                        output = None

                    return output
        finally:
            conn.close()

    def make_identifier(self, formats):
        output = {}

        for key in formats:
            output[key] = sql.Identifier(formats[key])
        # print(output)
        return output


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
