# journalapi/utils.py
from flask import Response
import json

def JsonResponse(body, status=200, mimetype="application/json"):
    return Response(json.dumps(body), status=status, mimetype=mimetype)
