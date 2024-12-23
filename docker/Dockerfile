ARG IMAGE_PYTHON=${IMAGE_PYTHON:-python:3.10-slim-bullseye}
FROM ${IMAGE_PYTHON}

RUN apt-get update &&\
    apt-get -y install curl &&\
    apt-get install -y rsyslog &&\
    apt-get install -y libgdal-dev &&\
    apt-get install -y g++ &&\
    apt-get install -y clang


# Define working directory
ARG VIRTUAL_ENV=/.venv
ENV PATH=${VIRTUAL_ENV}/bin:$PATH \
    VIRTUAL_ENV=${VIRTUAL_ENV}
ARG PROJECT_DIR=/project
ENV PROJECT_DIR=${PROJECT_DIR}
WORKDIR ${PROJECT_DIR}

# BACKEND
ENV PYTHONPATH=${PROJECT_DIR}/backend
COPY ./backend/ ${PROJECT_DIR}/backend
COPY docker/rsyslog.conf /etc/rsyslog.conf

# Install requirements package for python with poetry
#ARG POETRY_VERSION=1.8.2
#ENV POETRY_VERSION=${POETRY_VERSION}
#RUN pip install --upgrade pip && pip install --user "poetry==$POETRY_VERSION"
ENV PATH="${PATH}:/root/.local/bin"
COPY ./backend/pyproject.toml ./backend/alembic.ini ./backend/


# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ARG UV_PROJECT_ENVIRONMENT=${VIRTUAL_ENV}
ENV UV_PROJECT_ENVIRONMENT=${VIRTUAL_ENV}
RUN \
    cd backend &&\
    uv venv ${VIRTUAL_ENV} &&\
    echo ". ${VIRTUAL_ENV}/bin/activate" >> ~/.bashrc &&\
    . ${VIRTUAL_ENV}/bin/activate &&\
    uv sync

# Launch cron services
RUN DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install -y cron \
    # Remove package lists for smaller image sizes
    && rm -rf /var/lib/apt/lists/* \
    && which cron \
    && rm -rf /etc/cron.*/*

# FRONTEND
#ARG NPM_VERSION=v0.39.7
#ENV NPM_VERSION=${NPM_VERSION}
#ARG NODE_VERSION=18
#ENV NODE_VERSION=${NODE_VERSION}
#COPY frontend ${PROJECT_DIR}/frontend
# installs NVM (Node Version Manager)
# download and install Node.js
#RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/${NPM_VERSION}/install.sh | bash &&\
#	. /root/.bashrc &&\
#	nvm install $NODE_VERSION &&\
#	ln -sf `nvm which node` /usr/local/bin/node &&\
#	ln -sf ${PROJECT_DIR}/frontend/node_modules/next/dist/bin/next /usr/local/bin/next &&\
#	cd frontend &&\
#	npm install && (echo "NPM: Install OK") || (echo "NPM: Install error"; exit 1) &&\
#   npm run build && (echo "NPM: Build OK") || (echo "NPM: Build error"; exit 1)

COPY docker/entrypoint.sh /entrypoint.sh
RUN ["chmod", "+x", "/entrypoint.sh"]

# ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
# https://manpages.ubuntu.com/manpages/trusty/man8/cron.8.html
# -f | Stay in foreground mode, don't daemonize.
# -L loglevel | Tell  cron  what to log about jobs (errors are logged regardless of this value) as the sum of the following values:
CMD ["cron","-f", "-L", "2"]
