from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone, timedelta

Context = dict

@dataclass
class Partition:
    start_date:datetime
    interval:timedelta

@dataclass
class Step:
    id:str
    def pre_run(self,data,context:Optional[Context]=None):
        if not context: context = {}
        context["pre_run"]=True
        pass
    def run(self,data,context:Optional[Context]=None):
        self.pre_run(data,context=context)
        self.process(data,context=context)
        self.post_run(data,context=context)
    def process(self,data,context:Optional[Context]=None):
        return data
    def post_run(self,data,context:Optional[Context]=None):
        if not context: context = {}
        context["post_run"]=True
        pass

@dataclass
class ExtractStep(Step):
    def process(self, data, context = None):
        print("Extracting data...")
        return data
    
@dataclass
class TransformStep(Step):
    def process(self, data, context = None):
        print("Transforming data...")
        return data
    
@dataclass
class LoadStep(Step):
    def process(self, data, context = None):
        print("Loading data...")
        return data

@dataclass
class Pipeline:
    id:str
    partition:Optional[Partition]
    steps:list[Step]

    def run(self,data=None,context:Optional[Context]=None):
        if context is None: context={"pipeline_id":self.id}
        for step in self.steps:
            data=step.run(data,context=context)
        return data

