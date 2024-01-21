from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from dotenv import load_dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'planer.settings')
env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), '.env')
load_dotenv(env_file)

app = Celery('planer')
app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.enable_utc = False

app.conf.update(timezone='Europe/Warsaw')

app.autodiscover_tasks()