FROM python:3.8.5
ENV PYTHONUNBUFFERED=1
WORKDIR /code
ADD requirements /code/requirements
RUN pip install -r requirements/dev.txt
COPY . /code/
