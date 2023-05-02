


class Fleet:

    def __init__(self,vessels:dict):

        self.vessels = vessels

    def __repr__(self):
        return f"Fleet(n_vessels={len(self.vessels)})"

    def tolist(self):
        return list(self.vessels.values())

    def chunk_data(self,max_duration_hours = 1):
        for vessel_id in list(self.vessels.keys()):
            self.vessels[vessel_id].chunk_data(max_duration_hours)