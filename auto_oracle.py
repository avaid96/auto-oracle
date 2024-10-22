import argparse
import os
from questionnaire_parser import parse_questionnaire
from knowledge_base_query import query_knowledge_base
from output_handler import write_to_csv

def main():
    parser = argparse.ArgumentParser(description='Process a questionnaire and query a knowledge base.')
    parser.add_argument('--questionnaire', required=True, help='Path to the questionnaire document')
    parser.add_argument('--chatbot_link', required=True, help='Link to the knowledge base API')
    
    args = parser.parse_args()
    
    # Step 1: Identify questions
    questions = parse_questionnaire(args.questionnaire)
    print(f"Questions identified: {len(questions)}")
    
    # Step 2: Query knowledge base for answers
    answers = []
    for i, question in enumerate(questions):
        print("----")
        print(f"Finding answer for question {i + 1}/{len(questions)}: '{question}'")
        answer = query_knowledge_base(question, args.chatbot_link)
        answers.append(answer)
        print(f"Answer found: '{answer}'")
    
    # Step 3: Write output to CSV in output_docs folder
    output_dir = 'output_docs'
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
    output_file = os.path.join(output_dir, 'output.csv')  # Specify the output file path
    write_to_csv(questions, answers, output_file)  # Pass the output file path to the function
    print(f"Output document generated with {len(answers)} questions answered.")
    
    # Step 4: Automatically open the output document
    try:
        if os.name == 'nt':  # For Windows
            os.startfile(output_file)
        elif os.name == 'posix':  # For macOS and Linux
            os.system(f'open {output_file}')  # macOS
            # os.system(f'xdg-open {output_file}')  # Uncomment for Linux
        print(f"Opened {output_file} automatically.")
    except Exception as e:
        print(f"Failed to open the output document: {e}")

if __name__ == '__main__':
    main()
