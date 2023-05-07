FROM python:3.11-bullseye

WORKDIR /code

RUN apt-get update && apt-get -y install libpq-dev gcc && pip install psycopg2

COPY requirements/*.txt /code/requirements/
COPY setup.cfg /code/
COPY setup.py /code/
RUN pip install --no-cache-dir --use-pep517 --upgrade -e /code/.

COPY ./src /code/src
WORKDIR /code/src

CMD ["hypercorn", "--bind", "0.0.0.0:8080", "app.main:app"]
