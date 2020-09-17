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

    return render_template('list.html', headers=table_headers, questions=questions_sorted, order_by=order_by, order_direction=order_direction)


# Display a question
@app.route('/question/<question_id>')
def question_details(question_id):
    return render_template('under_contstruction.html')


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
        print(question)
        saved_questions.append(question)
        write_answers(saved_questions)

        return redirect(url_for('list'))

    else:
        return render_template('add-question.html')


# @app.route('/add-question', methods=["GET", "POST"])
# def question_add_post():
#     new_user_question = dict(request.form)
#     new_id = get_id(read_questions())
#     new_user_question["id"] = new_id
#
#     write_questions([new_user_question])
#
#     return redirect(url_for('list'))



# Post an answer
@app.route('/question/<question_id>/new-answer')
def answer_post(question_id):
    return render_template('under_contstruction.html')


# Delete question
@app.route('/question/<int:question_id>/delete')
def question_delete(question_id):
    questions = read_questions()
    questions.remove([question for question in questions if question['id'] == question_id][0])

    write_questions(questions)

    return redirect(url_for('list'))


# Edit a question
@app.route('/question/<question_id>/edit')
def question_edit(question_id):
    return render_template('under_contstruction.html')


# Delete an answer
@app.route('/answers/<answer_id>/delete')
def answer_delete(answer_id):
    answers = read_questions()
    answer_to_delete = [answer for answer in answers if answer['id'] == answer_id][0]
    answers.remove(answer_to_delete)

    write_answers(answers, QUESTIONS_HEADERS)

    return redirect(url_for('question_details', question_id=answer_to_delete['question_id']))


# Vote-up a question
@app.route('/question/<question_id>/vote_up')
def question_vote_up(question_id):
    return render_template('under_contstruction.html')


# Vote-down a question
@app.route('/question/<question_id>/vote_down')
def question_vote_down(question_id):
    return render_template('under_contstruction.html')


# Vote-up an answer
@app.route('/answer/<answer_id>/vote_up')
def answer_vote_up(answer_id):
    return render_template('under_contstruction.html')


# Vote-down an answer
@app.route('/answer/<answer_id>/vote_down')
def answer_vote_down(answer_id):
    return render_template('under_contstruction.html')


def time_to_utc(raw_time):
    time_converted = datetime.datetime.fromtimestamp(raw_time)
    time_formatted = time_converted.strftime('%d %B %Y, %H:%M').lstrip('0')
    return time_formatted


@app.context_processor
def util_functions():
    return dict(time_to_utc=time_to_utc)


if __name__ == '__main__':
    app.run()
