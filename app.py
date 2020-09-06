from flask import Flask, render_template, redirect, url_for
from data_manager import *


app = Flask(__name__)


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return request


# List questions
@app.route('/list')
def list():
    table_headers = ['Question id', 'Question title']
    questions = read_questions()

    return render_template('list.html', headers=table_headers, questions=questions)


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


if __name__ == '__main__':
    app.run()
