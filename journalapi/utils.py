# PWP_JournalAPI/journalapi/utils.py
import json
from flask import Response

def JsonResponse(body, status=200, mimetype="application/json"):
    # If the response is a dict and lacks _links, try to auto-add them based on resource type.
    if isinstance(body, dict) and "_links" not in body:
        if "id" in body:
            resource_type = detect_resource_type(body)
            body["_links"] = generate_links(resource_type, body["id"])
    # If it's a list, add _links for each item if not present
    elif isinstance(body, list):
        for item in body:
            if isinstance(item, dict) and "id" in item and "_links" not in item:
                resource_type = detect_resource_type(item)
                item["_links"] = generate_links(resource_type, item["id"])
    return Response(json.dumps(body), status=status, mimetype=mimetype)

def detect_resource_type(data):
    if "title" in data and "content" in data:
        return "entry"
    elif "email" in data:
        return "user"
    elif "journal_entry_id" in data and "content" in data:
        return "comment"
    elif "previous_content" in data:
        return "edithistory"
    return None

def generate_links(resource_type, id_):
    if resource_type == "entry":
        return {
            "self": {"href": f"/entries/{id_}"},
            "edit": {"href": f"/entries/{id_}"},
            "delete": {"href": f"/entries/{id_}"},
            "comments": {"href": f"/entries/{id_}/comments"},
            "history": {"href": f"/entries/{id_}/history"}
        }
    elif resource_type == "user":
        return {
            "self": {"href": f"/users/{id_}"},
            "edit": {"href": f"/users/{id_}"},
            "delete": {"href": f"/users/{id_}"}
        }
    elif resource_type == "comment":
        # Comment's resource URL uses parent entry info; this is handled in the model's to_dict
        return {
            "self": {"href": f"/entries/{id_}/comments/{id_}"}
        }
    elif resource_type == "edithistory":
        return {
            "self": {"href": f"/entries/{id_}/history/{id_}"}
        }
    return {}
