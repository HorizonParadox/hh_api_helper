from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel


class ChildArea(BaseModel):
    id: str
    parent_id: str
    name: str
    areas: List


class ParentArea(BaseModel):
    id: str
    parent_id: str
    name: str
    areas: List[ChildArea]


class ModelItem(BaseModel):
    id: str
    parent_id: Any
    name: str
    areas: List[ParentArea]


class Model(BaseModel):
    RootModel: List[ModelItem]