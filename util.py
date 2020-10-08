import re
import time


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


def mark(msg):
    return f'<span style="background-color: yellow;">{msg}</span>'


def format_search_results(message, quoted_phrases):
    output = ""

    indexes_dict = {}

    for phrase in quoted_phrases:
        start = 0

        while phrase.lower() in message[start:].lower():
            index = message[start:].lower().index(phrase.lower())
            start += index + 1
            indexes_dict[start - 1] = phrase

    # Sorted indexes of found phrases
    indexes = [f[0] for f in sorted(indexes_dict.items(), key=lambda x: x[0])]

    # Found phrases sorted by indexes (phrases are positioned in the list according to
    # their occurrence in the message)
    quoted_phrases = [f[1] for f in sorted(indexes_dict.items(), key=lambda x: x[0])]

    prev_index = 0
    for index, index_val in enumerate(indexes):
        if index_val > prev_index:
            to = index_val + len(quoted_phrases[index])

            output += message[prev_index:index_val]

            output += mark(message[index_val:to])
            prev_index += index_val + len(quoted_phrases[index])
        else:
            to = index_val + len(quoted_phrases[index])
            output += mark(message[0:to])
            prev_index = len(quoted_phrases[index])

    if prev_index < len(message):
        output += message[prev_index:]

    if len(output) == 0:
        output = message

    return output


# msg = "How to make lists in Python?"
# query = ["Python"]
# print(format_search_results(msg, query))
