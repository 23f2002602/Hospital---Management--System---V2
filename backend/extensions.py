from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_caching import Cache
from database import db

migrate = Migrate()
jwt = JWTManager()
cors = CORS()
cache = Cache()