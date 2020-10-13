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
        self.read_question_by_id = 'SELECT q.id, q.title, q.message, q.view_number, q.vote_number, q.submission_time, q.image, q.users_id_that_vote, u.user_id, u.username ' \
                                   'FROM question as q ' \
                                   'INNER JOIN users as u USING (user_id) '\
                                   'WHERE q.id = %(id)s'
        self.update_question_by_id = 'UPDATE question ' \
                                     'SET title=%(title)s, ' \
                                     'message=%(message)s, ' \
                                     'view_number=%(view_number)s, ' \
                                     'vote_number=%(vote_number)s, ' \
                                     'submission_time=%(submission_time)s, ' \
                                     'image=%(image)s, ' \
                                     'users_id_that_vote=%(users_id_that_vote)s WHERE id=%(id)s'
        self.read_answers_by_question_id = 'SELECT a.id, a.question_id, a.message, a.vote_number, a.submission_time, a.image, a.user_id, a.users_id_that_vote, u.user_id, u.username ' \
                                           'FROM answer as a ' \
                                           'INNER JOIN users as u USING (user_ID) ' \
                                           'WHERE a.question_id = %(question_id)s ' \
                                           'ORDER BY a.submission_time'
        self.update_answer_by_id = 'UPDATE answer ' \
                                   'SET message=%(message)s, ' \
                                   'vote_number=%(vote_number)s, ' \
                                   'submission_time=%(submission_time)s, ' \
                                   'users_id_that_vote=%(users_id_that_vote)s, ' \
                                   'image=%(image)s WHERE id=%(id)s'
        self.add_new_question = 'INSERT INTO question (submission_time, view_number, vote_number, title, message, image, user_id) ' \
                                'VALUES(%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s, %(user_id)s)'
        self.add_new_answer = 'INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id) ' \
                              'VALUES(%(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s, %(image)s, %(user_id)s)'
        self.get_last_id = 'SELECT id FROM {table} ORDER BY id desc limit 1'
        self.delete_answer_by_id = 'DELETE FROM answer WHERE id = %(id)s'
        self.delete_question_by_id = 'DELETE FROM question WHERE id = %(id)s'
        self.read_answer_by_id = 'SELECT id, question_id, message, vote_number, submission_time, image FROM answer WHERE id = %(id)s'
        self.add_comment_to_question = 'INSERT INTO comment (question_id, message, submission_time, edited_count)' \
                                       'VALUES (%(question_id)s, %(message)s, %(submission_time)s, %(edited_count)s)'
        self.read_comments_by_question_id = 'SELECT * FROM comment WHERE question_id=%(question_id)s'
        self.add_comment_to_answer = 'INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count)' \
                                     'VALUES (%(question_id)s, %(answer_id)s, %(message)s, %(submission_time)s, %(edited_count)s)'
        self.read_comments_by_answer_id = 'SELECT * FROM comment WHERE answer_id=%(answer_id)s'

        self.read_tag_id_by_question_id = 'SELECT tag_id FROM question_tag WHERE question_id=%(question_id)s'
        self.read_tag_by_id = 'SELECT name FROM tag WHERE id=%(tag_id)s'
        self.read_tag_id_by_name = 'SELECT id FROM tag WHERE name=%(name)s'
        self.read_all_tags = 'SELECT name FROM tag'
        self.add_new_tag = 'INSERT INTO tag (name) VALUES (%(name)s)'
        self.link_tag_question = 'INSERT INTO question_tag (question_id, tag_id) VALUES (%(question_id)s, %(tag_id)s)'
        self.read_tag_id_by_question_id = 'SELECT tag_id FROM question_tag WHERE question_id=%(question_id)s'
        self.delete_question_tag_links_by_question_id = 'DELETE FROM question_tag WHERE question_id=%(question_id)s'
        self.delete_question_tag_links_by_tag_id_question_id = 'DELETE FROM question_tag WHERE tag_id=%(tag_id)s and question_id=%(question_id)s'

        self.search_question = """SELECT DISTINCT q.id, q.title, q.message, q.view_number, q.vote_number, q.submission_time, q.image 
                FROM question as q
                LEFT JOIN answer as a ON (q.id = a.question_id)
                WHERE q.title ~* %(query)s OR q.message ~* %(query)s OR a.message ~* %(query)s"""
        self.search_answer = """SELECT id, question_id, message, vote_number, submission_time, image
                FROM answer
                WHERE message ~* %(query)s"""

        self.read_answer_by_id = 'SELECT id, question_id, message, vote_number, submission_time, image, users_id_that_vote FROM answer WHERE id = %(id)s'
        self.get_user_by_username = 'SELECT user_id, username, email, password, registration_date, reputation ' \
                                    'FROM users WHERE username = %(username)s'
        self.get_user_by_user_id = 'SELECT user_id, username, email, registration_date, reputation ' \
                                   'FROM users WHERE user_id = %(user_id)s'
        self.get_all_users = 'SELECT user_id, username, registration_date, reputation ' \
                             'FROM users'
        self.add_new_user = 'INSERT INTO users (username, email, password)' \
                            'VALUES (%(username)s, %(email)s, %(password)s)'
        self.get_all_questions_by_user_id = 'SELECT id, title, message, view_number, vote_number, submission_time, image, user_id ' \
                                            'FROM question ' \
                                            'WHERE user_id = %(user_id)s'
        self.get_all_answers_by_user_id = 'SELECT a.id, a.question_id, a.message, a.vote_number, a.submission_time, a.image, a.user_id, q.title as "question_title" ' \
                                           'FROM answer as a ' \
                                          'INNER JOIN question as q ON(q.id = a.question_id)' \
                                           'WHERE a.user_id = %(user_id)s'
        self.number_of_questions_by_user_id = 'SELECT COUNT(*) as "questions_num" ' \
                                              'FROM question ' \
                                              'WHERE user_id = %(user_id)s'
        self.number_of_answers_by_user_id = 'SELECT COUNT(*) as "answers_num" ' \
                                            'FROM answer ' \
                                            'WHERE user_id = %(user_id)s'
        self.read_latest_five_questions = 'SELECT id, title, message, view_number, vote_number, submission_time, image FROM question ORDER BY {order_by} DESC LIMIT 5'

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
