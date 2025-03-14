from bloom.container import UseCases
from bloom.infra.unit_of_work import SQLAlchemyUnitOfWork

def test_unit_of_work_list_vessel():
    print("Begin Unit Of Work")
    with UseCases.unit_of_work() as uow:
        print("Begin Unit Of Work")
        print(SQLAlchemyUnitOfWork(uow).vessel_repository.get_all_vessels_list())
        print("End Unit Of Work")


if __name__ == "__main__":
    test_unit_of_work_list_vessel()