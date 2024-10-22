import csv

def write_to_csv(questions, answers, output_file='output.csv'):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Question', 'Answer'])
        for question, answer in zip(questions, answers):
            writer.writerow([question, answer])