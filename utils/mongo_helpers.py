from bson import ObjectId

def to_json_serializable(obj):
    """
    Recursively convert MongoDB documents (dicts, lists) so all ObjectId fields become strings.
    This makes the result fully JSON-serializable for FastAPI responses.
    """
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_json_serializable(item) for item in obj]
    else:
        return obj
