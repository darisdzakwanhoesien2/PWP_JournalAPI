import json
from flask import Response

def JsonResponse(body, status=200, mimetype="application/json"):
    return Response(json.dumps(body), status=status, mimetype=mimetype)
