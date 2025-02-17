from bloom.etl import Pipeline, ExtractStep
from datetime import datetime, timezone, timedelta

class ExtractLastPipelineExecution(ExtractStep):
    def process(self, data, context=None):
        print(f"Context:{context}")
        print("ExtractLastPipelineExecution")
        return data

class ExtractNewVesselPositions(ExtractStep):
    def process(self, data, context=None):
        print(f"Context:{context}")
        print("ExtractNewVesselPositions")
        return data

class CreateUpdateExcursionsSegmentsPipeline(Pipeline):
    pass
    