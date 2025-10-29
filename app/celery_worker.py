import time

from celery import Celery
from app.config import REDIS_SERVER, REDIS_PORT, REDIS_DB

REDIS_URL = f"redis://{REDIS_SERVER}:{REDIS_PORT}/{REDIS_DB}"

app = Celery('tasks', broker=REDIS_URL)

@app.task
def send_welcome_email(email: str):
    time.sleep(5)
    print("Sending welcome email!")