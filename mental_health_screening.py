import os
import json
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_api_key():
    """Get API key from environment variable or prompt user."""
    api_key = os.getenv("API_KEY")
    if not api_key:
        api_key = input("Please enter your API key: ")
        os.environ["API_KEY"] = api_key
    return api_key

def configure_openai():
    """Configure OpenAI settings."""
    api_key = 'sk-UnNXXoNG6qqa1RUl24zKrakQaHBeyxqkxEtaVwGbSrGlRQxl'
    base_url = "https://xiaoai.plus/v1"
    
    # Configure OpenAI
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_API_BASE"] = base_url

class MentalHealthScreener:
    def __init__(self):
        try:
            # Load the mental disorders database
            with open('mental_disorders.json', 'r') as f:
                self.disorders_data = json.load(f)
            
            # Prepare documents for vector store
            self.documents = self._prepare_documents()
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            
            # Split documents into chunks
            self.splits = self.text_splitter.split_documents(self.documents)
            
            # Initialize embeddings and vector store
            self.embeddings = OpenAIEmbeddings()
            self.vectorstore = FAISS.from_documents(self.splits, self.embeddings)
            
            # Initialize conversation memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Initialize the LLM
            self.llm = ChatOpenAI(
                temperature=0.7,
                model_name="gpt-3.5-turbo"
            )
            
            # Create custom prompt template
            self.prompt_template = PromptTemplate(
                input_variables=["context", "question", "chat_history"],
                template="""You are a mental health screening assistant. Use the following pieces of context to answer the question at the end. 
                If you don't know the answer, just say that you don't know, don't try to make up an answer.
                
                Context: {context}
                
                Chat History: {chat_history}
                
                Question: {question}
                
                Answer: Let me help you with that. Based on the diagnostic criteria and your description, I can provide some information about potential mental health concerns. However, please note that this is not a diagnosis - only a qualified mental health professional can provide a proper diagnosis.
                """
            )
            
            # Initialize the conversation chain
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vectorstore.as_retriever(),
                memory=self.memory,
                combine_docs_chain_kwargs={"prompt": self.prompt_template}
            )
        except Exception as e:
            print(f"Error initializing the screener: {str(e)}")
            raise

    def _prepare_documents(self) -> List[Document]:
        """Convert the mental disorders data into a format suitable for the vector store."""
        documents = []
        for disorder in self.disorders_data["mental_disorders"]:
            # Create a text representation of each disorder
            content = f"Disorder: {disorder['name']}\n"
            content += "Diagnostic Criteria:\n"
            
            # Add each criterion
            for criterion_key, criterion_value in disorder["diagnostic_criteria"].items():
                if isinstance(criterion_value, dict):
                    content += f"{criterion_key}. {criterion_value.get('description', '')}\n"
                    if "symptoms" in criterion_value:
                        content += "Symptoms:\n"
                        for symptom in criterion_value["symptoms"]:
                            content += f"- {symptom}\n"
                    if "criteria" in criterion_value:
                        content += "Criteria:\n"
                        for c in criterion_value["criteria"]:
                            content += f"- {c}\n"
                else:
                    content += f"{criterion_key}. {criterion_value}\n"
            
            # Create a Document object
            doc = Document(
                page_content=content,
                metadata={"disorder": disorder["name"]}
            )
            documents.append(doc)
        
        return documents

    def screen(self, user_input: str) -> str:
        """Process user input and return a screening response."""
        try:
            response = self.qa_chain({"question": user_input})
            return response["answer"]
        except Exception as e:
            return f"An error occurred during screening: {str(e)}"

def main():
    try:
        # Configure OpenAI settings
        configure_openai()
        
        # Initialize the screener
        print("Initializing the Mental Health Screening Assistant...")
        screener = MentalHealthScreener()
        
        print("\nWelcome to the Mental Health Screening Assistant")
        print("Please describe your symptoms or concerns. Type 'quit' to exit.")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'quit':
                break
                
            response = screener.screen(user_input)
            print("\nAssistant:", response)
            
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Please make sure you have:")
        print("1. A valid API key")
        print("2. The mental_disorders.json file in the same directory")
        print("3. All required dependencies installed")

if __name__ == "__main__":
    main() 