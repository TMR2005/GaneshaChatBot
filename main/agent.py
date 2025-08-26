# This file should be located at: main/agent.py
from gpt4all import GPT4All
import os
import re # ADDED: Import the regular expression library
from dotenv import load_dotenv
from .prompt import prompt
from pydantic import BaseModel
from typing import Optional

# --- RAG Imports for ChromaDB and LangChain ---
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# --- Load environment variables and set up model path ---
load_dotenv()
model_path = os.getenv("MODEL_PATH")
if not model_path:
    # IMPORTANT: Update this path to where your model is actually located
    model_path = r"C:\Users\Admin\AppData\Local\nomic.ai\GPT4All\Meta-Llama-3-8B-Instruct.Q4_0.gguf"

# --- RAG Setup: Load the Vector Database ---
DB_DIR = os.path.join(PROJECT_ROOT, "chroma_db")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

print("RAG Agent: Initializing embeddings...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

print(f"RAG Agent: Loading vector database from {DB_DIR}...")
vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
print("RAG Agent: Database loaded successfully.")

# --- Initialize the language model ---
try:
    print(f"Loading LLM from: {model_path}")
    # --- THE FIX: Changed device="cpu" to "gpu" to use your NVIDIA card ---
    model = GPT4All(model_path, device="gpu", allow_download=False)
    print("LLM loaded successfully onto GPU.")
except Exception as e:
    print(f"Error loading model file: {model_path}\nDetails: {e}")
    model = None

# --- Define the response structure using Pydantic ---
class GaneshResponse(BaseModel):
    lang: str
    blessing_open: str
    answer: str
    blessing_close: str
    refusal: bool = False
    refusal_reason: Optional[str] = ""

    def to_dict(self):
        """Converts the Pydantic model to a JSON-serializable dictionary."""
        return self.model_dump()

# --- Main function to get the RAG-powered response ---
def get_ganesh_response(user_input: str) -> GaneshResponse:
    if model is None:
        return GaneshResponse(
            lang='en', blessing_open='',
            answer='I apologize, my connection to the divine consciousness is currently unavailable. Please try again later.',
            blessing_close='', refusal=True, refusal_reason='LLM model not loaded'
        )
        
    print(f"Agent received text: '{user_input}'")

    # --- RAG WORKFLOW ---
    # 1. Retrieve relevant documents and their scores from ChromaDB
    print("RAG Step 1: Retrieving context from database...")
    
    # MODIFIED: Use similarity_search_with_score to get debug info
    results_with_scores = vector_db.similarity_search_with_score(user_input, k=4)
    
    # NEW: Print the scores and sources for live debugging
    print("\n--- RAG Retrieval Results ---")
    if not results_with_scores:
        print("No relevant documents found.")
    else:
        for doc, score in results_with_scores:
            source = doc.metadata.get('source', 'Unknown')
            print(f"Score: {score:.4f} | Source: {os.path.basename(source)}")
    print("---------------------------\n")

    # Extract just the documents to build the context
    relevant_docs = [doc for doc, score in results_with_scores]
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    print(f"RAG Step 1: Found {len(relevant_docs)} relevant document chunks.")
    
    # 2. Augment the prompt with the retrieved context
    final_prompt = prompt.format(context=context, question=user_input)
    print("RAG Step 2: Augmented prompt created.")
    
    # 3. Generate the response using the full RAG prompt
    print("RAG Step 3: Generating response from LLM...")
    with model.chat_session():
        raw_response_text = model.generate(final_prompt, max_tokens=700)
        
    print(f"Raw LLM Output:\n{raw_response_text}")
    
    # 4. Parse the LLM's JSON output
    try:
        json_start = raw_response_text.find('{')
        json_end = raw_response_text.rfind('}') + 1
        
        if json_start != -1 and json_end != 0:
            json_string = raw_response_text[json_start:json_end]
            
            # --- THE FIX ---
            # Remove any invisible control characters (like \n, \r, \t) from the string
            sanitized_json_string = re.sub(r'[\x00-\x1f]', '', json_string)
            
            # Parse the cleaned string
            parsed_data = GaneshResponse.model_validate_json(sanitized_json_string)
        else:
            raise ValueError("No JSON object found in the LLM response.")
            
    except Exception as e:
        print(f"Failed to parse LLM response. Error: {e}")
        parsed_data = GaneshResponse(
            lang='en', blessing_open='',
            answer="I heard your words, but my thoughts are unclear at this moment. Please rephrase your question, and I shall try again to offer guidance.",
            blessing_close='', refusal=True, refusal_reason='LLM output was not valid JSON or could not be parsed'
        )
    
    return parsed_data
