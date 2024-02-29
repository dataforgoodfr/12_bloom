import os
import re
from pathlib import Path

from pydantic import BaseSettings

def extract_values_from_env(config:dict,allow_extend:bool=False) -> dict:
    """ function that extrat key=value pairs from a file
    Parameters:
    - config: dict to extend/update with new key/value pairs found in environment
    - allow_extend: allows to extend extracted keys with new keys that are not in
                    actuel config if True, restrict to already existing keys in config of False
    Returns a dict contains key/value
    """
    for k,v in os.environ.items():
        # Processing of indirect affectation via [ATTR]_FILE=VALUE_PATH => ATTR=VALUE
        if k in [f"{k}_FILE" for k in config.keys()]\
            and ( k.removesuffix('_FILE') in config.keys() or  allow_extend == True)\
            and Path(v).is_file():
                with Path.open(v, mode='r') as file:
                    config[k.removesuffix('_FILE')]=file.readline().strip()
        # Processing of direct affectation via ATTR=VALUE
        # if extracted key already exist in config OR if allowed to add new keys to config
        # Then adding/updating key/value
        if k in config.keys() or allow_extend == True:
            config[k]=v
    return config

def extract_values_from_file(filename:str,config:dict,
                             allow_extend:bool=False,
                             env_priority:bool=True
                             )-> dict:
    """ function that extrat key=value pairs from a file
    Parameters:
    - filename: filename/filepath from which to extract key/value pairs found in .env.* file
    - config: dict to extend/update with new key/value pairs
    - allow_extend: allows to extend extracted keys with new keys that are not in actuel
                    config if True, restrict to already existing keys in config of False
    Returns a dict contains key/value
    """ 
    filepath=Path(Path(__file__).parent).joinpath(filename)
    with Path.open(filepath) as file:
        for line in file:
            # Split line at first occurence of '='.
            # This allows to have values containing '=' character
            split=line.strip().split('=',1)
            # if extraction contains 2 items and strictly 2 items
            split_succeed=2
            if(len(split)==split_succeed):
                k=split[0]
                v=split[1]
                # Processing of indirect affectation via [ATTR]_FILE=VALUE_PATH => ATTR=VALUE
                if k in [f"{k}_FILE" for k in config.keys()]\
                    and ( k.removesuffix('_FILE') in config.keys() or  allow_extend == True)\
                    and Path(v).is_file():
                        with Path.open(v, mode='r') as file_value:
                            config[k.removesuffix('_FILE')]=file_value.readline().strip()
                # if extracted key already exist in config OR if allowed to add new keys to
                # config then adding/updating key/value
                if k in config.keys() or allow_extend == True:
                    config[k]=v
            # If env priority True, then overriding all values with ENV values before ending
            if env_priority:
                extract_values_from_env(config,allow_extend=False)
    return config
    
class Settings(BaseSettings):
    APP_ENV:str=None
    db_url:str=None
    def __init__(self):
        super().__init__(self)
        
        # dict to store temporary/overrided config parameters
        config={}
        
        # Here we extract value according to PHP Symfony Framework principles:
        # See: https://symfony.com/doc/current/configuration.html
        #      See Section configuration-based-on-environment-variable
        # The idea is to load sequentialy
        # - .env (default values and common values for all environments dev/test/prod/...).
        #    APP_ENV has to be defined here as default env (APP_ENV='dev' i.e.)
        # - .env.local (for local common overrided values)
        # - .env.${APP_ENV} (default values for the specific environment APP_ENV defined
        #                        and overrided before)
        # - .env.${APP_ENV}.local (for local APP_ENV specific values)
        #
        # Some princpales are coming with that:
        # - All configuration variables presents in theses files MUST be declare in .env file.
        # If not they won't be accessible in application.
        # This is a good way to have a file containging all parameters avialables,
        # don't hésitate to document them in .env.template
        # - All default files (.env, .env.APP_ENV) are optional but not ignored
        #       by git if created
        # - All local files (*.local) are optionel and ignored by git if created so theses
        #       files are specific and locl to deployment platform
        
        # In addition we impement the Docker standard that manage configuration base on files
        #    AND environment variables
        # - At each previous step, key=value pairs found in files are systematically override
        #   by its equivalent in environment variables if this one has been declared in env vars
        # This mecanism is usefull when deploying application in Docker as docker specific
        # values can override files configuration just by adding env vars
        # -  All attributes can be set by a direct KEY=VALUE pair or indirectly by adding
        #    a _FILE suffix to the name of the KEY, this KEY_FILE pointing to a file local to
        #    the deployment system that will give the final value to the attribute
        #    - Exemple: POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password will give a 
        
        # Extract .env.template as default values
        file_to_process=Path(Path(__file__).parent).joinpath(f"../.env")
        if Path(file_to_process).is_file():
            extract_values_from_file(file_to_process,config,allow_extend=True,env_priority=True)
        
        # Extract .env.local and override existing values
        file_to_process=Path(Path(__file__).parent).joinpath(f"../.env.local")
        if Path(file_to_process).is_file():
            extract_values_from_file(file_to_process,config,allow_extend=False,
                                     env_priority=True)
        
        # if APP_ENV has been defined
        if 'APP_ENV' in config:
            # Extract .env.${APP_ENV} and override existing values
            file_to_process=Path(Path(__file__).parent).joinpath(f"../.env.{config['APP_ENV']}")
            if Path(file_to_process).is_file():
                extract_values_from_file(file_to_process,config,allow_extend=False,
                                         env_priority=True)
        
            # Extract .env.${APP_ENV}.local and override existing values
            file_to_process=Path(Path(__file__).parent)\
                                .joinpath(f"../.env.{config['APP_ENV']}.local")
            if Path(file_to_process).is_file():
                extract_values_from_file(file_to_process,config,allow_extend=False,
                                         env_priority=True)
        
        # Now we extract key/value pairs from config and add/update them to current
        # class Settings class as attributes
        # All attributes declared in template
        self.__dict__.update(config)
        
        
        # Set the db_url attribute containing connection string to the database
        self.db_url = ( f"postgresql://"
                        f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                        f"@{self.POSTGRES_HOSTNAME}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")
        
        
        # 
        # Destination file of "env" merged config
        # Usefull to set it to docker.${APP_ENV} when generated for docker
        # If not defined, is None and no merged file is generated
        path_env=os.getenv('PATH_ENV')
        if path_env != None:
            # Now all .env.* files has been merged, we write the cumulated result to .env
            # .env is for compliance with docker/docker-compose standard
            print(f"writing {path_env}")
            with Path.open(path_env,"w") as file:
                file.truncate(0)
                file.write("# This file was generated automaticaly by bloom.config\n"
                        "# Don't modify values directly here\n"
                        "# Use .env.* files instead then restart application\n")
                for k,v in config.items():
                    file.write(f"{k}={v}\n")
                file.close()
                        

    srid: int = 4326

settings = Settings()
