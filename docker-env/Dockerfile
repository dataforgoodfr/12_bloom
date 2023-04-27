FROM python:3.10-slim

RUN apt-get update
RUN apt-get -y install wget

# Define working directory
WORKDIR /source_code
COPY bloom/ ./bloom/
COPY data/ ./data/
COPY app.py .

# Install requirements package for python with poetry
ENV POETRY_VERSION=1.4.0
RUN pip install --user "poetry==$POETRY_VERSION"
ENV PATH="${PATH}:/root/.local/bin"
COPY pyproject.toml poetry.lock ./
RUN poetry install

# Install cron
RUN apt-get install -y cron

# Install chrome in the latest version
ARG CHROME_VERSION="112.0.5615.165-1"
RUN wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb
RUN apt-get install -y /tmp/chrome.deb
RUN rm -f google-chrome-stable_current_amd64.deb

# Create cron task inside container
RUN echo '*/15 * * * * cd /source_code && /root/.local/bin/poetry run python3 app.py >> /data/cron_log.log 2>&1' >> ./cron_scrapper
RUN chmod 744 ./cron_scrapper

# Move cron tab into the right directory
RUN mv ./cron_scrapper /etc/cron.d/cron_scrapper

# Run file
RUN crontab /etc/cron.d/cron_scrapper

# Launch cron services
ENTRYPOINT ["cron", "-f"]

