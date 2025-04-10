import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain.schema import Document, HumanMessage, AIMessage, SystemMessage
from langchain.chains import ConversationChain
from typing import List, Dict, Tuple, Optional

# Load environment variables
load_dotenv()

# Global debug flag
DEBUG_RETRIEVAL = True
VECTOR_STORE_PATH = "faiss_index"

def configure_openai():
    """Configure OpenAI settings."""
    api_key = os.getenv("API_KEY")
    if not api_key:
        api_key = input("Please enter your API key: ")
        os.environ["API_KEY"] = api_key
    
    base_url = "https://xiaoai.plus/v1"
    
    # Configure OpenAI
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_API_BASE"] = base_url

# Load mental disorders data
def load_mental_disorders():
    with open("mental_disorders.json", "r") as f:
        data = json.load(f)
    return data["mental_disorders"]

def format_criterion(criterion_key: str, criterion_value: Dict) -> str:
    """Format a single criterion into a string."""
    if isinstance(criterion_value, dict):
        result = f"{criterion_key}. {criterion_value.get('description', '')}\n"
        if "symptoms" in criterion_value:
            result += "Symptoms:\n"
            for symptom in criterion_value["symptoms"]:
                result += f"- {symptom}\n"
        if "criteria" in criterion_value:
            result += "Criteria:\n"
            for c in criterion_value["criteria"]:
                result += f"- {c}\n"
        return result
    else:
        return f"{criterion_key}. {criterion_value}\n"

def format_disorder_info(doc: Document) -> Dict:
    """Format disorder information into a structured dictionary."""
    content = doc.page_content
    metadata = doc.metadata
    
    # Extract disorder name
    disorder_name = metadata.get('disorder', 'Unknown Disorder')
    
    # Parse diagnostic criteria
    criteria = {}
    current_criterion = None
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith(('A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.', 'H.', 'I.', 'J.')):
            current_criterion = line[0]
            criteria[current_criterion] = line[2:].strip()
        elif line.startswith('Symptoms:'):
            if current_criterion and isinstance(criteria[current_criterion], str):
                criteria[current_criterion] = {
                    'description': criteria[current_criterion],
                    'symptoms': []
                }
        elif line.startswith('- ') and current_criterion and isinstance(criteria[current_criterion], dict):
            criteria[current_criterion]['symptoms'].append(line[2:].strip())
    
    return {
        'name': disorder_name,
        'diagnostic_criteria': criteria
    }

# Process mental disorders data into documents
def create_documents(disorders) -> List[Document]:
    documents = []
    for disorder in disorders:
        # Create a complete text representation of each disorder
        content = f"Disorder: {disorder['name']}\n"
        content += "Diagnostic Criteria:\n"
        
        # Add each criterion
        for criterion_key, criterion_value in disorder["diagnostic_criteria"].items():
            content += format_criterion(criterion_key, criterion_value)
        
        # Create a Document object with the complete disorder information
        doc = Document(
            page_content=content,
            metadata={
                "disorder": disorder["name"],
                "complete_criteria": json.dumps(disorder["diagnostic_criteria"])
            }
        )
        documents.append(doc)
    
    return documents

def print_retrieved_documents(docs):
    """Print retrieved documents in a readable format"""
    if not docs:
        print("\n--- No Relevant Documents Found ---\n")
        return
        
    print("\n--- Retrieved Documents ---")
    for i, doc in enumerate(docs):
        print(f"\nDocument {i+1}: {doc.metadata.get('disorder', 'Unknown')}")
        # Print a shorter version of the content to keep output manageable
        content = doc.page_content
        if len(content) > 300:
            content = content[:300] + "... [truncated]"
        print(f"Content: {content}")
    print("-------------------------\n")

def load_or_create_vectorstore() -> Tuple[FAISS, bool]:
    """Load existing vectorstore or create a new one if it doesn't exist."""
    embeddings = OpenAIEmbeddings()
    
    # Check if the vectorstore exists
    if os.path.exists(VECTOR_STORE_PATH):
        try:
            print("Debug: Loading existing vector store...")
            vectorstore = FAISS.load_local(VECTOR_STORE_PATH, embeddings)
            print(f"Debug: Vector store loaded successfully from {VECTOR_STORE_PATH}")
            return vectorstore, False
        except Exception as e:
            print(f"Debug: Error loading vector store: {str(e)}")
            print("Debug: Will create a new vector store...")
    
    # Create a new vectorstore
    print("\nDebug: Loading disorders data...")
    disorders = load_mental_disorders()
    
    print("Debug: Creating documents...")
    documents = create_documents(disorders)
    
    print("Debug: Creating vector store...")
    # Initialize text splitter with larger chunk size to keep criteria together
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,  # Increased chunk size
        chunk_overlap=400,  # Increased overlap
        length_function=len,
    )
    
    # Split documents into chunks
    splits = text_splitter.split_documents(documents)
    print(f"Debug: Created {len(splits)} text chunks")
    
    # Initialize vector store
    vectorstore = FAISS.from_documents(splits, embeddings)
    print("Debug: FAISS index created successfully")
    
    # Save the vectorstore
    print(f"Debug: Saving vector store to {VECTOR_STORE_PATH}...")
    vectorstore.save_local(VECTOR_STORE_PATH)
    print("Debug: Vector store saved successfully")
    
    return vectorstore, True

def create_agent(llm: ChatOpenAI, tools: List[Tool]) -> AgentExecutor:
    """Create an agent with the given language model and tools."""
    template = """You are a mental health screening assistant. Your role is to help gather information about potential mental health concerns and provide relevant information based on the DSM-5 criteria. You cannot provide diagnoses, but you can discuss symptoms and suggest seeking professional help when appropriate.

Remember to:
1. Be empathetic and professional
2. Ask relevant follow-up questions
3. Use the search tool to find accurate information
4. Maintain confidentiality
5. Clearly state that you cannot provide diagnoses

Available tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}"""

    prompt = PromptTemplate(
        template=template,
        input_variables=["tools", "tool_names", "input", "agent_scratchpad"]
    )

    memory = ConversationBufferMemory(memory_key="chat_history")
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )

def create_conversation(llm: ChatOpenAI, vectorstore: FAISS) -> AgentExecutor:
    """Create a conversation chain with the chatbot."""
    print("Debug: Creating search tool")
    search_tool = create_search_tool(vectorstore)
    tools = [search_tool]
    
    print("Debug: Creating agent")
    agent_executor = create_agent(llm, tools)
    print("Debug: Agent created successfully")
    
    return agent_executor

def create_search_tool(vectorstore: FAISS) -> Tool:
    """Create a search tool for the vector store."""
    def search_documents(query: str) -> str:
        """Search the vector store for relevant documents."""
        docs = vectorstore.similarity_search(query, k=3)
        return "\n".join([doc.page_content for doc in docs])
    
    return Tool(
        name="Search Mental Health Information",
        func=search_documents,
        description="Search for information about mental health conditions, symptoms, and diagnostic criteria."
    )

def main():
    """Main function to run the mental health screening chatbot."""
    try:
        configure_openai()
        print("Debug: OpenAI settings configured")
        
        print("Debug: Creating chatbot...")
        disorders = load_mental_disorders()
        print("Debug: Mental disorders data loaded")
        
        documents = create_documents(disorders)
        print("Debug: Documents created from disorders data")
        
        embeddings = OpenAIEmbeddings()
        print("Debug: Embeddings initialized")
        
        vectorstore = FAISS.from_documents(documents, embeddings)
        print("Debug: FAISS index created successfully")
        
        llm = ChatOpenAI(temperature=0.7)
        conversation = create_conversation(llm, vectorstore)
        
        print("\nWelcome to the Mental Health Screening Assistant.")
        print("I'm here to help you discuss mental health concerns and provide information.")
        print("Please note that I cannot provide diagnoses. For professional help, please consult a qualified mental health professional.")
        print("\nHow are you feeling today?\n")
        
        while True:
            user_input = input("You: ").strip()
            if not user_input:
                print("Please enter a message. Type 'quit' to exit.")
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nThank you for talking with me. Take care!")
                break
            
            try:
                response = conversation.run(user_input)
                print("\nAssistant:", response.strip(), "\n")
            except Exception as e:
                print(f"An error occurred while processing your message: {str(e)}")
                print("Please try rephrasing your message or ask a different question.")
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
