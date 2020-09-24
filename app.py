from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from data_manager import *
from util import *
import datetime
import time
import os
from urllib.parse import unquote
from database import db, queries


UPLOAD_DIR = 'static/uploaded/'

app = Flask(__name__)

if not os.path.exists(os.path.join(UPLOAD_DIR, 'questions')):
    os.makedirs(os.path.join(UPLOAD_DIR, 'questions'))

if not os.path.exists(os.path.join(UPLOAD_DIR, 'answers')):
    os.makedirs(os.path.join(UPLOAD_DIR, 'answers'))

# Edit the 'Cache-Control' header to force browser to not cache external files, e.g. css files.
# The solution is suitable for development only.
@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return request


# Welcome page
@app.route('/')
def main_page():
    return render_template('main_page.html')


# List questions
@app.route('/list')
def list():
    table_headers = {
        'headers': ['Question', 'Number of views', 'Number of votes', 'Submission time'],
        'keys': ['title', 'view_number', 'vote_number', 'submission_time'],
        'directions': [None, None, None, None]
    }

    questions = db.execute_query(queries.read_questions_all)

    order_by = request.args.get('order_by')
    order_direction = request.args.get('order_direction')

    if order_by:
        questions_sorted = sort_questions(order_by, questions, direction=order_direction)
        index = table_headers['keys'].index(order_by)
        table_headers['directions'][index] = order_direction
    else:
        questions_sorted = sort_questions('submission_time', questions, direction='desc')
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

    answers = db.execute_query(queries.read_answers_by_question_id, {'question_id': question_id})

    return render_template('question-details.html', question_id=question_id, question_data=question, answers_data=answers)


# Ask a question
@app.route('/add-question', methods=["GET", "POST"])
def question_add():
    if request.method == "POST":
        question = request.form.to_dict()
        question["submission_time"] = datetime.datetime.now()
        question["vote_number"] = 0
        question["view_number"] = 0
        question['image'] = None

        uploaded_file = request.files.get('image')
        if uploaded_file:
            file_name = f'{time.time()}_{uploaded_file.filename}'

            file_path = os.path.join(UPLOAD_DIR, 'questions', file_name)
            uploaded_file.save(file_path)
            question['image'] = file_name

        db.execute_query(queries.add_new_question, question)

        return redirect(url_for('list'))

    else:
        return render_template('add-question.html')


# post answer
@app.route('/question/<int:question_id>/new-answer', methods=["GET", "POST"])
def answer_post(question_id):
    if request.method == "POST":
        answer = request.form.to_dict()
        answer["submission_time"] = datetime.datetime.now()
        answer["vote_number"] = 0
        answer["question_id"] = question_id
        answer['image'] = None

        uploaded_file = request.files.get('image')
        if uploaded_file:
            file_name = f'{time.time()}_{uploaded_file.filename}'

            file_path = os.path.join(UPLOAD_DIR, 'answers', file_name)
            uploaded_file.save(file_path)
            answer['image'] = file_name

        db.execute_query(queries.add_new_answer, answer)

        return redirect(url_for("question_details", question_id=question_id))

    else:
        return render_template('new-answer.html', question_id=question_id)


# Delete question
@app.route('/question/<int:question_id>/delete')
def question_delete(question_id):
    question = db.execute_query(queries.read_question_by_id, {'id': question_id})[0]

    if question['image'] != "":
        os.remove(os.path.join(UPLOAD_DIR, 'questions', question['image']))

    db.execute_query(queries.delete_question_by_id, {'id': question_id})

    return redirect(url_for('list'))


# Edit a question
@app.route('/question/<int:question_id>/edit', methods=["GET", "POST"])
def question_edit(question_id):
    question = db.execute_query(queries.read_question_by_id, {'id': question_id})[0]

    if request.method == "POST":
        question["title"] = request.form["title"]
        question["message"] = request.form["message"]
        question["submission_time"] = datetime.datetime.now()

        db.execute_query(queries.update_question_by_id, question)

        return redirect(url_for("question_details", question_id=question_id))
    else:
        return render_template("edit-question.html", title=question["title"], message=question["message"])


# Delete an answer
@app.route('/answers/<int:answer_id>/delete')
def answer_delete(answer_id):
    answer = db.execute_query(queries.read_answer_by_id, {'id': answer_id})[0]

    if answer['image'] is not None:
        os.remove(os.path.join(UPLOAD_DIR, 'answers', answer['image']))

    db.execute_query(queries.delete_answer_by_id, {'id': answer_id})

    return redirect(url_for('question_details', question_id=answer['question_id']))


# Vote-up a question
@app.route('/question/<question_id>/vote_up')
def question_vote_up(question_id):
    return render_template('under_construction.html')


# Vote-down a question
@app.route('/question/<question_id>/vote_down')
def question_vote_down(question_id):
    return render_template('under_construction.html')


# Vote-up an answer
@app.route('/answer/<answer_id>/vote_up')
def answer_vote_up(answer_id):
    return render_template('under_construction.html')


# Vote-down an answer
@app.route('/answer/<answer_id>/vote_down')
def answer_vote_down(answer_id):
    return render_template('under_construction.html')


def time_to_utc(raw_time):
    time_formatted = raw_time.strftime('%d %B %Y, %H:%M').lstrip('0')
    return time_formatted


def file_size(file_name):
    file_name = file_name.lstrip("/")
    size_bytes = os.path.getsize(unquote(file_name)) * 0.001 # unquote converts url-encoded string into the normal one
    size_kb = f'{size_bytes:.1f}'

    return size_kb


@app.context_processor
def util_functions():
    return dict(
        time_to_utc=time_to_utc,
        file_size=file_size
    )


if __name__ == '__main__':
    app.run()
