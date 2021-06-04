from typing import ClassVar, Type

from marshmallow import Schema
from marshmallow_dataclass import dataclass


@dataclass
class ModelBase:
    Schema: ClassVar[Type[Schema]] = Schema
