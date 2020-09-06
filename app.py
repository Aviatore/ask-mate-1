from flask import Flask, render_template

app = Flask(__name__)
headers = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
questions = [
    {
        'id': 1,
        'submission': 1493368154,
        'view_number': 29,
        'vote_number': 7,
        'title': "How to make lists in Python?",
        'message': "I am totally new to this, any hints?",
        'image': ''
    }
]


@app.route('/list')
def list():
    return render_template('list.html', headers=headers, questions=questions)




if __name__ == '__main__':
    app.run()
