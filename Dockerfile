FROM python:3.10-slim
RUN apt-get update
RUN apt-get -y install wget

COPY bloom/ ./bloom/
COPY data/ ./data/
COPY app.py .

# Install requirements package for python with poetry
ENV POETRY_VERSION=1.4.0
RUN pip install --user "poetry==$POETRY_VERSION"
# Add the poetry binary files in the executable path
ENV PATH="${PATH}:/root/.local/bin"
COPY pyproject.toml poetry.lock ./
RUN poetry install

# Install chrome in the latest version
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN rm -f google-chrome-stable_current_amd64.deb


# Launch cron services
ENTRYPOINT ["poetry","run","python3", "app.py"]