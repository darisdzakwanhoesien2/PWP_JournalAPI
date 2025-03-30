from flask import Response
import json

def JsonResponse(body, statusCode, mimetype="application/json"):
    return Response(json.dumps(body), status=statusCode, mimetype=mimetype)