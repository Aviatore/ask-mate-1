from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash
from data_manager import *
from util import parse_search_phrase
import datetime
import time
import os
from urllib.parse import unquote
from werkzeug.utils import secure_filename
from database import db, queries


UPLOAD_DIR = 'uploaded/'

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

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
    return render_template('main_page.html')


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

    return render_template('list.html', headers=table_headers, questions=questions_sorted, order_by=order_by,
                           order_direction=order_direction)


# Display a question
@app.route('/question/<question_id>')
def question_details(question_id):
    question = db.execute_query(queries.read_question_by_id, {'id': question_id})[0]

    if question != "":
        question['view_number'] += 1

    db.execute_query(queries.update_question_by_id, question)

    if question['image'] is not None:
        question['image'] = question['image'].split(';')

    answers = db.execute_query(queries.read_answers_by_question_id, {'question_id': question_id})

    for answer in answers:
        if answer['image'] is not None:
            answer['image'] = answer['image'].split(';')

    return render_template('question-details.html', question_id=question_id, question_data=question, answers_data=answers)


# Ask a question
@app.route('/add-question', methods=["GET", "POST"])
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

        db.execute_query(queries.add_new_question, question)

        return redirect(url_for('question_list'))

    else:
        return render_template('add-question.html', warnings=None, question=None)


# post answer
@app.route('/question/<int:question_id>/new-answer', methods=["GET", "POST"])
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

        db.execute_query(queries.add_new_answer, answer)

        return redirect(url_for("question_details", question_id=question_id))

    else:
        return render_template('new-answer.html', question_id=question_id, warnings=None)


# Delete question
@app.route('/question/<int:question_id>/delete')
def question_delete(question_id):
    question = db.execute_query(queries.read_question_by_id, {'id': question_id})[0]
    quest_answers = db.execute_query(queries.read_answers_by_question_id, {'question_id': question_id})

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
def question_edit(question_id):
    warnings = {
        'title': None,
        'message': None
    }

    question = db.execute_query(queries.read_question_by_id, {'id': question_id})[0]
    if question['image'] is not None:
        question['image'] = question['image'].split(';')

    if request.method == "POST":
        question["title"] = request.form["title"]
        question["message"] = request.form["message"]
        question["submission_time"] = datetime.datetime.now()

        if question['title'] == '':
            warnings['title'] = "You must define your question's title"
        if question['message'] == '':
            warnings['message'] = "You must type a message"

        # If at least one warning is set, a new response is rendered with warnings argument
        # that allow to format problematic form fields.
        if len([f for f in warnings if warnings[f] is not None]) > 0:
            return render_template('edit-question.html', warnings=warnings, question=question)

        remove_images = request.form.get('image-remove')
        if remove_images:
            question['image'] = None
        else:
            # The function saves submitted files (if any) and saves images names under the 'image' key
            # in the question dictionary.
            update_image_files(question)

        db.execute_query(queries.update_question_by_id, question)

        return redirect(url_for("question_details", question_id=question_id))
    else:
        return render_template("edit-question.html", question=question, warnings=None)


# Delete an answer
@app.route('/answers/<int:answer_id>/delete')
def answer_delete(answer_id):
    answer = db.execute_query(queries.read_answer_by_id, {'id': answer_id})[0]

    if answer['image'] is not None:
        for image_path in answer['image'].split(';'):
            os.remove(os.path.join(UPLOAD_DIR, 'answers', image_path))

    db.execute_query(queries.delete_answer_by_id, {'id': answer_id})

    return redirect(url_for('question_details', question_id=answer['question_id']))


# Vote-up a question
@app.route('/question/<int:question_id>/vote_up')
def question_vote_up(question_id):
    question = db.execute_query(queries.read_question_by_id, {'id': question_id})[0]

    question["view_number"] -= 1

    question["vote_number"] += 1
    db.execute_query(queries.update_question_by_id, question)

    return redirect(url_for('question_details', question_id=question_id))


# Vote-down a question
@app.route('/question/<question_id>/vote_down')
def question_vote_down(question_id):
    question = db.execute_query(queries.read_question_by_id, {'id': question_id})[0]

    question["view_number"] -= 1
    question["vote_number"] -= 1

    db.execute_query(queries.update_question_by_id, question)

    return redirect(url_for('question_details', question_id=question_id))


# Vote-up an answer
@app.route('/answer/<answer_id>/vote_up')
def answer_vote_up(answer_id):
    answer = db.execute_query(queries.read_answer_by_id, {'id': answer_id})[0]

    answer["vote_number"] += 1
    db.execute_query(queries.update_answer_by_id, answer)

    return redirect(url_for('question_details', question_id=answer['question_id']))


# Vote-down an answer
@app.route('/answer/<answer_id>/vote_down')
def answer_vote_down(answer_id):
    answer = db.execute_query(queries.read_answer_by_id, {'id': answer_id})[0]

    answer["vote_number"] -= 1
    db.execute_query(queries.update_answer_by_id, answer)

    return redirect(url_for('question_details', question_id=answer['question_id']))


def update_image_files(type):
    """The function gets submitted files list and saves each file to its destination
    directory. If more than one file is submitted, file names are joined by a semicolon
    and saved as a single string to in a database. The argument 'type' is of type
    dictionary with keys corresponding to the table (question or answer) columns in a database."""

    print(f'DEBUG: ok')
    if 'question_id' in type:
        dir = 'answers'
    else:
        dir = 'questions'

    uploaded_files = request.files.getlist('image')
    paths = []
    if uploaded_files:
        for file in uploaded_files:
            print(f'DEBUG: uploaded_files')
            if file.filename != "":
                print(f'DEBUG: {file.filename}')
                file_name_raw = secure_filename(file.filename)
                file_name = f'{time.time()}_{file_name_raw}'
                file_path = os.path.join(UPLOAD_DIR, dir, file_name)
                file.save(file_path)
                paths.append(file_name)

    if len(paths) > 0:
        print(f'DEBUG: paths len: {len(paths)}')
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


@app.route('/get_file/<directory>/<file_name>')
def get_image(directory, file_name):
    return send_from_directory(os.path.join(UPLOAD_DIR, directory), filename=file_name)


@app.route('/search')
def search_question():
    search_phrase = request.args.get('q')

    quoted, unquoted = parse_search_phrase(search_phrase)

    quoted.extend(unquoted)

    merge_phrase_parenthesis = [f'({f})' for f in quoted]

    regex_phrase = '|'.join(merge_phrase_parenthesis)

    questions = db.execute_query(queries.search_question, {'query': regex_phrase})

    print(f'DEBUG: {regex_phrase}')
    print(f'DEBUG: {[f["id"] for f in questions]}')

    return redirect(url_for('main_page'))


@app.context_processor
def util_functions():
    return dict(
        time_to_utc=time_to_utc,
        file_size=file_size
    )


if __name__ == '__main__':
    app.run()
