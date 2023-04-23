FROM python:3.10-slim

RUN apt-get update
RUN apt-get -y install wget

# Define working directory
WORKDIR /source_code

# Install requirements package for python with poetry
ENV POETRY_VERSION=1.3.1
RUN pip install --user "poetry==$POETRY_VERSION"
ENV PATH="${PATH}:/root/.local/bin"
COPY pyproject.toml poetry.lock ./
RUN poetry install

# Install cron
RUN apt-get install -y cron

# Install chrome in the latest version
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN rm -f google-chrome-stable_current_amd64.deb

# Create cron task inside container
RUN echo '*/15 * * * * cd /source_code && /root/.local/bin/poetry run python3 app.py >> /data/cron_log.log 2>&1' >> ./cron_scrapper
RUN chmod 744 ./cron_scrapper

# Move cron tab into the right directory
RUN mv ./cron_scrapper /etc/cron.d/cron_scrapper

# Run file
ENV CHROME_DRIVER_VERSION 109
RUN crontab /etc/cron.d/cron_scrapper

# Launch cron services
ENTRYPOINT ["cron", "-f"]

