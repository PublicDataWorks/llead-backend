FROM python:3.8.5
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get -y install ghostscript

COPY policy.xml /etc/ImageMagick-6/policy.xml

WORKDIR /code
ADD requirements /code/requirements

RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements/dev.txt

RUN python -m spacy download en_core_web_sm

ADD . /code

CMD ls -la

CMD gunicorn config.wsgi -c gunicorn.conf.py --chdir /code/ipno