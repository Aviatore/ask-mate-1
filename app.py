from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from data_manager import *
from util import *
import datetime
import time
import os
from urllib.parse import unquote


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

    questions = read_questions()

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
    questions = read_questions()
    question_title = ""
    question_message = ""

    question_data = None

    for question in questions:
        if str(question["id"]) == question_id:
            question_data = question
            # question_title = question["title"]
            # question_message = question["message"]

    question_data['view_number'] += 1
    write_questions(questions)

    answers = read_answers()
    answers_data = []

    for answer in answers:
        if str(answer["question_id"]) == question_id:
            answers_data.append(answer)

    return render_template('question-details.html', question_id=question_id, question_data=question_data, answers_data=answers_data)


# Ask a question
@app.route('/add-question', methods=["GET", "POST"])
def question_add():
    if request.method == "POST":
        saved_questions = read_questions()
        question = request.form.to_dict()
        question["id"] = get_id(read_questions())
        question["submission_time"] = str(int(time.time()))
        question["vote_number"] = "0"
        question["view_number"] = "0"

        uploaded_file = request.files.get('image')
        if uploaded_file:
            file_name = f'{get_id(saved_questions)}_{uploaded_file.filename}'

            file_path = os.path.join(UPLOAD_DIR, 'questions', file_name)
            uploaded_file.save(file_path)
            question['image'] = file_name

        print(question)
        saved_questions.append(question)
        write_questions(saved_questions)

        return redirect(url_for('list'))

    else:
        return render_template('add-question.html')


# post answer
@app.route('/question/<question_id>/new-answer', methods=["GET", "POST"])
def answer_post(question_id):
    if request.method == "POST":
        saved_answers = read_answers()
        answer = request.form.to_dict()
        answer["id"] = get_id(read_answers())
        answer["submission_time"] = str(int(time.time()))
        answer["vote_number"] = "0"
        answer["question_id"] = question_id

        uploaded_file = request.files.get('image')
        if uploaded_file:
            file_name = f'{get_id(saved_answers)}_{uploaded_file.filename}'

            file_path = os.path.join(UPLOAD_DIR, 'answers', file_name)
            uploaded_file.save(file_path)
            answer['image'] = file_name

        saved_answers.append(answer)
        write_answers(saved_answers)

        return redirect(url_for("question_details", question_id=question_id))

    else:
        return render_template('new-answer.html', question_id=question_id)


# Delete question
@app.route('/question/<int:question_id>/delete')
def question_delete(question_id):
    questions = read_questions()
    question_to_delete = [question for question in questions if question['id'] == question_id][0]
    questions.remove(question_to_delete)

    write_questions(questions)

    if question_to_delete['image'] != "":
        os.remove(os.path.join(UPLOAD_DIR, 'questions', question_to_delete['image']))

    return redirect(url_for('list'))


# Edit a question
@app.route('/question/<question_id>/edit', methods=["GET", "POST"])
def question_edit(question_id):
    questions = read_questions()
    question_to_edit = {}

    for question in questions:
        if str(question["id"]) == str(question_id):
            question_to_edit = question

    title = question_to_edit["title"]
    message = question_to_edit["message"]

    if request.method == "POST":
        new_title = request.form["title"]
        new_message = request.form["message"]
        question_to_edit["title"] = new_title
        question_to_edit["message"] = new_message
        question_to_edit["submission_time"] = str(int(time.time()))
        write_questions(questions)

        return redirect(url_for("question_details", question_id=question_id))

    else:
        return render_template("edit-question.html", title=title, message=message)


# Delete an answer
@app.route('/answers/<int:answer_id>/delete')
def answer_delete(answer_id):
    answers = read_answers()
    answer_to_delete = [answer for answer in answers if answer['id'] == answer_id][0]

    if answer_to_delete['image'] != "":
        os.remove(os.path.join(UPLOAD_DIR, 'answers', answer_to_delete['image']))

    answers.remove(answer_to_delete)

    write_answers(answers)



    return redirect(url_for('question_details', question_id=answer_to_delete['question_id']))


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
    time_converted = datetime.datetime.fromtimestamp(raw_time)
    time_formatted = time_converted.strftime('%d %B %Y, %H:%M').lstrip('0')
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
