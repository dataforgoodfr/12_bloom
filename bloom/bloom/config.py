import os
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
        if k.lower() in [f"{k}_FILE".lower() for k in config.keys()]\
            and ( k.removesuffix('_FILE').lower() in config.keys() or  allow_extend == True)\
            and Path(v).is_file():
                with Path.open(v, mode='r') as file:
                    config[k.removesuffix('_FILE').lower()]=file.readline().strip()
        # Processing of direct affectation via ATTR=VALUE
        # if extracted key already exist in config OR if allowed to add new keys to config
        # Then adding/updating key/value
        if k.lower() in [k.lower() for k in config.keys()] or allow_extend == True:
            config[k.lower()]=v
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
                if k.lower() in [f"{k}_FILE".lower() for k in config.keys()]\
                    and ( k.removesuffix('_FILE').lower() in config.keys() or  allow_extend == True)\
                    and Path(v).is_file():
                        with Path(v).open( mode='r') as file_value:
                            config[k.removesuffix('_FILE').lower()]=file_value.readline().strip()
                # if extracted key already exist in config OR if allowed to add new keys to
                # config then adding/updating key/value
                if k.lower() in [k.lower() for k in config.keys()] or allow_extend == True:
                    config[k.lower()]=v
            # If env priority True, then overriding all values with ENV values before ending
            if env_priority:
                extract_values_from_env(config,allow_extend=False)
    return config


class Settings(BaseSettings):
    # Déclaration des attributs/paramètres disponibles au sein de la class settings
    postgres_user:str = None
    postgres_password:str = None
    postgres_hostname:str = None
    postgres_port:str = None
    postgres_db:str = None
    srid: int = 4326
    db_url:str = None
    spire_toekn:str = None
    
    def __init__(self):
        super().__init__(self)
        # Default values
        srid: int = 4326
        
        # Si le fichier de configuration à charger est précisé par la variable d'environnement
        # BLOOM_CONFIG alors on charge ce fichier, sinon par défaut c'est ../.env
        BLOOM_CONFIG=os.getenv('BLOOM_CONFIG',"../../.env")
        
        # Ici on charge les paramètres à partir du fichier BLOOM_CONFIG
        # et on mets à jour directement les valeurs des paramètres en tant qu'attribut de la
        # la classe courante Settings en attanquant le self.__dict__
        # Ces variables sont systmétiquement convertie en lower case
        # 
        # allow_extend=False précise que seuls les attributs déjà existants dans la config
        # passée en paramètres (ici self.__dict__) sont mis à jour. Pas de nouveau paramètres
        # Cela singifie que pour rendre accessible un nouveau paramètre il faut le déclaré
        # dans la liste des attributs de la classe Settings
        #
        # env_priority=true signifie que si un paramètres est présent dans la classe Settings,
        # mas aussi dans le fichier BLOOM_CONFIG ainsi qu'en tant que variable d'environnement
        # alors c'est la valeur de la variable d'environnement qui sera chargée au final
        # La priorité est donnée aux valeur de l'environnement selon le standard Docker
        extract_values_from_file(APP_CONFIG,self.__dict__,allow_extend=False,env_priority=True)
    
        self.db_url = ( f"postgresql://{self.postgres_user}:"
                  f"{self.postgres_password}@{self.postgres_hostname}:"
                  f"{self.postgres_port}/{self.postgres_db}")


settings = Settings()
