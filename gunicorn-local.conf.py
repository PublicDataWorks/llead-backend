from gevent import monkey
from psycogreen.gevent import patch_psycopg

monkey.patch_all()


bind = "0.0.0.0:8000"
loglevel = "info"
accesslog = None
errorlog = '-'


raw_env = [
    'DJANGO_SETTINGS_MODULE=config.settings.dev',
    'GOOGLE_APPLICATION_CREDENTIALS=/code/gcloud-credentials.json'
]

worker_class = 'gevent'
workers = 3


def do_post_fork(server, worker):
    patch_psycopg()

    worker.log.info("Made Psycopg2 Green")


post_fork = do_post_fork
