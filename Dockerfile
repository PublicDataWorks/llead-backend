FROM python:3.8.5
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get -y install ghostscript

COPY policy.xml /etc/ImageMagick-6/policy.xml

WORKDIR /code
ADD requirements /code/requirements
RUN pip install -r requirements/dev.txt
ADD . /code

CMD ls -la

CMD gunicorn config.wsgi -c gunicorn.conf.py --chdir /code/ipno