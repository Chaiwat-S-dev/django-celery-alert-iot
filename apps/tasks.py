from celery import Celery
from .settings import CELERY_BROKER_URL

app = Celery('tasks', broker=CELERY_BROKER_URL)

@app.task
def add(x, y):
    print(f'parse args: {x=}, {y=}')
    print(f'result: {x+y}')