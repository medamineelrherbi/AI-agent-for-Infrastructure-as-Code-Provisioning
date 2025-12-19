# 🤖 Terraform AI Orchestrator (KAT-Coder Edition)

An advanced **DevOps AI Agent** designed to bridge the gap between natural language requirements and **Infrastructure as Code (IaC)**. This system leverages a specialized coding LLM, a local RAG (Retrieval-Augmented Generation) system, and a custom execution engine to deploy AWS resources to **LocalStack**.

---

![Architecture Diagram](.\assets\architecture diagram.png)



### 🧩 The Workflow: Simplified

This project follows a "Reasoning-Action" (ReAct) loop orchestrated by **LangChain**:


1. **Orchestration**: **LangChain** manages the flow, connecting the user input to the tools and the AI model.
2. **Reasoning**: The **Kat-Coder Pro** model acts as the brain, planning the infrastructure steps.
3. **Knowledge (RAG)**: **ChromaDB** provides a local memory, ensuring the AI uses your specific HCL templates and rules.
4. **Execution**: The **Terraform Executor** tool writes the code to disk and automates `terraform apply`.
5. **Environment**: **LocalStack** serves as the target "Sandbox," providing a local AWS-compatible API for testing.

---
## 🏗️ System Architecture

The agent operates on a **closed-loop feedback system** using the **ReAct (Reasoning + Acting)** framework. Unlike simple chatbots, this agent "thinks" before it acts and observes the results of its actions to ensure success.



1.  **User Input**: The user provides a high-level infrastructure request.
2.  **RAG Retrieval**: The system queries a **ChromaDB** vector store to find relevant Terraform snippets and organizational rules.
3.  **LLM Reasoning**: The **Kat-Coder** model analyzes the input and retrieved context to decide on the next action.
4.  **Tool Execution**: The agent calls internal Python tools (Knowledge Base, Internet Search, or Terraform Apply).
5.  **Observation**: The output of the tools (e.g., Terraform logs) is fed back to the LLM to confirm success or debug errors.

---

## 🧠 The LLM & Prompt Engineering

### Specialized Model
This project utilizes **`kwaipilot/kat-coder-pro:free`** via OpenRouter. This model is specifically optimized for:
* **HCL (HashiCorp Configuration Language) Syntax**: Deep understanding of Terraform resource structures.
* **Logic Reasoning**: Superior ability to follow complex technical instructions.
* **Low Latency**: Optimized for developer-centric workflows.

### Strict ReAct Prompting
The agent is governed by a custom `PromptTemplate` that enforces strict formatting to prevent parsing errors common in free-tier models:
* **One-at-a-time**: Forces the model to choose exactly one action or a final answer.
* **Format Enforcement**: Uses a custom error handler (`_handle_error`) to catch and correct malformed LLM outputs in real-time.
* **No Hallucination**: Explicitly forbids the LLM from writing Terraform code in the "Thought" section, forcing it to use the `Action Input` field.

---

## 📚 RAG (Retrieval-Augmented Generation)

To ensure the AI generates code compliant with specific local requirements, we implemented a robust **RAG pipeline**:



* **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
* **Data Processing**: Documents from `terraform_examples/` (both `.tf` and `.txt`) are loaded, split into 500-character chunks, and stored.
* **Vector Store**: **ChromaDB** persists the knowledge locally in the `chroma_data/` directory.
* **Knowledge Retrieval**: When requested, the `retriever` pulls the top 2 most relevant chunks to provide the LLM with "few-shot" examples of how your infrastructure should be coded.

---

## 🛠️ The Technical Stack

| Component | Technology |
| :--- | :--- |
| **Orchestration** | LangChain (v0.2 Ecosystem) |
| **LLM** | Kat-Coder Pro (via OpenRouter) |
| **Vector DB** | ChromaDB (Persistent) |
| **Embeddings** | HuggingFace (Sentence Transformers) |
| **Cloud Simulation**| LocalStack (Docker) |
| **IaC Engine** | Terraform CLI + Python Subprocess |


---

## 🔧 Agent Tools & Automation

The agent is equipped with specialized tools to interact with the environment:

1.  **Terraform_Knowledge_Base**: Performs similarity searches on local documentation to provide the LLM with context.
2.  **Internet_Search**: Uses a limited DuckDuckGo wrapper to fetch live documentation or fix provider-specific errors.
3.  **Terraform_Apply (The Executor)**: 
    * **Provider Protection**: Automatically injects a pre-defined **LocalStack provider** (US-East-1, path-style S3, localhost endpoints).
    * **Regex Cleaning**: A safety layer that uses Regular Expressions to strip any "hallucinated" provider blocks from the LLM's output before writing to disk.
    * **Automated Workflow**: Handles the full `terraform init` and `terraform apply -auto-approve` sequence.

---

## 📝 Usage Example & Input

### Example Input
> *"create a bucket named 'dev-storage-bucket' with versioning enabled and a tag 'Project'='Internal'. Do not include a provider block."*

### Internal Agent Flow
1.  **Thought**: I need to consult the knowledge base for S3 versioning examples.
2.  **Action**: `Terraform_Knowledge_Base`
3.  **Action Input**: "S3 bucket versioning HCL example"
4.  **Observation**: (Retrieves text: `versioning { status = "Enabled" }`)
5.  **Action**: `Terraform_Apply`
6.  **Action Input**: `resource "aws_s3_bucket" "b" { bucket = "..." versioning { ... } }`
7.  **Final Answer**: Infrastructure deployed successfully to LocalStack.

---

## ⚙️ Project Structure

* `agent.py`: Main entry point containing the ReAct logic and tool definitions.
* `setup_rag.py`: Script to ingest Terraform examples into ChromaDB.
* `agent_tools/terraform_executor.py`: Python wrapper for the Terraform CLI.
* `terraform_examples/`: Folder containing your `.tf` files and `agent_rules.txt`.
* `Terraform/`: Working directory where `main.tf` is generated and executed.

---

## ⚖️ License
Distributed under the MIT License.