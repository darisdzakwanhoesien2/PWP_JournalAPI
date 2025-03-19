from flask import Blueprint
from flask_restful import Api

from journalapi.resources.user import UserLoginResource, UserRegisterResource, UserResource
# from journal_api.resources.location import LocationItem
# from journal_api.resources.measurement import MeasurementCollection

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

print("Registering routes...")
api.add_resource(UserRegisterResource, "/user/register/", endpoint="user_register")
api.add_resource(UserLoginResource, "/user/login/", endpoint="user_login")
api.add_resource(UserResource, "/users/<int:user_id>/", endpoint="user")
# api.add_resource(MeasurementCollection, "/sensors/<sensor:sensor>/measurements/")