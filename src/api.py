from typing import Any, Dict, List, Union
from fastapi import FastAPI
import logging

app = FastAPI()

@app.post("/custom")
def dummy(request_dict: Union[List,Dict,Any]=None):
    logging.warn(f"Query dict: {request_dict}")
    return {"a": "b"}