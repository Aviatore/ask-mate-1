def sort_questions(by, questions, direction='asc'):
    rev = True if direction == 'desc' else False

    if by == 'submission_time':
        return sorted(questions, key=lambda x: x['submission_time'], reverse=rev)
    elif by == 'title':
        return sorted(questions, key=lambda x: x['title'], reverse=rev)
    elif by == 'message':
        return sorted(questions, key=lambda x: x['message'], reverse=rev)
    elif by == 'view_number':
        return sorted(questions, key=lambda x: x['view_number'], reverse=rev)
    elif by == 'vote_number':
        return sorted(questions, key=lambda x: x['vote_number'], reverse=rev)
