import os
from dotenv import load_dotenv
import time
# LangChain & Tools
from langsmith import Client
 #from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.tools import Tool, DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Internal Modules
from agent_tools.terraform_executor import TerraformExecutor

# Load API Keys 
load_dotenv()

# --- 1. Setup RAG Retrieval ---
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_PATH = "chroma_data"

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
vectorstore = Chroma(
    persist_directory=CHROMA_PATH, 
    embedding_function=embeddings,
    collection_name="terraform_knowledge"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

def query_knowledge_base(query: str):
    """Consults the local RAG database for Terraform examples and rules."""
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([d.page_content for d in docs])
    return context

# --- 2. Setup Terraform Tool ---
tf_executor = TerraformExecutor()

# --- 3. Define Tools ---
def limited_ddg_search(query: str):
    search = DuckDuckGoSearchRun()
    results = search.run(query)
    # On ne garde que les 1500 premiers caractères pour économiser les tokens
    return results[:1500]

tools = [
    Tool(
        name="Terraform_Knowledge_Base",
        func=query_knowledge_base,
        description="Useful for finding Terraform code examples and AWS best practices from local files."
    ),
    Tool(
        name="Terraform_Apply",
        func=tf_executor.apply_infrastructure,
        description="Use this to actually create or update infrastructure. Input must be valid Terraform HCL code."
    ),
    Tool(
        name="Internet_Search",
        func=limited_ddg_search,
        description="Useful for searching the internet for updated documentation, fixing Terraform errors, or finding new AWS features."
        )
]
model_name = "meta-llama/llama-3.3-70b-instruct:free"
# --- 4. Initialize LLM & Agent ---
llm = ChatOpenAI(
    model=model_name,
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0,
    max_retries=0
)

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
# Get the prompt template from LangChain Hub
prompt = client.pull_prompt("hwchase17/structured-chat-agent")

# Create the Agent
agent = create_structured_chat_agent(llm, tools, prompt)

# Create the Executor
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True
)

# --- 5. Execution Loop ---
# --- 5. Execution Loop ---
if __name__ == "__main__":
    print("AI Infrastructure Agent is ready. (Type 'exit' to quit)")
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        try:
            # Run the agent
            response = agent_executor.invoke({"input": user_input})
            print(f"\nAgent: {response['output']}")
            
            # --- CRITICAL FIX FOR FREE TIER ---
            # Wait 10 seconds after every request to let the Quota cool down
            print("\n(Cooling down API quota for 5 seconds...)")
            time.sleep(5) 
            # ----------------------------------

        except Exception as e:
            print(f"Error: {e}")
            print("You hit the rate limit. Please wait 1 minute before trying again.")