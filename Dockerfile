FROM python:3.8.5
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get -y install ghostscript

COPY policy.xml /etc/ImageMagick-6/policy.xml

WORKDIR /code
ADD requirements /code/requirements
RUN pip install -r requirements/dev.txt
ADD . /code

CMD ls -la

CMD gunicorn config.wsgi --bind 0.0.0.0:8000 --chdir /code/ipno
