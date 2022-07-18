FROM python:3.8-buster as base

# Install poetry
RUN pip install poetry

ARG TILEBOX_API_KEY

WORKDIR /app
ADD poetry.lock pyproject.toml ./

# Install our dependencies
RUN poetry config repositories.tilebox https://pypi.adler-x.snamber.com
RUN poetry config http-basic.tilebox __token__ $TILEBOX_API_KEY
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-dev
ENV PATH "/app/.venv/bin/:${PATH}"

# Install the tilebox-processing binary
RUN wget -O /usr/bin/tilebox-processing --user=nouser --password=$TILEBOX_API_KEY  https://processing.tilebox.io/get/tilebox-processing/tilebox-processing_latest_linux_amd64 && chmod +x /usr/bin/tilebox-processing

# Install our application(s)
ADD . .
RUN poetry install --no-dev

CMD ["tilebox-processing", "node"]
