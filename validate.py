"""Find references to entities that don't exist."""
from typing import Mapping, Sequence

from homeassistant.util.yaml import load_yaml

from entities import ENTITIES

IGNORED_KEYS = ["service"]


def find_references(key, value):
    if key in IGNORED_KEYS:
        return
    # 'str' is also a 'Sequence' and must be first
    if isinstance(value, str):
        parts = value.split(".")
        if len(parts) == 2 and parts[0] in domains and value not in ENTITIES:
            missing_entity_ids.add(value)
    elif isinstance(value, Mapping):
        for k, v in value.items():
            find_references(k, v)
    elif isinstance(value, Sequence):
        for v in value:
            find_references(key, v)


domains = {x.split(".")[0] for x in ENTITIES}
missing_entity_ids = set()

secrets = load_yaml("../secrets.yaml")
config = load_yaml("../configuration.yaml", secrets)

for k, v in config.items():
    find_references(k, v)

for entity_id in sorted(missing_entity_ids):
    print(entity_id)
