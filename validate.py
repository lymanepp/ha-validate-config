"""Find references to entities that don't exist."""
import json
import os
from typing import Any, Mapping, Sequence

from homeassistant.core import valid_entity_id
from homeassistant.util.yaml import load_yaml

from entities import ENTITIES

IGNORED_KEYS = ["service"]


def scan_references(key, value, path=[]):
    if isinstance(value, str):
        if valid_entity_id(value):
            if value in ENTITIES:
                referenced_entity_ids.add(value)
            elif key not in IGNORED_KEYS:
                display_path = "/".join(path).replace("/[", "[")
                missing_entity_ids.setdefault(value, set()).add(display_path)
    elif isinstance(value, Mapping):
        for k, v in value.items():
            path.append(k)
            scan_references(k, v, path)
            path.pop()
    elif isinstance(value, Sequence):
        for ndx, v in enumerate(value):
            if isinstance(v, Mapping):
                ndx = v.get("alias", v.get("name", v.get("title", ndx)))
            path.append(f"[{ndx}]")
            scan_references(None, v, path)
            path.pop()

def load_json(filename: str) -> dict[str, Any]:
    path = f"../.storage/{filename}"
    if not os.path.exists(path):
        return None
    with open(path) as file:
        return json.load(file)

def load_lovelace():
    dashboards = load_json("lovelace_dashboards")
    for item in dashboards["data"]["items"]:
        id = "lovelace." + item["id"]
        dashboard = load_json(id)
        if dashboard:
            ENTITIES.append(id)
            yield dashboard

domains = {x.split(".")[0] for x in ENTITIES}
missing_entity_ids = {}
referenced_entity_ids = set()

secrets = load_yaml("../secrets.yaml")
config = load_yaml("../configuration.yaml", secrets)

scan_references(None, config)

dashboards = load_json("lovelace_dashboards")
for item in dashboards["data"]["items"]:
    id = "lovelace." + item["id"]
    dashboard = load_json(id)
    if dashboard:
        try:
            ENTITIES.append(id)
            scan_references(id, dashboard["data"]["config"])
        except LookupError:
            pass

for entity_id, paths in sorted(missing_entity_ids.items()):
    print(entity_id)
    for path in paths:
        print(f"- {path}")
    print()

#unreferenced_entity_ids = set(ENTITIES) - referenced_entity_ids
#if unreferenced_entity_ids:
#    print("Unused entities:")
#    for entity_id in sorted(unreferenced_entity_ids):
#        print(entity_id)
