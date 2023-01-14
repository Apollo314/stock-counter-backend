FROM python:3-slim as python
ENV PYTHONUNBUFFERED=true

FROM python as poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -
COPY pyproject.toml /code/
WORKDIR /code
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction
ENV PATH="/app/.venv/bin:$PATH"

COPY . /code/

ENTRYPOINT ["/code/entrypoint.sh"]

# CMD ["gunicorn", "goktugv2.asgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "-k", "uvicorn.workers.UvicornWorker"]