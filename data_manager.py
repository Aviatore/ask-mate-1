from connection import *


QUESTIONS_FILE = 'sample_data/question.csv'
QUESTIONS_HEADERS = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_FILE = 'sample_data/answer.csv'
ANSWERS_HEADERS = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def read_questions():
    questions = read_csv(QUESTIONS_FILE)

    for question in questions:
        for key in question.keys():
            if question[key] is not None:
                if question[key].isdigit():
                    question[key] = int(question[key])

    return questions


def read_answers():
    return read_csv(ANSWERS_FILE)


def write_questions(data):
    write_csv(QUESTIONS_FILE, data, QUESTIONS_HEADERS)


def write_answers(data):
    write_csv(ANSWERS_FILE, data, ANSWERS_HEADERS)
