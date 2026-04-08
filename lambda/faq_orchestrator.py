import boto3
import json

# AWS clients
bedrock = boto3.client("bedrock-runtime")
lambda_client = boto3.client("lambda")

# ✅ Your Guardrail ID (correct one)
GUARDRAIL_ID = "wnrqv1prb6eq"

def call_llm(prompt, max_tokens=100):
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens
        }),
        guardrailIdentifier=GUARDRAIL_ID,
        guardrailVersion="1"
    )

    output = json.loads(response["body"].read())
    return output["content"][0]["text"].strip()


def lambda_handler(event, context):
    question = event.get("question", "")

    # -----------------------------
    # STEP 1: SAFETY + ROUTING
    # -----------------------------
    decision_prompt = f"""
    You are a strict classifier.

    Classify the question into one of three categories:

    - TOOL → ONLY if clearly about refund or shipping
    - RAG → ONLY if clearly about warranty, support, returns, cancellation
    - UNSAFE → if the question involves hacking, illegal activity, scams, violence, weapons, harmful instructions, or anything unsafe

    Respond with ONLY one word: TOOL, RAG, or UNSAFE.

    Question: {question}
    """

    decision = call_llm(decision_prompt, max_tokens=10).upper()

    # -----------------------------
    # STEP 2: BLOCK UNSAFE
    # -----------------------------
    if "UNSAFE" in decision:
        return {"result": "Sorry, I cannot answer that request."}

    # -----------------------------
    # STEP 3: TOOL FLOW
    # -----------------------------
    elif "TOOL" in decision:

        tool_prompt = f"""
        Decide which tool to use:

        - refund → for refund related questions
        - shipping → for shipping related questions

        Respond ONLY with one word: refund or shipping.

        Question: {question}
        """

        tool_name = call_llm(tool_prompt, max_tokens=5).lower()

        # safety fallback
        if tool_name not in ["refund", "shipping"]:
            return {"result": "Sorry, I could not determine the correct tool."}

        tool_res = lambda_client.invoke(
            FunctionName="faq-tools",
            Payload=json.dumps({"tool": tool_name})
        )

        return json.loads(tool_res["Payload"].read())

    # -----------------------------
    # STEP 4: RAG FLOW
    # -----------------------------
    elif "RAG" in decision:

        rag_res = lambda_client.invoke(
            FunctionName="faq-rag",
            Payload=json.dumps({"query": question})
        )

        context = json.loads(rag_res["Payload"].read())["context"]

        # Optional: pass through LLM for better formatting
        final_prompt = f"""
        Answer the question using the information below:

        {context}

        Question: {question}
        """

        answer = call_llm(final_prompt, max_tokens=200)

        return {"result": answer}

    # -----------------------------
    # FALLBACK
    # -----------------------------
    return {"result": "Sorry, I could not understand your request."}