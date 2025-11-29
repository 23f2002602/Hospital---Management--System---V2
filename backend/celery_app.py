from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        backend=app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    )
    celery.conf.update(app.config)

    celery.conf.beat_schedule = {
        "daily-appointment-reminders": {
            "task": "tasks.send_daily_reminders",
            "schedule": app.config.get("CELERY_REMINDER_CRON", 86400),  # default once per 86400s; override below if needed
        },
  }

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery