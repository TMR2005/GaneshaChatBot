from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# --- Configuration (should match your agent.py) ---
DB_DIR = "chroma_db"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def debug_retrieval(query: str):
    """Loads the database and performs a similarity search with scores."""
    print("--- Initializing and loading database for test ---")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    
    print(f"\nSearching for: '{query}'\n")
    
    # Use similarity_search_with_score to see the distance score
    # A LOWER score is BETTER (it means the vectors are closer)
    results_with_scores = vector_db.similarity_search_with_score(query, k=4)
    
    if not results_with_scores:
        print("!!! RETRIEVAL FAILED: No documents found. !!!")
        return

    for i, (doc, score) in enumerate(results_with_scores):
        print(f"--- Result {i+1} | Score: {score:.4f} ---")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Content: {doc.page_content}\n")

if __name__ == "__main__":
    # Test with a few different phrasings
    debug_retrieval("how did you win against your brother")
    # debug_retrieval("story of the Mahabharata")