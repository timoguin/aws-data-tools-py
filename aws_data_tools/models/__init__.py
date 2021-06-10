from dataclasses import asdict, dataclass, is_dataclass
from json import dumps as json_dumps
from typing import Any, Dict

from yaml import dump as yaml_dump


@dataclass
class ModelBase:
    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if not k.startswith("_")}

    def as_json(self) -> str:
        return json_dumps(self.as_dict(), default=str)

    def as_yaml(self) -> str:
        return yaml_dump(self.as_dict())
