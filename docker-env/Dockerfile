FROM python:3.10-bullseye

# Define working directory
WORKDIR /source_code

# Install requirements package for python with poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY pyproject.toml poetry.lock ./
RUN /root/.local/bin/poetry install

# Install cron
RUN apt-get update
RUN apt-get install -y cron

# Install chrome in a specific version 109
ARG CHROME_VERSION="109.0.5414.119-1"
RUN wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb
RUN apt install -y /tmp/chrome.deb
RUN rm /tmp/chrome.deb

# Create cron task inside container
RUN echo '*/15 * * * * cd /source_code && /root/.local/bin/poetry run python3 app.py >> /data/cron_log.log 2>&1' >> ./cron_scrapper
RUN chmod 744 ./cron_scrapper

# Move cron tab into the right directory 
RUN mv ./cron_scrapper /etc/cron.d/cron_scrapper

# Run file
RUN crontab /etc/cron.d/cron_scrapper

# Launch cron services
ENTRYPOINT ["cron", "-f"]

