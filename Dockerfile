FROM python:3.8.5
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=$PYTHONPATH:/code/ipno

RUN apt-get update && apt-get -y install ghostscript netcat

COPY policy.xml /etc/ImageMagick-6/policy.xml

WORKDIR /code
ADD requirements /code/requirements

RUN pip install -U pip setuptools

RUN pip install -r requirements/dev.txt

RUN python -m spacy download en_core_web_sm

ADD . /code

CMD gunicorn config.wsgi -c gunicorn.conf.py --chdir /code/ipno