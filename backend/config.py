class Config:
    #---App Configg---
    SECRET_KEY = "avinash-secret-key"

    #---DataBase Config---
    SQLALCHEMY_DATABASE_URI = "sqlite:///hospital.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #---JWT Config---
    JWT_SECRET_KEY = "avinash-jwt"
    JWT_ACCESS_TOKEN_EXPIRES = 60*60*24 #24 hours

    #---Redis/Celery Config---
    REDIS_URL = "redis://localhost:6379/0"
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/1"

    #---Caching Config---
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = "redis://localhost:6379/2"
    