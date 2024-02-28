

---
id: 
title: Bloom App Configuraiton Management
desc: "This document describes how configurations files/variables are managed and runtime environment dev/test/prod"
updated: 
created: 
---

# Introduction
The Bloom App configuration set up manage file configuration AND environment variables configuration

It is inspired by two configuration systems:
- PHP [Symfony Framework configuration system](https://symfony.com/doc/current/configuration.html#configuration-based-on-environment-variables)

This configuration system is based on file system with ***.env*** that gives default values for **ALL** parameters and define the list of the configuration variables that could be overrided in optional files ***.env.local***, ***.env.[APP_ENV]***, ***.env.[APP_ENV].local*** where ***APP_ENV*** is the runtime environment (dev/test/prod/...). 
Some files are indexed in Git repository as they gives default values and default overrided values per environment: ***.env***, **.env.[APP_ENV]**. Note that even if not ignore by ***.ignore***, theses files are optional and created on demand.
***APP_ENV*** must have its default value set in ***.env*** (*APP_ENV='dev'* i.e.) and can be overload on demand on .env.local (*APP_ENV='test'* .e.i)
- Docker suite standard for configuration management

Docker is now everywhere and comes with best practices. In terms of configuration management Docker image editors have set up a standard of fact concerning configuration that must give flexibility to image users but manage some deployment constraints as multiple enivironment management and sensibility of some parameters
Here are Docker "Best Practices" that have been implemented for Bloom App:
* All parameters can be loaded by a configuration file and environment variables
* If present in both, priority is givent to the environment variable value
* All attributes can be give by a direct KEY=VALUE pair or indirectly by adding a _FILE suffix to the name of the KEY, this KEY_FILE pointing to a file local to the deployment system that will give the final value to the attribute
	* Exemple: POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password will give a POSTGRES_PASSWORD equals to the content of postgres_password file. In Docker this is heavely used to manage sensible values known as "secrets"

Theses two systems of configuration management allows to manage easely multiple environment (Symfony) and multiple deployment as configurations values can be overloaded explicitly by environments variables specific to the deployement plateforme as can be a Docker Container based deployment

# Quick Start

## First step : défine default values (indexed in git)

* create blank .env file or copy it from .env.template
* git add .env
* git commit -m "add: default values in .env"

**IMPORTANT:** Toutes les valeurs disponibles dans l'application doivent impérativement avoir été déclarées dans ce fichier ***.env***, sinon elle ne seront pas traitée dans la suite du process et ne seront pas disponible via la configuration

## Second step : define specific values for local deployment (ignored by git)

* create blank .env.local
* define local value for APP_ENV (APP_ENV=test i.e)
* define all local variables values that will be common to all APP_ENV (dev/test/prod)

## Third step : define default APP_ENV specific values (optional)

This step is optional as there maybe not specific values per APP_ENV
It is generally usefull when multiple environment can be launch on the same host and solve port or Docker container name conflicts automatically
It is usefull too to ensure that an instance in "dev" cannot pretend to be an instance in another environment (test or prod), it's eliminate ambiguity as dev won't use same user, port, database then the other by default

* create .env.dev, .env.test, .env.prod
* define default values that could be specific for each platform
* git commit -m "add: default values in .env.${APP_ENV}"

## Forth step : define default APP_ENV specific local values (optional)

As previous one, this step is optional as there maybe not specific values per APP_ENV
You can define .env.test.local without having a .env.test existing

* create .env.dev.local, .env.test.local, .env.prod.local
* define local plateform and APP_ENV sepcific values

It is generally used for credentials that must not be indexed in git, are platform and environment (dev/test/prod) specific

## Access to "merged" APP_ENV specific configuration in Bloom Application

To get values that will be extracted according to .env variable list, APP_ENV value and .env.* files presence, you just have to import settings object from bloom.config

    from bloom.config import settings
    print(settings.POSTGRES_USER)
   WARNING: Be carefull, bloom.config is case sensitive and is based on syntax used in ***.env*** file
   To get the whole list of variables available, consult [.env.template](.env.template)
  
## Switching environment (test=>prod, prod=>test,test<=>dev,...)

To switch from environment to another, two ways are available:
- modify .env.local and then set `APP_ENV=prod` to switch to prod **(recommended method)**
- just change APP_ENV value by exporting/forcing new value : `export APP_ENV=prod` 

Both technics are available for Docker conteneur too

# Additional ways to manage configuration values
## By environment variable (prioritary on file)
In several cases, it can be interseting to override file configuration with other values. The default way to do this is to modify one of the .env.*.local file but there is another way by exporting the same setting as environment variable
***IMPORTANT:***  All key=value defined in environment variables will be prioritary on key=value pairs defined in .env* files. It is specially usefull when loading current configuration in a Docker container but for Docker specific needs you have to override some parameters. So you can do that without chaging configuration files
Example:
***.env file***

	# /.env (default values and restricted list)
    POSTGRES_HOSTNAME=my.database.host
    
***.env.local***

    .env.local
    POSTGRES_HOSTNAME=localhost
***Docker command***

    docker run -v "$(pwd)/.env:/source_code/.env" -v "$(pwd)/.env.local:/source_code/.env.local" -e POSTGRES_HOSTNAME=postgres app_bloom:latest

In this case, even if local configuration says `POSTGRES_HOSTNAME=localhost` then in Docker, the value will overrided by ENV value `POSTGRES_HOSTNAME=postgres`

This mecanism can be used to override APP_ENV defined in files (.env.local)

## "indirect value by file" (_FILE)

All attributes defined in .env define the list of key=value pairs that will be processed and accesisble in bloom.config module in the application
In addition to that, and for conformity with Docker standard, all attribute can be set by direct key=value pair but can be set by indirect set with [key]_FILE=VALUE_PATH pair.
In this case, the bloom.config module will analyse VALUE_PATH and then load the content of the pointed file in the [key] key of the configuration
This is specificly usefull to manage secrets in Docker but can be used other type of use even in native deployment to centralise and have sensible data in other folder than the application
