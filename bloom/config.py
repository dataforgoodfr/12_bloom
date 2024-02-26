import os
from pathlib import Path

from pydantic import BaseSettings

def extract_values(filename:str,config:dict,allow_extend:bool=True):
    """ function that extrat key=value pairs from a file
    Parameters:
    - filename: filename/filepath from which to extract key/value pairs
    - config: dict to extend/update with new key/value pairs
    - allow_extend: allows to extend extracted keys with new keys that are not in actuel config if True,
                    restrict to already existing keys in config of False
    Returns a dict contains key/value
    """ 
    FILEPATH=Path(os.path.dirname(__file__)).joinpath(filename)
    for l in open(FILEPATH):
        # Split line at first occurence of '='. This allows to have values containing '=' character
        split=l.strip().split('=',1)
        # if extraction contains 2 items and strictly 2 items
        if(len(split)==2):
            # if extracted key already exist in config OR if allowed to add new keys to config
            # Then adding/updating key/value
            if split[0] in config.keys() or allow_extend == True:
                config[split[0].lower()]=split[1]
    return config
            
class Settings(BaseSettings):
    app_env:str=None
    db_url:str=None
    def __init__(self,*arg, **args):
        super().__init__(self,*arg, **args)
        # Default app_env is 'dev'
        self.app_env='dev'
        
        # dict to store temporary/overrided config parameters
        config={}
        # Extract .env.template as default values
        # The keys present in .env.template now will restrict keys that are extracted from following files
        # So all parameters MUST HAVE a default value declared in .env.template to be loaded
        file_to_process=Path(os.path.dirname(__file__)).joinpath(f"../.env.template")
        if os.path.isfile(file_to_process): extract_values(file_to_process,config,allow_extend=True)
        
        # Extract .env.local and override existing values
        # We restrict extracted keys to the keys already existing in .env.template
        file_to_process=Path(os.path.dirname(__file__)).joinpath(f"../.env.local")
        if os.path.isfile(file_to_process): extract_values(file_to_process,config,allow_extend=False)
        
        # Extract .env.${app_env} and override existing values
        # We restrict extracted keys to the keys already existing in .env.template
        file_to_process=Path(os.path.dirname(__file__)).joinpath(f"../.env.{self.app_env}")
        if os.path.isfile(file_to_process): extract_values(file_to_process,config,allow_extend=False)
        
        # Extract .env.${app_env}.local and override existing values
        # We restrict extracted keys to the keys already existing in .env.template
        file_to_process=Path(os.path.dirname(__file__)).joinpath(f"../.env.{self.app_env}.local")
        if os.path.isfile(file_to_process): extract_values(file_to_process,config,allow_extend=False)
        
        # Now all .env.* files has been merged, we write the cumulated result to .env
        # .env is for compliance with docker/docker-compose standard
        file_to_process=Path(os.path.dirname(__file__)).joinpath(f"../.env")
        f = open(file_to_process, "w")
        f.truncate(0)
        f.write("# This file was generated automaticaly by bloom.config\n# Don't modify values directly here\n# Use .env.* files instead then restart application")
        for k,v in config.items():
            f.write(f"{k}={v}\n")
        f.close()
        # Now we extract key/value pairs from new .env and add them to current class as attributes
        if os.path.isfile(file_to_process): extract_values(file_to_process,self.__dict__)
        
        # Set the db_url attribute containing connection string to the database
        self.db_url = ( f"postgresql://"
                        f"{self.postgres_user}:{self.postgres_password}"
                        f"@{self.postgres_hostname}:{self.postgres_port}/{self.postgres_db}")
                        

    srid: int = 4326

settings = Settings()
