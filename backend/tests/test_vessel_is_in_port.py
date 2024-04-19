import math

from bloom.logger import logger
from bloom.services import geo

def test_vessel_is_in_port():
    test_data = [
        (1, 2.2087008337345244, 51.03849547707603), # Dunkerque
        (2, 2.3567829215805722, 51.73938862920116), # in the see
    ]
    response = geo.find_positions_in_port_buffer(test_data)

    assert response[0][-1] == "Dunkerque"
    assert math.isnan(response[1][-2]) is True

if __name__ == "__main__":
    test_vessel_is_in_port()