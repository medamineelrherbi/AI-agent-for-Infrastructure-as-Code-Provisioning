import os
from dotenv import load_dotenv
import time

# LangChain & Tools
from langsmith import Client
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool, DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate

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
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

def query_knowledge_base(query: str):
    docs = retriever.invoke(query)
    context = "\n\n".join(d.page_content for d in docs)
    return context


# --- 2. Setup Terraform Tool ---
tf_executor = TerraformExecutor()

# --- 3. Define Tools ---
def limited_ddg_search(query: str):
    search = DuckDuckGoSearchRun()
    results = search.run(query)
    return results[:1500]

tools = [
    Tool(
        name="Terraform_Knowledge_Base",
        func=query_knowledge_base,
        description="Useful for finding Terraform code examples."
    ),
    Tool(
        name="Terraform_Apply",
        func=tf_executor.apply_infrastructure,
        description="""Use this tool to execute Terraform code. 
        INPUT: The input must be ONLY the Terraform Resource/Variable blocks. 
        DO NOT include the 'provider' block.
        DO NOT write code in the 'Thought'. Pass the code entirely to 'Action Input'."""
    ),
    Tool(
        name="Internet_Search",
        func=limited_ddg_search,
        description="Useful for searching the internet for documentation."
    )
]

model_name = "kwaipilot/kat-coder-pro:free"

template = """
You are a Terraform automation agent.

You have access to the following tools:
{tools}

You can ONLY use the following tool names:
{tool_names}

STRICT RULES:
- NEVER output Terraform code outside of Action Input.
- NEVER include provider blocks.
- Use EXACTLY one of the following outputs:
  - Action + Action Input
  - OR Final Answer
- NEVER mix Action and Final Answer in the same response.

Question: {input}
Thought:{agent_scratchpad}
"""



prompt = PromptTemplate.from_template(template)

# --- 5. Initialize LLM ---
llm = ChatOpenAI(
    model=model_name,
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0,
    max_retries=0,
)

agent = create_react_agent(llm, tools, prompt)

# --- 6. CUSTOM ERROR HANDLER ---
# This function fixes the loop by telling the LLM exactly what it did wrong.
def _handle_error(error) -> str:
    return (
        "FORMAT ERROR.\n"
        "You must respond with EITHER:\n"
        "- Action: <tool>\n  Action Input: <input>\n"
        "OR:\n"
        "- Final Answer: <text>\n"
        "Do not include Terraform code outside Action Input."
    )

def load_requirements():
    try:
        with open("terraform_examples/agent_rules.txt", "r") as f:
            return f.read()
    except Exception:
        return ""

core_requirements = load_requirements()
static_history_text = f"System: CORE INSTRUCTIONS: {core_requirements}\nAI: Understood."

# --- 7. Agent Executor with Error Handling ---
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    # This prevents the crash and allows the agent to self-correct
    handle_parsing_errors=_handle_error, 
)

if __name__ == "__main__":
    print("Terraform AI Agent is ready. Type 'exit' to quit.")

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in {"exit", "quit"}:
            break
        
        # CORRECTION : Tout ce bloc doit être indenté
        try:
            # On vérifie que l'utilisateur n'a pas juste appuyé sur Entrée
            if user_input.strip(): 
                response = agent_executor.invoke({"input": user_input})
                print(f"\nAgent: {response['output']}")
                time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")