import os
import chromadb
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter


# --- Configuration ---
CHROMA_PATH = "chroma_data"
DATA_PATH = "terraform_examples"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def setup_chroma_rag():
    print(f"Loading documents from {DATA_PATH}...")
    # DirectoryLoader finds all files in the directory with extensions .tf and .txt
    # (We are including .txt for the agent_rules.txt file)
    # loader_cls tells the DirectoryLoader which specific LangChain class to instantiate and use to read and parse every file
    loader = DirectoryLoader(DATA_PATH, glob="**/*", loader_cls=TextLoader,silent_errors=True)
    documents = loader.load()

    if not documents:
        print("Error: No Terraform files loaded. Check the 'terraform_examples' folder and file extensions.")
        return

    # Split documents into chunks for RAG
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    
    print(f"Found {len(documents)} documents, split into {len(texts)} chunks.")

    # Initialize the embedding model
    print(f"Initializing embedding model: {EMBEDDING_MODEL_NAME}")
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    # Create the Chroma client (PersistentClient saves data to disk)
    print(f"Creating Chroma client at: {CHROMA_PATH}")
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    collection_name = "terraform_knowledge"
    
    # Create the VectorStore (this performs embedding and storage)
    print("Embedding and storing documents in Chroma...")
    db = Chroma.from_documents(
        texts,
        embedding_function,
        client=chroma_client,
        collection_name=collection_name,
    )

    print("\n--- Setup Complete ---")
    print(f"Vector Database has {db._collection.count()} entries.")
    
    # Simple test to confirm retrieval is working
    print("\nTesting retrieval...")
    query = "How to create an S3 bucket with tags?"
    results = db.similarity_search(query, k=1)
    
    print(f"Retrieved Document Source: {results[0].metadata.get('source')}")
    print("\n--- Retrieved Content ---")
    print(results[0].page_content)


if __name__ == "__main__":
    setup_chroma_rag()