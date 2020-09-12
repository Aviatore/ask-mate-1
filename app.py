from flask import Flask, render_template, redirect, url_for
from data_manager import *
from util import *
import datetime


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
        'keys': ['title', 'message', 'view_number', 'vote_number', 'submission_time']
    }

    questions = read_questions()
    questions_by_time = sort_questions('submission_time', questions, direction='desc')

    return render_template('list.html', headers=table_headers, questions=questions_by_time)


# Display a question
@app.route('/question/<question_id>')
def question_details(question_id):
    return render_template('under_contstruction.html')


# Ask a question
@app.route('/add-question')
def question_add():
    return render_template('under_contstruction.html')


# Post an answer
@app.route('/question/<question_id>/new-answer')
def answer_post(question_id):
    return render_template('under_contstruction.html')


# Delete question
@app.route('/question/<question_id>/delete')
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
