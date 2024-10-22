# Importing necessary libraries
from aihub import AIHub
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the API client with the API key from .env
client = AIHub(api_key=os.getenv("API_KEY"), api_root="https://aihub.instabase.com/api", ib_context=os.getenv("IB-CONTEXT"))

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
        prompt = 'Identify upto 10 questions in this questionnaire document and output exactly in a list format ["question 1 text", "question 2 text", etc.]. If no questions are identified, please return exactly an empty list ```[]```'
        
        # Query the document
        answer = client.conversations.converse(
            conversation_id=conversation_id,
            question=prompt,
            document_ids=[document_id]
        )
        
        print("Found the following questions", answer)

        # Parse the answer into a list of questions
        try:
            questions = eval(answer.answer)
            if not isinstance(questions, list):
                raise ValueError("Error: The answer is not a valid list.")
        except Exception as e:
            raise ValueError(f"Error: Failed to parse the answer. {str(e)}")

        # Return the list of questions
        return questions
    else:
        raise ValueError("Error: The conversation could not be processed.")
