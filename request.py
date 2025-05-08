import requests
import json
import sys
import os
import uuid # Import uuid to generate unique IDs
from dotenv import load_dotenv
load_dotenv()
# Default API URL, can be overridden by environment variable
DEFAULT_API_URL = os.getenv("CHATBOT_API_URL", "http://localhost:8080/chat")

def chat(message: str, conversation_id: str, api_url: str = DEFAULT_API_URL) -> str | None:
    """
    Sends a message to the chatbot API server and returns the reply.

    Args:
        message: The message string to send to the chatbot.
        conversation_id: The unique ID for the current conversation.
        api_url: The URL of the chatbot API server's /chat endpoint.

    Returns:
        The chatbot's reply as a string, or None if an error occurred.
    """
    headers = {'Content-Type': 'application/json'}
    # Include conversation_id in the payload
    payload = {
        'message': message,
        'conversation_id': conversation_id 
    }

    try:
        print(f"Sending message to {api_url} (Conv ID: {conversation_id})...")
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        print("Received response.")
        response_data = response.json()
        
        # The API now returns conversation_id, but we mainly need the reply here
        if "reply" in response_data:
            return response_data['reply']
        else:
            print(f"Error: 'reply' key not found in response: {response_data}")
            return None

    except requests.exceptions.ConnectionError as e:
        print(f"Error: Could not connect to the API server at {api_url}. Is it running?")
        print(f"Details: {e}")
        return None
    except requests.exceptions.Timeout as e:
        print(f"Error: Request timed out connecting to {api_url}.")
        print(f"Details: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error occurred: {e.response.status_code} {e.response.reason}")
        try:
            # Try to get more specific error from the server response
            error_details = e.response.json()
            print(f"Server error details: {error_details}")
        except json.JSONDecodeError:
            print(f"Server response content: {e.response.text}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON response from server.")
        print(f"Response text: {response.text}")
        print(f"Details: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred during the API request: {e}")
        return None


if __name__ == "__main__":
    # Generate a unique conversation ID for this chat session
    current_conversation_id = str(uuid.uuid4())
    print(f"Starting chat client (Conversation ID: {current_conversation_id})...")
    print("Enter your message below (or type 'quit' to exit).")
    print("Bot: Hi, I am Dr. Mind, a mental health screening specialist. May I have your name, please?")
    while True:
        try:
            user_input = input("You: ") 
            if user_input.lower() == 'quit':
                break
            
            if not user_input:
                continue

            # Pass the conversation ID to the chat function
            reply = chat(user_input, current_conversation_id)

            if reply:
                print(f"Bot: {reply}")
            else:
                print("Failed to get a reply from the bot.")
                # Optionally break or wait before retrying
                # break 

        except KeyboardInterrupt:
            print("\nExiting chat client.")
            break
        except EOFError: # Handle Ctrl+D
            print("\nExiting chat client.")
            break

    print("Chat client finished.") 