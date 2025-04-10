import requests
import json
import sys
import os

# Default API URL, can be overridden by environment variable
DEFAULT_API_URL = os.getenv("CHATBOT_API_URL", "http://127.0.0.1:8080/chat")

def chat(message: str, api_url: str = DEFAULT_API_URL) -> str | None:
    """
    Sends a message to the chatbot API server and returns the reply.

    Args:
        message: The message string to send to the chatbot.
        api_url: The URL of the chatbot API server's /chat endpoint.

    Returns:
        The chatbot's reply as a string, or None if an error occurred.
    """
    headers = {'Content-Type': 'application/json'}
    payload = {'message': message}

    try:
        print(f"Sending message to {api_url}...")
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        print("Received response.")
        response_data = response.json()
        
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
    print("Starting chat client...")
    print("Enter your message below (or type 'quit' to exit).")

    while True:
        try:
            user_input = input("You: ") 
            if user_input.lower() == 'quit':
                break
            
            if not user_input:
                continue

            reply = chat(user_input)

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