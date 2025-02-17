
from bloom.container import UseCases
from bloom.domain.vessel import Vessel
from bloom.infra.database import sql_model

          
if __name__ == "__main__":
    with UseCases.uow() as uow:
        print(uow.repository_vessel.get_all_vessels_list())
