from flask import Flask, render_template, redirect, url_for, request, send_from_directory, session, flash, make_response
from data_manager import *
from util import parse_search_phrase, format_search_results
import datetime
import time
import os
from urllib.parse import unquote
from werkzeug.utils import secure_filename
from database import db, queries
import bcrypt
import base64
from functools import wraps


UPLOAD_DIR = 'uploaded/'

app = Flask(__name__)
app.secret_key = os.urandom(16)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            print('user logged in')
            return func(*args, **kwargs)
        print('user is not logged in')
        return redirect(url_for('login'))

    return wrapper


if not os.path.exists(os.path.join(UPLOAD_DIR, 'questions')):
    os.makedirs(os.path.join(UPLOAD_DIR, 'questions'))

if not os.path.exists(os.path.join(UPLOAD_DIR, 'answers')):
    os.makedirs(os.path.join(UPLOAD_DIR, 'answers'))

# Edit the 'Cache-Control' header to force browser to not cache external files, e.g. css files.
# The solution is suitable for development only.
# @app.after_request
# def add_header(request):
#     request.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
#     return request


# Welcome page
@app.route('/')
def main_page():
    table_headers = {
        'headers': ['Question', 'Number of views', 'Number of votes', 'Submission time'],
        'keys': ['title', 'view_number', 'vote_number', 'submission_time'],
        'directions': [None, None, None, None]
    }

    order_by = 'submission_time'
    latest_questions = db.execute_query(queries.read_latest_five_questions, order_by=order_by)
    index = table_headers['keys'].index('submission_time')
    table_headers['directions'][index] = 'desc'

    response = make_response(render_template('main_page.html', headers=table_headers, questions=latest_questions, order_by=order_by))
    response.set_cookie('prev_page', base64_encode(url_for('main_page')))

    return response

# List questions
@app.route('/list')
def question_list():
    table_headers = {
        'headers': ['Question', 'Number of views', 'Number of votes', 'Submission time'],
        'keys': ['title', 'view_number', 'vote_number', 'submission_time'],
        'directions': [None, None, None, None]
    }

    order_by = request.args.get('order_by', 'submission_time')
    order_direction = request.args.get('order_direction')

    if order_by:
        if order_direction == 'asc':
            questions_sorted = db.execute_query(queries.read_questions_all_asc, order_by=order_by)
        else:
            questions_sorted = db.execute_query(queries.read_questions_all_desc, order_by=order_by)

        index = table_headers['keys'].index(order_by)
        table_headers['directions'][index] = order_direction
    else:
        questions_sorted = db.execute_query(queries.read_questions_all_desc, order_by=order_by)

        index = table_headers['keys'].index('submission_time')
        table_headers['directions'][index] = 'desc'

    response = make_response(render_template('list.html', headers=table_headers, questions=questions_sorted, order_by=order_by,
                           order_direction=order_direction))

    response.set_cookie('prev_page', base64_encode(url_for('question_list')))

    return response


# List users
@app.route('/users')
def users_list():
    table_headers = {
        'headers': ['User id', 'Username', 'Registration date', 'Reputation', 'Questions asked', 'Answers added', 'Commented posts'],
        'keys': ['user_id', 'username', 'registration_date', 'reputation', 'questions_num', 'answers_num', 'comments_num']
    }

    users = db.execute_query(queries.users_activity_stats)

    return render_template('users_list.html', headers=table_headers, users=users)


# Display a question
@app.route('/question/<question_id>')
def question_details(question_id):
    question = db.execute_query(queries.read_question_by_id, {'id': question_id})[0]
    comments = db.execute_query(queries.read_comments_by_question_id, {"question_id": question_id})

    if question != "":
        question['view_number'] += 1

    db.execute_query(queries.update_question_by_id, question)

    if question['image'] is not None:
        question['image'] = question['image'].split(';')

    answers = db.execute_query(queries.read_answers_by_question_id, {'question_id': question_id})

    for answer in answers:
        if answer['image'] is not None:
            answer['image'] = answer['image'].split(';')

    # tags
    tag_id_row = db.execute_query(queries.read_tag_id_by_question_id, {'question_id': question_id})
    question_tags = {}
    for t_row in tag_id_row:
        tag_id = t_row['tag_id']
        question_tag_row = db.execute_query(queries.read_tag_by_id, {'tag_id': tag_id})
        for qt_row in question_tag_row:
            question_tags[tag_id] = qt_row['name']

            # question_tags.append(qt_row['name'])

    response = make_response(render_template('question-details.html',
                           question_id=question_id,
                           question_data=question,
                           answers_data=answers,
                           question_tags=question_tags,
                           comments=comments))

    response.set_cookie('prev_page', base64_encode(url_for('question_details', question_id=question_id)))

    return response


# Ask a question
@app.route('/add-question', methods=["GET", "POST"])
@login_required
def question_add():
    warnings = {
        'title': None,
        'message': None
    }

    if request.method == "POST":
        question = request.form.to_dict()
        question["submission_time"] = datetime.datetime.now()
        question["vote_number"] = 0
        question["view_number"] = 0
        question['image'] = None

        if question['title'] == '':
            warnings['title'] = "You must define your question's title"
        if question['message'] == '':
            warnings['message'] = "You must type a message"

        # If at least one warning is set, a new response is rendered with warnings argument
        # that allow to format problematic form fields.
        if len([f for f in warnings if warnings[f] is not None]) > 0:
            return render_template('add-question.html', warnings=warnings, question=question)
            # return redirect(url_for('question_add', warnings=warnings))

        update_image_files(question)
        question['user_id'] = session['user_id']

        db.execute_query(queries.add_new_question, question)

        return redirect(url_for('question_list'))

    else:
        return render_template('add-question.html', warnings=None, question=None)


# post answer
@app.route('/question/<int:question_id>/new-answer', methods=["GET", "POST"])
@login_required
def answer_post(question_id):
    warnings = {
        'message': None
    }

    if request.method == "POST":
        answer = request.form.to_dict()
        answer["submission_time"] = datetime.datetime.now()
        answer["vote_number"] = 0
        answer["question_id"] = question_id
        answer['image'] = None

        if answer['message'] == '':
            warnings['message'] = "You must type a message"

        # If a warning is set, a new response is rendered with warnings argument
        # that allow to format problematic form field.
        if warnings['message'] is not None:
            return render_template('new-answer.html', question_id=question_id, warnings=warnings)

        update_image_files(answer)

        answer['user_id'] = session['user_id']

        db.execute_query(queries.add_new_answer, answer)

        return redirect(url_for("question_details", question_id=question_id))

    else:
        return render_template('new-answer.html', question_id=question_id, warnings=None)


# Delete question
@app.route('/question/<int:question_id>/delete')
@login_required
def question_delete(question_id):
    question = db.execute_query(queries.read_question_by_id, {'id': question_id})[0]
    quest_answers = db.execute_query(queries.read_answers_by_question_id, {'question_id': question_id})

    db.execute_query(queries.delete_question_tag_links_by_question_id, {'question_id':question_id})
    db.execute_query(queries.delete_question_by_id, {'id': question_id})

    if question['image'] is not None:
        # The 'split' method allows to get a list of more than one submitted image files
        # tha can be displayed on the page.
        for image_path in question['image'].split(';'):
            os.remove(os.path.join(UPLOAD_DIR, 'questions', image_path))

    for quest_answer in quest_answers:
        if quest_answer['image'] is not None:
            for image_path in quest_answer['image'].split(';'):
                os.remove(os.path.join(UPLOAD_DIR, 'answers', image_path))

    return redirect(url_for('question_list'))


# Edit a question
@app.route('/question/<int:question_id>/edit', methods=["GET", "POST"])
@login_required
def question_edit(question_id):
    output = edit_engine(table='question', id=question_id)

    if output['return_code'] == 'form_ok':
        return redirect(url_for("question_details", question_id=question_id))
    elif output['return_code'] == 'form_fail':
        return render_template('edit-question.html', question=output['table_row'], warnings=output['warnings'])
    elif output['return_code'] == 'ok':
        return render_template("edit-question.html", question=output['table_row'], warnings=None)


# Edit an answer
@app.route('/answer/<int:answer_id>/edit', methods=["GET", "POST"])
@login_required
def answer_edit(answer_id):
    output = edit_engine(table='answer', id=answer_id)

    if output['return_code'] == 'form_ok':
        return redirect(url_for("question_details", question_id=output['table_row']['question_id']))
    elif output['return_code'] == 'form_fail':
        return render_template('edit-answer.html', answer=output['table_row'], warnings=output['warnings'])
    elif output['return_code'] == 'ok':
        return render_template("edit-answer.html", answer=output['table_row'], warnings=None)


def edit_engine(table, id):
    """The function handles edition of both questions and answers"""

    warnings = {
        'title': None,
        'message': None
    }
    if table == 'question':
        search_query = queries.read_question_by_id
        update_query = queries.update_question_by_id
    elif table == 'answer':
        search_query = queries.read_answer_by_id
        update_query = queries.update_answer_by_id

    table_row = db.execute_query(search_query, {'id': id})[0]

    if table_row['image'] is not None:
        table_row['image'] = table_row['image'].split(';')

    if request.method == "POST":
        if table == 'question':
            table_row["title"] = request.form["title"]

        table_row["message"] = request.form["message"]
        table_row["submission_time"] = datetime.datetime.now()

        if table == 'question':
            if table_row['title'] == '':
                warnings['title'] = "You must define your question's title"

        if table_row['message'] == '':
            warnings['message'] = "You must type a message"

        # If at least one warning is set, a new response is rendered with warnings argument
        # that allow to format problematic form fields.
        if len([f for f in warnings if warnings[f] is not None]) > 0:
            output = {
                'return_code': 'form_fail',
                'warnings': warnings,
                'table_row': table_row
            }

            return output

        remove_images = request.form.get('image-remove')
        if remove_images:
            table_row['image'] = None
        else:
            # The function saves submitted files (if any) and saves images names under the 'image' key
            # in the question dictionary.
            update_image_files(table_row)

        db.execute_query(update_query, table_row)

        output = {
            'return_code': 'form_ok',
            'table_row': table_row
        }

        return output
    else:
        output = {
            'return_code': 'ok',
            'table_row': table_row
        }

        return output


# Delete an answer
@app.route('/answers/<int:answer_id>/delete')
@login_required
def answer_delete(answer_id):
    answer = db.execute_query(queries.read_answer_by_id, {'id': answer_id})[0]

    if answer['image'] is not None:
        for image_path in answer['image'].split(';'):
            os.remove(os.path.join(UPLOAD_DIR, 'answers', image_path))

    db.execute_query(queries.delete_answer_by_id, {'id': answer_id})

    return redirect(url_for('question_details', question_id=answer['question_id']))


# Vote-up a question
@app.route('/question/<int:question_id>/vote_up')
@login_required
def question_vote_up(question_id):
    if 'user_id' in session:
        question = db.execute_query(queries.read_question_by_id, {'id': question_id})[0]

        if session['user_id'] not in question['users_id_that_vote']:
            question["view_number"] -= 1
            question["vote_number"] += 1

            question['users_id_that_vote'].append(session['user_id'])

            db.execute_query(queries.update_question_by_id, question)


            rep_value = 5
            question_user_id = db.execute_query(queries.read_user_id_by_question_id, {'id':question_id})[0]['user_id']
            db.execute_query(queries.add_reputation, {'rep_value':rep_value, 'user_id':question_user_id})

    return redirect(url_for('question_details', question_id=question_id))


# Vote-down a question
@app.route('/question/<question_id>/vote_down')
@login_required
def question_vote_down(question_id):
    if 'user_id' in session:
        question = db.execute_query(queries.read_question_by_id, {'id': question_id})[0]

        if session['user_id'] not in question['users_id_that_vote']:
            question["view_number"] -= 1
            question["vote_number"] -= 1

            question['users_id_that_vote'].append(session['user_id'])

            db.execute_query(queries.update_question_by_id, question)

            rep_value = -2
            question_user_id = db.execute_query(queries.read_user_id_by_question_id, {'id':question_id})[0]['user_id']
            db.execute_query(queries.add_reputation, {'rep_value':rep_value, 'user_id':question_user_id})

    return redirect(url_for('question_details', question_id=question_id))


# Vote-up an answer
@app.route('/answer/<answer_id>/vote_up')
@login_required
def answer_vote_up(answer_id):
    if 'user_id' in session:
        answer = db.execute_query(queries.read_answer_by_id, {'id': answer_id})[0]
        question = db.execute_query(queries.read_question_by_id, {'id': answer['question_id']})[0]

        if session['user_id'] not in answer['users_id_that_vote']:
            answer["vote_number"] += 1
            question["view_number"] -= 1

            answer['users_id_that_vote'].append(session['user_id'])
            db.execute_query(queries.update_answer_by_id, answer)
            db.execute_query(queries.update_question_by_id, question)

            rep_value = 10
            asnwer_user_id = db.execute_query(queries.read_user_id_by_answer_id, {'id':answer_id})[0]['user_id']
            db.execute_query(queries.add_reputation, {'rep_value':rep_value, 'user_id':asnwer_user_id})


    return redirect(url_for('question_details', question_id=answer['question_id']))


# Vote-down an answer
@app.route('/answer/<answer_id>/vote_down')
@login_required
def answer_vote_down(answer_id):
    if 'user_id' in session:
        answer = db.execute_query(queries.read_answer_by_id, {'id': answer_id})[0]
        question = db.execute_query(queries.read_question_by_id, {'id': answer['question_id']})[0]

        if session['user_id'] not in answer['users_id_that_vote']:
            answer["vote_number"] -= 1
            question["view_number"] -= 1

            answer['users_id_that_vote'].append(session['user_id'])
            db.execute_query(queries.update_answer_by_id, answer)
            db.execute_query(queries.update_question_by_id, question)

            rep_value = -2
            asnwer_user_id = db.execute_query(queries.read_user_id_by_answer_id, {'id':answer_id})[0]['user_id']
            db.execute_query(queries.add_reputation, {'rep_value':rep_value, 'user_id':asnwer_user_id})

    return redirect(url_for('question_details', question_id=answer['question_id']))


@app.route("/question/<question_id>/new-tag", methods=["POST", "GET"])
@login_required
def new_tag(question_id):

    all_tags = []
    tags_rows = db.execute_query(queries.read_all_tags)
    for row in tags_rows:
        all_tags.append(row['name'])

    if request.method == "POST":
        tag = request.form.to_dict()
        if tag['add_tag'] != "":
            name = tag['add_tag']
        else:
            name = tag['select_tag']

        if name not in all_tags:
            db.execute_query(queries.add_new_tag, {'name':name})
            tag_id = db.execute_query(queries.read_tag_id_by_name, {'name':name})[0]['id']
            db.execute_query(queries.link_tag_question, {'question_id':question_id, 'tag_id':tag_id})
        else:
            question_tag_ids = []
            question_tag_ids_rows = db.execute_query(queries.read_tag_id_by_question_id, {'question_id':question_id})
            for row in question_tag_ids_rows:
                question_tag_ids.append(row['tag_id'])
            question_tags = []
            for item in question_tag_ids:
                question_tags.append(db.execute_query(queries.read_tag_by_id, {'tag_id':item})[0]['name'])
            if name not in question_tags:
                tag_id = db.execute_query(queries.read_tag_id_by_name, {'name': name})[0]['id']
                db.execute_query(queries.link_tag_question, {'question_id': question_id, 'tag_id': tag_id})

        return redirect(url_for('question_details', question_id=question_id))

    else:

        return render_template("new_tag.html", question_id=question_id, all_tags=all_tags)


@app.route('/question/<question_id>/tag/<tag_id>/delete', methods=['POST', "GET"])
@login_required
def delete_tag(question_id, tag_id):
    db.execute_query(queries.delete_question_tag_links_by_tag_id_question_id, {'question_id':question_id, 'tag_id':tag_id})

    return redirect(url_for('question_details', question_id=question_id))


@app.route('/registration', methods=['GET', 'POST'])
def register():
    warnings = {
        'username': None,
        'email': None,
        'password': None
    }
    new_user = {
        'username': None,
        'email': None,
        'password': None
    }

    if request.method == 'POST':
        new_user['username'] = request.form.get('username')
        new_user['email'] = request.form.get('email')
        new_user['password'] = request.form.get('password')

        if new_user['username'] == '':
            warnings['username'] = "You must define your user name."

        if new_user['email'] == '':
            warnings['email'] = "You must define you email"

        if new_user['password'] == '':
            warnings['password'] = "You must define a password."

        if len([f for f in warnings if warnings[f] is not None]) > 0:
            return render_template('register.html', warnings=warnings)

        user = db.execute_query(queries.get_user_by_username, new_user)

        if len(user) > 0:
            warnings['username'] = "The provided user name already exists."
            return render_template('register.html', warnings=warnings)

        new_user['password'] = bcrypt.hashpw(new_user['password'].encode('utf-8'), bcrypt.gensalt())

        db.execute_query(queries.add_new_user, params=new_user)

        return redirect(url_for('main_page'))

    return render_template('register.html', warnings=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    warnings = {
        'username': None,
        'password': None,
        'not_valid': None
    }

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == '':
            warnings['username'] = "You must define your user name."

        if password == '':
            warnings['password'] = "You must define a password."

        if len([f for f in warnings if warnings[f] is not None]) > 0:
            return render_template('login.html', warnings=warnings)

        user = db.execute_query(queries.get_user_by_username, {'username': username})
        user = user[0] if len(user) > 0 else None

        if user and bcrypt.checkpw(password.encode('utf-8'), b'' + user['password']):
            session['username'] = user['username']
            session['user_id'] = user['user_id']

            return redirect(get_prev_url())

        warnings['not_valid'] = "Your user name and/or password is not valid."

        return render_template('login.html', warnings=warnings)

    response = make_response(render_template('login.html', warnings=None))

    prev_url = request.referrer
    if prev_url:
        response.set_cookie('prev_page', base64_encode(prev_url))
    else:
        prev_url = url_for('main_page')
        response.set_cookie('prev_page', base64_encode(prev_url))

    return response
    # return render_template('login.html', warnings=None)


@app.route('/logout')
def logout():
    if session:
        session.pop('username')
        session.pop('user_id')

    prev_url = request.cookies.get('prev_page')
    if prev_url:
        prev_url = base64_decode(prev_url)
    else:
        prev_url = url_for('main_page')

    return redirect(prev_url)

    # return redirect(url_for('main_page'))


@app.route('/user/<int:user_id>')
def user_details(user_id):
    questions = db.execute_query(queries.get_all_questions_by_user_id, {'user_id': user_id})
    questions_number = db.execute_query(queries.number_of_questions_by_user_id, {'user_id': user_id})[0]['questions_num']
    answers = db.execute_query(queries.get_all_answers_by_user_id, {'user_id': user_id})
    answers_number = db.execute_query(queries.number_of_answers_by_user_id, {'user_id': user_id})[0]['answers_num']
    user = db.execute_query(queries.get_user_by_user_id, {'user_id': user_id})[0]

    response = make_response(render_template('user_page.html', questions=questions, answers=answers, questions_number=questions_number,
                           answers_number=answers_number, user=user))

    response.delete_cookie('prev_page')

    return response


def update_image_files(type):
    """The function gets submitted files list and saves each file to its destination
    directory. If more than one file is submitted, file names are joined by a semicolon
    and saved as a single string to in a database. The argument 'type' is of type
    dictionary with keys corresponding to the table (question or answer) columns in a database."""

    if 'question_id' in type:
        dir = 'answers'
    else:
        dir = 'questions'

    uploaded_files = request.files.getlist('image')
    paths = []
    if uploaded_files:
        for file in uploaded_files:
            if file.filename != "":
                file_name_raw = secure_filename(file.filename)
                file_name = f'{time.time()}_{file_name_raw}'
                file_path = os.path.join(UPLOAD_DIR, dir, file_name)
                file.save(file_path)
                paths.append(file_name)

    if len(paths) > 0:
        type['image'] = ';'.join(paths)
    elif isinstance(type['image'], list):
        type['image'] = ';'.join(type['image'])


def time_to_utc(raw_time):
    time_formatted = raw_time.strftime('%d %B %Y, %H:%M').lstrip('0')
    return time_formatted


def file_size(directory, file_name):
    file_name = unquote(file_name) # unquote converts url-encoded string into the normal one
    file_path = os.path.join(UPLOAD_DIR, directory, file_name)
    file_size_bytes = os.path.getsize(file_path) * 0.001
    file_size_kb = f'{file_size_bytes:.1f}'

    return file_size_kb


def base64_encode(message):
    return base64.b64encode(message.encode('utf-8'))


def base64_decode(message):
    return base64.b64decode(message).decode('utf-8')


def get_prev_url():
    prev_url = request.cookies.get('prev_page')

    if prev_url:
        return base64_decode(prev_url)

    return url_for('main_page')


@app.route('/get_file/<directory>/<file_name>')
def get_image(directory, file_name):
    return send_from_directory(os.path.join(UPLOAD_DIR, directory), filename=file_name)


@app.route('/search')
def search_question():
    search_phrase = request.args.get('q')

    quoted, unquoted = parse_search_phrase(search_phrase)

    quoted.extend(unquoted)

    quoted_copy = quoted.copy()
    # for index1, i in enumerate(quoted):
    #     for index2, j in enumerate(quoted):
    #         if index1 != index2 and i in j:
    #             quoted_copy.remove(i)

    merge_phrase_parenthesis = [f'({f})' for f in quoted_copy]

    regex_phrase = '|'.join(merge_phrase_parenthesis)

    questions = db.execute_query(queries.search_question, {'query': regex_phrase})
    answers = db.execute_query(queries.search_answer, {'query': regex_phrase})

    for table_type in [answers, questions]:
        for item in table_type:
            if 'title' in item:
                item['title'] = format_search_results(item['title'], quoted_copy)
            item['message'] = format_search_results(item['message'], quoted_copy)

    response = make_response(render_template('search-results.html', questions=questions, answers=answers))
    response.set_cookie('prev_page', base64_encode(url_for('search_question', q=search_phrase)))

    return response


@app.context_processor
def util_functions():
    return dict(
        time_to_utc=time_to_utc,
        file_size=file_size
    )

# Add comment to question
@app.route('/question/<int:question_id>/new-comment', methods=["GET", "POST"])
def add_comment_to_question(question_id):

    warnings = {'message': None}

    if request.method == "POST":
        comment = request.form.to_dict()
        comment["submission_time"] = datetime.datetime.now()
        comment["edited_count"] = 0
        comment["question_id"] = question_id

        if comment['message'] == '':
            warnings['message'] = "You must type a message"

        comment['user_id'] = session['user_id']

        # If at least one warning is set, a new response is rendered with warnings argument
        # that allow to format problematic form fields.
        if warnings["message"] is not None:
            return render_template('add-comment-to-question.html', warnings=warnings, comment=comment, question_id=question_id)

        db.execute_query(queries.add_comment_to_question, comment)

        return redirect(url_for('question_details', question_id=question_id))

    else:
        return render_template('add-comment-to-question.html', warnings=None, comment=None, question_id=question_id)


# Add comment to answer
@app.route('/answer/<answer_id>/new-comment', methods=["GET", "POST"])
def add_comment_to_answer(answer_id):
    answer = db.execute_query(queries.read_answer_by_id, {"id": answer_id})[0]
    warnings = {'message': None}

    if request.method == "POST":
        comment = request.form.to_dict()
        comment["submission_time"] = datetime.datetime.now()
        comment["edited_count"] = 0
        comment["answer_id"] = answer_id
        comment["question_id"] = answer["question_id"]

        if comment['message'] == '':
            warnings['message'] = "You must type a message"

        comment['user_id'] = session['user_id']

        # If at least one warning is set, a new response is rendered with warnings argument
        # that allow to format problematic form fields.
        if warnings["message"] is not None:
            return render_template('add-comment-to-answer.html', warnings=warnings, comment=comment, answer=answer)

        db.execute_query(queries.add_comment_to_answer, comment)

        return redirect(url_for('question_details', question_id=answer['question_id']))

    else:
        return render_template('add-comment-to-answer.html', warnings=None, comment=None, answer=answer)





if __name__ == '__main__':
    app.run()
