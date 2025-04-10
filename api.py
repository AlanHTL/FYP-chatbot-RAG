import os
import asyncio
import json
from aiohttp import web
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

def configure_openai():
    """Configure OpenAI settings, prioritizing standard environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Fallback to user's variable name if standard one isn't set
        api_key_custom = os.getenv("API_KEY")
        if not api_key_custom:
            print("Neither OPENAI_API_KEY nor API_KEY found in environment.")
            api_key_custom = input("Please enter your OpenAI API key: ")
        
        if api_key_custom:
            os.environ["OPENAI_API_KEY"] = api_key_custom
            api_key = api_key_custom # Use the key that was set

    # Use OPENAI_API_BASE if set, otherwise default to the user's provided URL
    base_url = os.getenv("OPENAI_API_BASE", "https://xiaoai.plus/v1")
    os.environ["OPENAI_API_BASE"] = base_url

    # Verify settings
    print(f"Using OpenAI API Base: {os.environ.get('OPENAI_API_BASE')}")
    if not os.environ.get("OPENAI_API_KEY"):
         print("Warning: OPENAI_API_KEY could not be configured.")
    else:
        # Optionally mask the key partially if printing
        # print(f"Using OpenAI API Key: {...}") 
        print("OpenAI API Key is configured.")


# Configure OpenAI settings on script start
configure_openai()

# --- Langchain Chat Model Initialization ---
chat_model = None
try:
    # Ensure API key is available before initializing
    if "OPENAI_API_KEY" not in os.environ or not os.environ["OPENAI_API_KEY"]:
        raise ValueError("OPENAI_API_KEY is missing or empty. Cannot initialize ChatOpenAI.")

    chat_model = ChatOpenAI(
        model="gpt-3.5-turbo",
        # Langchain automatically picks up OPENAI_API_KEY and OPENAI_API_BASE from env vars
        # openai_api_key=os.environ.get("OPENAI_API_KEY"), # Explicit pass usually not needed
        # openai_api_base=os.environ.get("OPENAI_API_BASE") # Explicit pass usually not needed
        temperature=0.7 # Example: Set creativity level
    )
    print("ChatOpenAI model initialized successfully.")
except Exception as e:
    print(f"Error initializing ChatOpenAI model: {e}")
    # Consider exiting if the chat model is essential and failed to load
    # sys.exit(f"Fatal Error: Could not initialize chat model - {e}")


# --- API Request Handler ---
async def handle_chat(request):
    """Handles incoming chat requests concurrently."""
    if chat_model is None:
        print("Error: Chat model is not available.")
        return web.json_response({"error": "Chat model not initialized or failed to load"}, status=500)

    try:
        # Ensure request body is valid JSON
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON format in request body"}, status=400)

        user_message = data.get("message")
        if not user_message or not isinstance(user_message, str):
            return web.json_response({"error": "Missing or invalid 'message' string in request body"}, status=400)

        # Prepare messages for Langchain
        messages = [
            SystemMessage(content="You are a helpful AI assistant."),
            HumanMessage(content=user_message),
        ]

        # Use ainvoke for asynchronous call to the language model
        print(f"Invoking chat model for input: '{user_message[:50]}...'") # Log reception
        response = await chat_model.ainvoke(messages)
        print("Chat model invocation successful.") # Log success

        # Return the response from the chatbot
        return web.json_response({"reply": response.content})

    except Exception as e:
        # Log the full error for debugging on the server side
        import traceback
        print(f"Error processing chat request: {e}
{traceback.format_exc()}")
        return web.json_response({"error": f"An internal server error occurred."}, status=500)


# --- Server Setup ---
def setup_server():
    """Creates and configures the aiohttp application."""
    app = web.Application()
    app.router.add_post('/chat', handle_chat)
    print("'/chat' route (POST) added.")
    return app

# --- Main Execution Block ---
if __name__ == '__main__':
    host = os.getenv("API_HOST", "127.0.0.1") # Default to localhost
    port = int(os.getenv("API_PORT", 8080))   # Default to port 8080
    
    app = setup_server()

    print(f"Starting API server on http://{host}:{port}")
    try:
        web.run_app(app, host=host, port=port)
    except Exception as e:
        print(f"Failed to start server: {e}") 