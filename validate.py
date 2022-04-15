"""Find references to entities that don't exist."""
from typing import Mapping, Sequence

from homeassistant.core import valid_entity_id
from homeassistant.util.yaml import load_yaml

from entities import ENTITIES

IGNORED_KEYS = ["service"]


def scan_references(key, value, path=[]):
    if isinstance(value, str):
        if valid_entity_id(value) and value not in ENTITIES and key not in IGNORED_KEYS:
            missing_entity_ids.setdefault(value, set()).add(
                "/".join(path).replace("/[", "[")
            )
    elif isinstance(value, Mapping):
        for k, v in value.items():
            path.append(k)
            scan_references(k, v, path)
            path.pop()
    elif isinstance(value, Sequence):
        for k, v in enumerate(value):
            if isinstance(v, Mapping):
                k = v.get("alias", v.get("name", k))
            path.append(f"[{k}]")
            scan_references(None, v, path)
            path.pop()


domains = {x.split(".")[0] for x in ENTITIES}
missing_entity_ids = {}

secrets = load_yaml("../secrets.yaml")
config = load_yaml("../configuration.yaml", secrets)

scan_references(None, config)

for entity_id, paths in sorted(missing_entity_ids.items()):
    print(entity_id)
    for path in paths:
        print(f"- {path}")
    print()
