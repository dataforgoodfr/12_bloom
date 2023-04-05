FROM python:3.10-bullseye
RUN apt-get update

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

# Install chrome in a specific version 109
ARG CHROME_VERSION="109.0.5414.119-1"
RUN wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb
RUN apt-get install -y /tmp/chrome.deb
RUN rm /tmp/chrome.deb
ENV CHROME_DRIVER_VERSION 109

# Launch cron services
ENTRYPOINT ["python3", "app.py"]