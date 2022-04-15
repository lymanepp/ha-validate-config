"""
Use HA template to generate ENTITIES list

ENTITIES = {{ states | map(attribute='entity_id') | list | unique | set }}
"""

ENTITIES = []
