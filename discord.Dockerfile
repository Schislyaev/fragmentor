FROM python:3.10.2

WORKDIR /opt/app

RUN pip install poetry

#COPY pyproject.toml poetry.lock /opt/app/
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY ./discord_bot ./discord_bot/
COPY ./core ./core/

COPY discord_entry.sh /

WORKDIR /opt/app

ENTRYPOINT ["sh", "/discord_entry.sh"]
