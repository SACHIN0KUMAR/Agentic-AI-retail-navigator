# ui/http_api.py
# pyright: reportGeneralTypeIssues=false, reportArgumentType=false

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from impactify.graph.graph import build_graph
from langchain_core.messages import HumanMessage


app = FastAPI(title="Impactify Retail Navigator API")

graph = build_graph()
SESSION_STATE: Dict[str, Dict[str, Any]] = {}
