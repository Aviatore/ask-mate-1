from flask import Flask, render_template, redirect, url_for, request
from data_manager import *
from util import *
import datetime
import time

app = Flask(__name__)


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
    return render_template('under_construction.html')


# Ask a question
@app.route('/add-question')
def question_add():
    return render_template('under_construction.html')


# Post an answer
@app.route('/question/<question_id>/new-answer', methods=["GET", "POST"])
def answer_post(question_id):
    if request.method == "POST":
        saved_answers = read_answers()
        answer = request.form.to_dict()
        answer["id"] = get_id(read_answers())
        answer["submission_time"] = str(int(time.time()))
        answer["vote_number"] = "0"
        answer["question_id"] = question_id

        saved_answers.append(answer)
        write_answers(saved_answers)

        return redirect(url_for("question_details", question_id=question_id))

    else:
        return render_template('new-answer.html')


# Delete question
@app.route('/question/<int:question_id>/delete')
def question_delete(question_id):
    questions = read_questions()
    questions.remove([question for question in questions if question['id'] == question_id][0])

    write_questions(questions)

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
        # questions.remove(question_to_edit)
        # questions.append(question_to_edit)
        write_questions(questions)

        return redirect(url_for("question_details", question_id=question_id))

    else:
        return render_template("edit-question.html", title=title, message=message)


# Delete an answer
@app.route('/answers/<answer_id>/delete')
def answer_delete(answer_id):
    answers = read_questions()
    answer_to_delete = [answer for answer in answers if answer['id'] == answer_id][0]
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


@app.context_processor
def util_functions():
    return dict(time_to_utc=time_to_utc)


if __name__ == '__main__':
    app.run()
