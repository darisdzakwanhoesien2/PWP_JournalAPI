# PWP_JournalAPI/journalapi/utils.py
import json
from flask import Response

def JsonResponse(body, status=200, mimetype="application/json"):
    if isinstance(body, dict) and "_links" not in body:
        if "id" in body:
            # Inject common links based on resource type
            resource_type = detect_resource_type(body)
            body["_links"] = generate_links(resource_type, body["id"])
    return Response(json.dumps(body), status=status, mimetype=mimetype)


def detect_resource_type(data):
    # Basic logic to determine resource type
    if "title" in data:
        return "entry"
    elif "email" in data:
        return "user"
    elif "content" in data and "journal_entry_id" in data:
        return "comment"
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
        return {
            "self": {"href": f"/entries/{id_}/comments/{id_}"},
            "edit": {"href": f"/entries/{id_}/comments/{id_}"},
            "delete": {"href": f"/entries/{id_}/comments/{id_}"}
        }
    return {}
