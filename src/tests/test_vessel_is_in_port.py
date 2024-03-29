import math

from bloom.logger import logger
from bloom.container import UseCases

def test_vessel_is_in_port():
    use_cases = UseCases()
    port_repository = use_cases.port_repository()
    db = use_cases.db()
    with db.session() as session:
        test_data = [
            (1, 2.2087008337345244, 51.03849547707603), # Dunkerque
            (2, 2.3567829215805722, 51.73938862920116), # in the see
        ]
        response = port_repository.find_positions_in_port_buffer(session, test_data)

    assert response[0][-1] == "Dunkerque"
    assert math.isnan(response[1][-2]) is True

if __name__ == "__main__":
    test_vessel_is_in_port()