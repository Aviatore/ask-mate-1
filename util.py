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


def parse_search_phrase(search_phrase):
    # Get a list of indexes of double quotes
    indexes = [index for index, value in enumerate(search_phrase) if value == '"']

    quoted = []
    unquoted = []

    # If the list contains odd number of indexes, remove the last one
    if len(indexes) % 2 != 0:
        indexes = indexes[0:-1]

    # Get a list of tuples of index pairs, e.g. [(1,7), (12,23)]
    prev_start = 0
    for start, stop in zip(*[iter(indexes)] * 2):
        quoted.append(search_phrase[start + 1:stop])

        if start > prev_start:
            unquoted.append(search_phrase[prev_start:start])

        prev_start = stop + 1

    if len(search_phrase) > prev_start:
        unquoted.append(search_phrase[prev_start:])

    # Split unquoted phrase by spaces
    unquoted_single_words = []
    for phrase in unquoted:  # e.g. ['hej  ho'] - string contains double spaces
        words = [i.strip() for i in phrase.split(' ')]  # e.g. ['hej', '', 'ho']
        words_no_blanks = [i for i in words if i != '']  # e.g. ['hej', 'ho']
        unquoted_single_words.extend(words_no_blanks)

    return quoted, unquoted_single_words


def create_regex(quoted, unquoted):
    regex_phrase = ''

    for word in quoted:
        regex_phrase += '()'