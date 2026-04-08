import json

# This is our "knowledge base"
DATA = [
    "Our products come with a 1-year warranty covering manufacturing defects.",
    "You can cancel an order within 24 hours of placing it.",
    "Customer support is available 24/7 via chat and email.",
    "Returns are processed within 5 business days after approval."
]

def lambda_handler(event, context):
    query = event["query"].lower()

    # Simple keyword search (simulating RAG)
    for doc in DATA:
        if any(word in doc.lower() for word in query.split()):
            return {"context": doc}

    return {"context": "No relevant information found."}