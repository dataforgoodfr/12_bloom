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
