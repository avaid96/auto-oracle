from aihub import AIHub
import os
import uuid
import time
from flask import Flask, request, jsonify, send_file
from urllib.parse import urlparse
from genarate_docs import fill_docx_with_qa
from flask_cors import CORS  # Add this import

app = Flask(__name__)
CORS(app)

client = AIHub(api_root="https://aihub.instabase.com/api", api_key="ncyMgvQkVE0bAJxa7mFs07zUxLMKdW", ib_context="ib-internal")

def parse_questionnaire(doc_path):
    # Create a conversation and upload the document
    conversation = client.conversations.create(
        name='Questionnaire Conversation',
        description='Conversation for parsing questionnaire',
        files=[doc_path]
    )
    # Get the conversation ID
    conversation_id = conversation.id
    
    # Check the status of the conversation
    status = client.conversations.status(conversation_id)
    
    # Wait for the conversation to finish processing
    while status.state == 'RUNNING':
        print("Status: Processing questionairre document...")
        time.sleep(5)
        status = client.conversations.status(conversation_id)
    
    # Check if processing was successful
    if status.state == 'COMPLETE':
        print("Status: Processing complete. Conversation ID = ", conversation_id)
        # Pull in the document ID
        document_id = status.documents[0].id
        
        # Prepare the prompt for querying
        prompt = 'Given the document look for all the questionaire asked in the document. The question can be in any form like a statement, field name or a question itself. Return the  output exactly in a list format ["question 1 text", "question 2 text", etc.]. If no questions are identified, please return exactly an empty list. Preserve the question numbers if given in the document. Do not include any other information in the output.Make sure the output format is a LIST'
        
        # Query the document
        answer = client.conversations.converse(
            conversation_id=conversation_id,
            question=prompt,
            document_ids=[document_id]
        )
        
        #print("Found the following questions", questions)
        #questions = questions.answer.split("\n")
        answer = answer.answer
        print (type(answer))
        answer = answer.strip('```').strip('python')
        answer = answer.strip().strip('json').strip()
        print (answer)
        questions = eval(answer)
        #print(f'questions: {questions}')
        # Parse the answer into a list of questions
        try:
            # questions = eval(answer.answer.split("\n-"))
            if not isinstance(questions, list):
                print("Error: The answer is not a valid list.")
                raise ValueError("Error: The answer is not a valid list.")
        except Exception as e:
           print(f"Error: Failed to parse the answer. {str(e)}")
           raise ValueError(f"Error: Failed to parse the answer. {str(e)}")

        # Return the list of questions
        return questions
    else:
        print("Error: The conversation could not be processed.")
        raise ValueError("Error: The conversation could not be processed.")



def query_knowledge_base(question, chatbot_link):  # Added chatbot_link parameter
    # Extract the chatbot ID from the chatbot_link
    parsed_url = urlparse(chatbot_link)
    chatbot_id = parsed_url.path.split('/')[-1]  # Get the last part of the path as the ID

    # Define the source_app with the chatbot ID
    source = {
        'type': 'CHATBOT',
        'id': chatbot_id  # Use the extracted chatbot ID
    }
    # Send a query to the chatbot
    response = client.queries.run(
        query=question,
        source_app = source,
        model_name = 'multistep-lite',  # Optional: specify the model
        include_source_info=False  # Optional: specify if you want source info
    )
    
    # Get the query ID to check the status
    query_id = response.query_id

    # Check query status until an answer is ready
    status_response = client.queries.status(query_id)
    while status_response.status == 'RUNNING':
        time.sleep(5)  # Wait before checking again
        status_response = client.queries.status(query_id)

    # Parse the chatbot answer
    if status_response.status == 'COMPLETE':
        for result in status_response.results:
            return result.response  # Return the chatbot's answer
    else:
        print(f"Error: {status_response.error}")
        raise ValueError(f"Error: {status_response.error}")  # Handle errors



@app.route('/query', methods=['POST'])
def query_chatbot():
    try:
        data = request.get_json()
        if not data or 'question' not in data or 'chatbot_link' not in data:
            print('Both question and chatbot_link are required')
            return jsonify({'error': 'Both question and chatbot_link are required'}), 400
        
        question = data['question']
        chatbot_link = data['chatbot_link']
        
        answer = query_knowledge_base(question, chatbot_link)
        return jsonify({'answer': answer})
    
    except ValueError as e:
        print(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Create uploads directory if it doesn't exist
    upload_dir = 'uploads'
    os.makedirs(upload_dir, exist_ok=True)

    # Save the file
    filepath = os.path.join(upload_dir, file.filename)
    file.save(filepath)

    return jsonify({'filePath': filepath})


@app.route('/parse', methods=['POST'])
def parse_document():
    try:
        data = request.get_json()
        print (data)
        if not data or 'doc_path' not in data:
            print('doc_path is required')
            return jsonify({'error': 'doc_path is required'}), 400
        
        doc_path = data['doc_path']
        print(f'Parsing document at {doc_path}')
        questions = parse_questionnaire(doc_path)
        return jsonify({'questions': questions})
    
    except ValueError as e:
        print(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/generate', methods=['POST'])
def generate_documents():
    try:
        data = request.get_json()
        print (data)
        # if not data or 'questions' not in data or 'answers' not in data or 'output_filepath' not in data:
        #     print('question, answer and output_filepath is required')
        #     return jsonify({'error': 'question, answer and output_filepath is required'}), 400
        
        doc_name = data['documentName']
        doc_path = f'uploads/{doc_name}'
        qaArray = data['qaArray']
        qa_pairs = []
        for each in qaArray:
            question, ans = each['question'], each['answer']
            qa_pairs.append((question, ans))
        
        #questions = data['questions']
        #answers = data['answers']
        # qa_pairs = list(zip(questions, answers))
        # output_filepath = data['output_filepath']

        #out_path = fill_docx_with_qa(doc_path, qa_pairs)
        time.sleep(5)
        out_path = '/Users/subbu/Projects/hackathon/auto-oracle/api-call-server/uploads/Sample RFP_filled.docx'
        return send_file(
            out_path,  # Path to your generated file
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,  # This prompts download instead of displaying in browser
            download_name='generated-document.docx'  # Name of the downloaded file
        )
    except ValueError as e:
        print(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500



if __name__ == '__main__':
    #app.run(debug=True, port=5000)
   app.run(host="127.0.0.1", port=5001)
   #print (query_knowledge_base('What are the steps to run an AI Hub app from my python code?', 'https://aihub.instabase.com/hub/apps/0686b7fe-c04c-42ea-ab3f-4c940abc1baa'))
   #parse_questionnaire('uploads/Instabase_Ai_Hub_Sample_Queries_v2.pdf')
#    qa_pairs = [
#        ('Is the system SOC2 compliant?', 'Yes, users can delete their data. According to the "Data privacy and security" document, users can choose to delete their content at any time. Additionally, the "Conversing with documents" document explains that users can delete conversations and their conversation history')
#    ]
#    fill_docx_with_qa('/Users/subbu/Projects/hackathon/auto-oracle/api-call-server/uploads/Sample RFP.docx', qa_pairs)