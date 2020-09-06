import csv


def read_csv(file_name):
    data = []
    with open(file_name) as file:
        reader = csv.DictReader(file)

        for question in reader:
            data.append(question)

    return data


def write_csv(file_name, data, field_names):
    with open(file_name, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()

        writer.writerows(data)

