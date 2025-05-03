from enum import Enum
from pydantic import BaseModel
from typing import Optional


class ParameterOption(BaseModel):
    label: str
    value: str


class Parameter(BaseModel):
    description: str
    default: Optional[str] = None
    options: Optional[list[ParameterOption]] = None


class ViewType(Enum):
    Articles = 0
    SocialMedia = 1
    Pictures = 2
    Videos = 3
    Audios = 4
    Notifications = 5


class RouteItem(BaseModel):
    path: str | list[str]
    name: str
    url: Optional[str] = None
    mantainers: Optional[list[str]] = None
    example: Optional[str] = None
    categories: Optional[list[str]] = None
    parameters: Optional[dict[str, str | Parameter]] = None
    description: Optional[str] = None
    features: Optional[dict] = None  # ignored beacause it is not used in the code
    rader: Optional[list[dict]] = None  # ignored beacause it is not used in the code
    view: Optional[ViewType] = None


class NamespaceItem(BaseModel):
    routes: dict[str, RouteItem]
