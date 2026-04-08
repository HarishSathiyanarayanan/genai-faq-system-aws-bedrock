# 🚀 GenAI FAQ System using AWS Bedrock

## 📌 Overview

This project demonstrates a **GenAI-powered FAQ system** built using AWS Bedrock.
It intelligently routes user queries between:

* 🔧 **Tool Calling (Lambda)** → for structured responses (refund, shipping)
* 📚 **RAG (Retrieval-Augmented Generation)** → for knowledge-based answers
* 🛡️ **Guardrails** → for safety and harmful content filtering

---

## 🧠 Key Features

* ✅ LLM-based intelligent routing (TOOL / RAG / UNSAFE)
* ✅ AWS Lambda-based tool execution
* ✅ Simple RAG system for contextual responses
* ✅ AWS Step Functions orchestration
* ✅ Bedrock Guardrails for safety
* ✅ Retry handling for reliability

---

## 🏗️ Architecture

```text
User
 ↓
Step Function
 ↓
Lambda Orchestrator
 ↓
 ├── Tool Lambda (refund / shipping)
 ├── RAG Lambda (knowledge retrieval)
 ↓
Bedrock LLM (Claude)
 ↓
Guardrails
 ↓
Final Response
```

---

## 🛠️ Tech Stack

* **AWS Bedrock (Claude 3 Haiku)**
* **AWS Lambda**
* **AWS Step Functions**
* **Python (boto3)**

---

## 📂 Project Structure

```
genai-faq-system-aws-bedrock/
│
├── lambda/
│   ├── orchestrator.py
│   ├── faq_tools.py
│   ├── faq_rag.py
│
├── step_function/
│   └── state_machine.json
│
├── requirements.txt
├── README.md
```

---

## 🧪 Example Queries

| Query                  | Flow      |
| ---------------------- | --------- |
| What is refund policy? | Tool      |
| How long is shipping?  | Tool      |
| Tell me about warranty | RAG       |
| How to hack a system?  | ❌ Blocked |

---

## 🔐 Safety Design

This system uses **multi-layer safety**:

* LLM-based classification (UNSAFE detection)
* AWS Bedrock Guardrails (input/output filtering)
* Controlled tool execution (no unsafe tool calls)

---

## 🚀 How It Works

1. User sends a question
2. Orchestrator decides:

   * TOOL → Calls Lambda tool
   * RAG → Retrieves context
   * UNSAFE → Blocks request
3. Bedrock generates response
4. Guardrails ensure safe output

---

## 📌 Future Improvements

* 🔍 Integrate Vector Database (FAISS / OpenSearch)
* 🌐 Add real APIs (weather, payments)
* 🖥️ Build UI (Streamlit / React)
* 🤖 Add Agent Framework (LangChain)

---

## 👨‍💻 Author

**Harish Sathiyanarayanan**
