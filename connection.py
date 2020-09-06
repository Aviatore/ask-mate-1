import csv
QUESTIONS_FILE = 'sample_data/question.csv'


def read_questions():
    questions = []
    with open('sample_data/question.csv') as file:
        reader = csv.DictReader(file)

        for question in reader:
            questions.append(question)

    return questions


def write_questions(questions, fieldnames):
    with open('tmp.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        writer.writerows(questions)


