import json

def lambda_handler(event, context):
    tool = event.get("tool")

    if tool == "refund":
        return {"result": "Refund within 7 days with receipt."}

    elif tool == "shipping":
        return {"result": "Shipping takes 3-5 days."}

    return {"result": "Unknown tool"}