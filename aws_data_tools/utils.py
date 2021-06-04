from dataclasses import asdict
from json import dumps as json_dumps
from typing import Dict, List


def tag_list_to_dict(tags: List[Dict[str, str]]) -> Dict[str, str]:
    tag_dict = {}
    for tag in tags:
        # TODO: Look into why some calls to this function are letting through tag
        # objects with no 'Key' field. For now, dropping them by catching KeyError
        try:
            tag_dict.update({tag['Key']: tag['Value']})
        except KeyError:
            continue
    return tag_dict


def dataclass_to_json(dclass) -> str:
    return json_dumps(asdict(dclass))
