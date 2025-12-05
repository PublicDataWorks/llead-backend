FROM python:3.8.5
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=$PYTHONPATH:/code/ipno

# Use Debian archive for Buster (deprecated but still available)
RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org|archive.debian.org/|g' /etc/apt/sources.list && \
    sed -i '/stretch-updates/d' /etc/apt/sources.list && \
    apt-get update && apt-get -y install ghostscript netcat

COPY policy.xml /etc/ImageMagick-6/policy.xml

WORKDIR /code
ADD requirements /code/requirements

RUN pip install -U "pip<24.1" setuptools

RUN pip install -r requirements/dev.txt

RUN python -m spacy download en_core_web_sm

ADD . /code

CMD gunicorn config.wsgi -c gunicorn.conf.py --chdir /code/ipno