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
        self.read_questions_all_desc = 'SELECT id, title, message, view_number, vote_number, submission_time, image FROM question ORDER BY {order_by} DESC'
        self.read_questions_all_asc = 'SELECT id, title, message, view_number, vote_number, submission_time, image FROM question ORDER BY {order_by} ASC'
        self.read_question_by_id = 'SELECT id, title, message, view_number, vote_number, submission_time, image FROM question WHERE id = %(id)s'
        self.read_answer_by_id = 'SELECT id, title, message, view_number, vote_number, submission_time, image FROM answer WHERE id = %(id)s'
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
        self.search_question = """SELECT q.id, q.title, q.message, q.view_number, q.vote_number, q.submission_time, q.image 
                FROM question as q
                LEFT JOIN answer as a ON (q.id = a.question_id)
                WHERE q.title ~* %(query)s OR q.message ~* %(query)s OR a.message ~* %(query)s"""
        self.search_answer = """SELECT id, question_id, message, vote_number, submission_time, image
                FROM answer
                WHERE message ~* %(query)s"""

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

        return output


db = DB()
queries = Queries()
