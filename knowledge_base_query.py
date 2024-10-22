# Importing necessary library
from aihub import AIHub  # Added import for AIHub
import os  # Added import for os
from dotenv import load_dotenv  # Added import for load_dotenv
import time  # Added import for time
from urllib.parse import urlparse  # Added import for URL parsing

# Load environment variables from .env file
load_dotenv()  # Added to load environment variables

# Initialize the API client with the API key from .env
client = AIHub(api_key=os.getenv("API_KEY"), api_root="https://aihub.instabase.com/api", ib_context=os.getenv("IB-CONTEXT"))  # Added client initialization

def query_knowledge_base(question, chatbot_link):  # Added chatbot_link parameter
    # Extract the chatbot ID from the chatbot_link
    parsed_url = urlparse(chatbot_link)
    chatbot_id = parsed_url.path.split('/')[-1]  # Get the last part of the path as the ID

    # Define the source_app with the chatbot ID
    source_app = {
        'type': 'CHATBOT',
        'id': chatbot_id  # Use the extracted chatbot ID
    }

    # Send a query to the chatbot
    response = client.queries.run(
        query=question,
        source_app=source_app,
        model_name='multistep-lite',  # Optional: specify the model
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
        raise ValueError(f"Error: {status_response.error}")  # Handle errors
