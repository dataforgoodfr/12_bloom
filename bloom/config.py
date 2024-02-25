import os

from pydantic import BaseSettings

class Settings(BaseSettings):
    
    postgres_user:str = None
    postgres_password:str = None
    postgres_hostname:str = None
    postgres_db:str = None
    postgres_port:str = None
    db_url:str = None
    
    def __init__(self):
        super().__init__(self)
        # Loading of settings from SECRET file content or direct ENV value
        # All ENV values with ATTR_FILE suffix are interpreted as filepath to read as ATTR value
        # All ENV values without _FILE suffix are interpreted direct ATTR value
        if "POSTGRES_USER" not in os.environ and  "POSTGRES_USER_FILE" not in os.environ:
            raise ValueError("POSTGRES_USER or POSTGRES_USER_FILE must be defined in ENV")
        else:
            try: f = open(os.environ.get("POSTGRES_USER_FILE"))
            except TypeError: pass
            except FileNotFoundError: pass
            else:
                with f: self.postgres_user = f.readline().strip()
            if os.environ.get("POSTGRES_USER") != None : self.postgres_user = os.environ.get("POSTGRES_USER")
        
        if "POSTGRES_PASSWORD" not in os.environ and  "POSTGRES_PASSWORD_FILE" not in os.environ:
            raise ValueError("POSTGRES_PASSWORD or POSTGRES_PASSWORD_FILE must be defined in ENV")
        else:
            try: f = open(os.environ.get("POSTGRES_PASSWORD_FILE"))
            except TypeError: pass
            except FileNotFoundError: pass
            else:
                with f: self.postgres_password = f.readline().strip()
            if os.environ.get("POSTGRES_PASSWORD") != None: self.postgres_password = os.environ.get("POSTGRES_PASSWORD")
        
        if "POSTGRES_HOSTNAME" not in os.environ and  "POSTGRES_HOSTNAME_FILE" not in os.environ:
            raise ValueError("POSTGRES_HOSTNAME or POSTGRES_HOSTNAME_FILE must be defined in ENV")
        else:
            try: f = open(os.environ.get("POSTGRES_HOSTNAME_FILE"))
            except TypeError: pass
            except FileNotFoundError: pass
            else:
                with f: self.postgres_hostname = f.readline().strip()
            if os.environ.get("POSTGRES_HOSTNAME") != None: self.postgres_hostname = os.environ.get("POSTGRES_HOSTNAME")
        
        if "POSTGRES_DB" not in os.environ and  "POSTGRES_DB_FILE" not in os.environ:
            raise ValueError("POSTGRES_DB or POSTGRES_DB_FILE must be defined in ENV")
        else:
            try: f = open(os.environ.get("POSTGRES_DB_FILE"))
            except TypeError: pass
            except FileNotFoundError: pass
            else:
                with f: self.postgres_db = f.readline().strip()
            if os.environ.get("POSTGRES_DB") != None : self.postgres_db = os.environ.get("POSTGRES_DB")
        
        if "POSTGRES_PORT" not in os.environ and  "POSTGRES_PORT_FILE" not in os.environ:
            raise ValueError("POSTGRES_PORT or POSTGRES_PORT_FILE must be defined in ENV")
        else:
            try: f = open(os.environ.get("POSTGRES_PORT_FILE"))
            except TypeError: pass
            except FileNotFoundError: pass
            else:
                with f: self.postgres_port = f.readline().strip()
            if os.environ.get("POSTGRES_PORT") != None: self.postgres_port = os.environ.get("POSTGRES_PORT")

        self.db_url = (
            "postgresql://"
            + self.postgres_user
            + ":"
            + self.postgres_password
            + "@"
            + self.postgres_hostname
            + ":"
            + self.postgres_port
            + "/"
            + self.postgres_db
        )

    srid: int = 4326


settings = Settings()
