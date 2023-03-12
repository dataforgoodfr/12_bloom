FROM python:3.10-bullseye

# Install requirements package for python 
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Install cron
RUN apt-get update
RUN apt-get install -y cron

# Create cron task inside container
RUN echo '*/5 * * * * python3 /source_code/bloom_scraper_crontab.py >> cron_log.log 2>&1' >> ./cron_scrapper
RUN chmod 744 ./cron_scrapper

# Move cron tab into the right directory 
RUN mv ./cron_scrapper /etc/cron.d/cron_scrapper

# Run file
RUN crontab /etc/cron.d/cron_scrapper

# Launch cron services
CMD ["cron", "-f"]

