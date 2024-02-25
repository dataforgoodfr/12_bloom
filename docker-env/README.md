
# Docker

## Build APP_BLOOM container
### Default build
```
#> cd <project>
#> docker build -t app_bloom -f docker-env/Dockerfile .
```
### Build with arguments
The container can be build with default arguments so all following build arguments are optionals. However, some settings can be customized

**Available build arguments** :
* **FROM_IMAGE**: define the image "FROM" for the Dockerfile. Permit to test easely other python distributions .
  * **Default: python:3.10-slim-bullseye**
* **APP_DIR**: define the app home folder and working directory
  * **Default: /source_code**
* **POETRY_VERSION**: define poetry package version
  * **Default: 1.4.0**
* **CHROME_VERSION**: define the Chrome navigator version
  * **Default: 112.0.5615.165-1**

**Example:**
```
#> cd <project>
#> docker build -t app_bloom --build-arg="FROM_IMAGE=python:3.12-slim-bullseye" --build-arg="POETRY_VERSION=1.7.0" --build-arg="APP_DIR=/app" -f docker-env/Dockerfile .
```
This example build the **app_bloom** container with an overrided **FROM_IMAGE** python 3.12 version, a **POETRY_VERSION** equals to 1.7.0 and an **APP_DIR** home folder path /app instead of /source_code

# Run APP_BLOOM container
## Environment variables
The APP_BLOOM image uses several environment variables which are easy to miss. The variable required are:
* `POSTGRES_USER`
This environment variable is required for you to use the APP_BLOOM image. It must not be empty or undefined. This environment variable sets the name to use for PostgreSQL database connexion.
* `POSTGRES_PASSWORD`
This environment variable is required for you to use the APP_BLOOM image. It must not be empty or undefined. This environment variable sets the password to use for PostgreSQL database connexion.
* `POSTGRES_HOSTNAME`
This environment variable is required for you to use the APP_BLOOM image. It must not be empty or undefined. This environment variable sets the hostname server to use for PostgreSQL database connexion.
* `POSTGRES_DB`
This environment variable is required for you to use the APP_BLOOM image. It must not be empty or undefined. This environment variable sets the database name to use for PostgreSQL database connexion.
* `POSTGRES_PORT`
This environment variable is required for you to use the APP_BLOOM image. It must not be empty or undefined. This environment variable sets the database port to use for PostgreSQL database connexion.
* `SPIRE_TOKEN`
This environment variable is required for you to use the APP_BLOOM image. It must not be empty or undefined. This environment variable sets the *Spire Token* port to use for *Spire API* connexion.

## Docker Secrets
As an alternative to passing sensitive information via environment variables, `_FILE` may be appended to some of the previously listed environment variables, causing the initialization script to load the values for those variables from files present in the container. In particular, this can be used to load passwords from Docker secrets stored in `/run/secrets/<secret_name>` files.
For example:
```console
$ docker run --name app_bloom -e [...] -e POSTGRES_PASSWORD_FILE=/run/secrets/postgres-passwd -v "/path/to/secrets/postgres-password:/run/secrets/postgres-passwd" -d app_bloom:latest
```
