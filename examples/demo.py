""" RDF-Knowledge Graph to AAS Demo"""
import rdflib
import json
from pyld import jsonld
from jsonschema import validate
import os
import requests
import re

cwd = os.path.dirname(__file__)

# set paths for input data
mapping_path = os.path.join(cwd, "input","mapping.sparql")
frame_path = os.path.join(cwd, "input", "frame_slim.json")
graph_path = os.path.join(cwd, "input", "test.ttl") 
output_path = os.path.join(cwd,"output", "output.json")
output_ld_path = os.path.join(cwd,"output", "output-jsonld.json")

# set parameters
patterns = [
    {
        "regex": r'"aas:[^/"]+/([^/"]+)"',
        "replacement": r'"\1"'
    },
    {
        "regex": r'"aas:([^/"]+)"',
        "replacement": r'"\1"'
    }
]
target_type = "Submodel"
aas_json_schema = "https://raw.githubusercontent.com/admin-shell-io/aas-specs/refs/heads/master/schemas/json/aas.json"

# parse input graph and apply query to transform into AAS in json-ld
g = rdflib.Graph()
g.parse(graph_path)
with open(mapping_path, "r", encoding="utf-8") as file:
    query = file.read()
result = g.query(query).serialize(format="json-ld")
json_ld = json.loads(result)

# apply @context for framing and compacting
with open(frame_path, "r", encoding="utf-8") as file:
    frame = json.loads(file.read())
json_ld = jsonld.frame(json_ld, frame)
output = jsonld.compact(json_ld, frame["@context"])

# replace ids
result = json.dumps(output,indent=2)
for pattern in patterns:
    result = re.sub(pattern["regex"], pattern["replacement"], result)
output = json.loads(result)

# get submodel node
for node in output["@graph"]:
    node_type = node.get("@type")
    if node_type == target_type:
        output = node
        break

# validate the output against the json schema of aas
validate(output, requests.get(aas_json_schema).json())

# write output files
with open(output_path, "w", encoding="utf-8") as file:
    file.write(json.dumps(output, indent=2))

with open(output_ld_path, "w", encoding="utf-8") as file:
    file.write(json.dumps(json_ld, indent=2))
