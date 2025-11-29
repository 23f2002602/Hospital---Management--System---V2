from app import create_app
from celery_app import make_celery
from tasks import init_celery

app = create_app()
celery = make_celery(app)

init_celery(celery)