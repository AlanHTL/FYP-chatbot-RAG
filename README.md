# Mental Health Screening Chatbot

A RAG-based chatbot that uses conversational AI to help screen for potential mental health disorders.

## Features

- Converses naturally with users to gather information about symptoms
- Leverages data from mental_disorders.json as the knowledge base
- Uses the OpenAI API for text generation and embeddings
- Provides preliminary screening insights (not diagnoses)
- Recommends professional evaluation when appropriate

## Setup

1. Make sure you have Python 3.8+ installed

2. Clone this repository and navigate to the project directory

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Make sure your `.env` file contains your API key:
   ```
   API_KEY = 'your-api-key'
   ```

## Usage

Run the chatbot with:
```
python screening_chatbot.py
```

The chatbot will start a conversation in the terminal. You can interact with it by typing your responses. Type 'exit' to end the conversation.

## Important Notes

- This chatbot is for screening purposes only and does not provide diagnoses
- Always consult with a qualified mental health professional for proper evaluation
- The information provided by the chatbot should not be considered medical advice
- Patient privacy and confidentiality should be maintained when using this tool

## Technical Details

- Uses LangChain for the RAG (Retrieval-Augmented Generation) system
- Employs FAISS for efficient vector storage and similarity search
- Relies on OpenAI's gpt-3.5-turbo model for text generation
- Utilizes the text-embedding-ada-002 model for creating embeddings
- Implements conversation memory to maintain context 