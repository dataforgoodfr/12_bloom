import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any

from pydantic import (
    AliasChoices,
    AmqpDsn,
    BaseModel,
    Field,
    ImportString,
    PostgresDsn,
    RedisDsn,
    field_validator,
    model_validator
)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # validate_assignment=True allows to update db_url value as soon as one of
        # postgres_user, postgres_password, postgres_hostname, postgres_port, postgres_db
        # is modified then db_url_update is called
        validate_assignment=True,
        # env_ignore_empty=False take env as it is and if declared but empty then empty
        # the setting value
        env_ignore_empty=True,
        env_nested_delimiter='__',
        env_file='.env',
        env_file_encoding = 'utf-8',
        extra='ignore'
        )
    
    # Déclaration des attributs/paramètres disponibles au sein de la class settings
    postgres_user:str = Field(default='')
    postgres_password:str = Field(default='')
    postgres_hostname:str = Field(min_length=1,
                                  default='localhost')
    postgres_port:int = Field(gt=1024,
                                  default=5432)

    postgres_db:str = Field(min_length=1,max_length=32,pattern=r'^(?:[a-zA-Z]|_)[\w\d_]*$')
    postgres_schema:str = Field(default='public')
    srid: int = Field(default=4326)
    spire_token:str = Field(default='')
    data_folder:str=Field(default=str(Path(__file__).parent.parent.parent.joinpath('./data')))
    db_url:str=Field(default='')

    redis_host: str = Field(default='localhost')
    redis_port: int = Field(default=6379)
    redis_password: str = Field(default='bloom',min_length=1)
    redis_cache_expiration: int = Field(default=900)
    
    logging_level:str=Field(
                                default="INFO",
                                pattern=r'NOTSET|DEBUG|INFO|WARNING|ERROR|CRITICAL'
                            )
    api_key:str = Field(min_length=4,default='bloom')

    @model_validator(mode='after')
    def update_db_url(self)->dict:
        new_url= f"postgresql://{self.postgres_user}:"\
                          f"{self.postgres_password}@{self.postgres_hostname}:"\
                          f"{self.postgres_port}/{self.postgres_db}"
        if self.db_url != new_url:
           self.db_url = new_url
        return self


settings = Settings(_env_file=os.getenv('BLOOM_CONFIG',
                                    Path(__file__).parent.parent.parent.joinpath('.env')),
                    _secrets_dir=os.getenv('BLOOM_SECRETS_DIR',
                                    Path(__file__).parent.parent.parent.joinpath('./secrets')))
