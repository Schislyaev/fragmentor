FROM python:3.10.2

WORKDIR /opt/app

RUN pip install poetry
RUN pip install debugpy

#COPY pyproject.toml poetry.lock /opt/app/
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY ./tg ./tg/
COPY ./core ./core/

COPY tg_debug_entry.sh /

WORKDIR /opt/app

ENTRYPOINT ["sh", "/tg_debug_entry.sh"]
