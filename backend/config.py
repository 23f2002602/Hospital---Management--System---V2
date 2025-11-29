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

    CELERY_REMINDER_CRON = 86400

    # Mail settings
    MAIL_SERVER = "localhost"
    MAIL_PORT = 1025
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = "no-reply@hms.local"

    # Report generation settings
    ENABLE_PDF_REPORTS = False

    #---Caching Config---
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = "redis://localhost:6379/2"
    
    DEFAULT_CACHE_TTL = 300            # 5 minutes
    AVAILABILITY_CACHE_TTL = 300       # 5 minutes
    DOCTOR_SEARCH_CACHE_TTL = 60       # 1 minute