import boto3
import json

bedrock = boto3.client("bedrock-runtime")
lambda_client = boto3.client("lambda")

GUARDRAIL_ID = "wnrqv1prb6eq"
GUARDRAIL_VERSION = "1"

def lambda_handler(event, context):
    question = event.get("question", "")

    # -----------------------------
    # STEP 1: CLASSIFY (TOOL / RAG / UNKNOWN)
    # -----------------------------
    decision_prompt = f"""
    Classify the user question into one of the following:

    TOOL → if about refund or shipping  
    RAG → if about warranty, cancellation, support, returns  
    UNKNOWN → if unrelated to business FAQs  

    Respond ONLY with one word: TOOL, RAG, or UNKNOWN.

    Question: {question}
    """

    decision_response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": decision_prompt}],
            "max_tokens": 10
        }),
        guardrailIdentifier=GUARDRAIL_ID,
        guardrailVersion=GUARDRAIL_VERSION
    )

    decision_output = json.loads(decision_response["body"].read())
    decision = decision_output["content"][0]["text"].strip().upper()

    # -----------------------------
    # HANDLE UNKNOWN (VERY IMPORTANT 🔥)
    # -----------------------------
    if "UNKNOWN" in decision:
        return {
            "result": "Sorry, I can only answer questions related to our services."
        }

    # -----------------------------
    # TOOL FLOW
    # -----------------------------
    if "TOOL" in decision:

        tool_prompt = f"""
        If question is about refund → say refund
        If question is about shipping → say shipping

        Only respond with one word.

        Question: {question}
        """

        tool_response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": tool_prompt}],
                "max_tokens": 5
            }),
            guardrailIdentifier=GUARDRAIL_ID,
            guardrailVersion=GUARDRAIL_VERSION
        )

        tool_output = json.loads(tool_response["body"].read())
        tool_name = tool_output["content"][0]["text"].strip().lower()

        # Safety fallback
        if tool_name not in ["refund", "shipping"]:
            tool_name = "refund"

        tool_res = lambda_client.invoke(
            FunctionName="faq-tools",
            Payload=json.dumps({"tool": tool_name})
        )

        return json.loads(tool_res["Payload"].read())

    # -----------------------------
    # RAG FLOW
    # -----------------------------
    elif "RAG" in decision:

        rag_res = lambda_client.invoke(
            FunctionName="faq-rag",
            Payload=json.dumps({"query": question})
        )

        context_text = json.loads(rag_res["Payload"].read())["context"]

        # 🔥 CONTROLLED SHORT RESPONSE
        final_prompt = f"""
        Answer the question using ONLY the given context.

        Keep the answer SHORT (1 sentence only).
        Do NOT add extra explanation.

        Question: {question}
        Context: {context_text}
        """

        final_response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": final_prompt}],
                "max_tokens": 50
            }),
            guardrailIdentifier=GUARDRAIL_ID,
            guardrailVersion=GUARDRAIL_VERSION
        )

        final_output = json.loads(final_response["body"].read())
        answer = final_output["content"][0]["text"].strip()

        return {"result": answer}

    # -----------------------------
    # FINAL FALLBACK
    # -----------------------------
    return {
        "result": "Sorry, I cannot answer that request."
    }