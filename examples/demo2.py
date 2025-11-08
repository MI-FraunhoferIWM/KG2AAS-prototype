""" RDF-Knowledge Graph to AAS Demo"""
import rdflib
import json
from pyld import jsonld
from jsonschema import validate
import os
import requests
import re

import os
from rdflib import Graph, RDF, Namespace
import json
from py_aas_rdf.models.submodel import Submodel
from py_aas_rdf.models.concept_description import ConceptDescription
from py_aas_rdf.models.asset_administraion_shell import AssetAdministrationShell

AAS = Namespace("https://admin-shell.io/aas/3/0/")


cwd = os.path.dirname(__file__)

# set paths for input data
mapping_path = os.path.join(cwd, "input","mapping2.sparql")
graph_path = os.path.join(cwd, "input", "test.ttl") 
output_path = os.path.join(cwd, "output", "output2.json")

aas_json_schema = "https://raw.githubusercontent.com/admin-shell-io/aas-specs/refs/heads/master/schemas/json/aas.json"

g = rdflib.Graph()
g.parse(graph_path)
with open(mapping_path, "r", encoding="utf-8") as file:
    query = file.read()
result = g.query(query)


g = Graph().parse(data=result, format='turtle')
submodels_subjects = [subject for subject in g.subjects(predicate=RDF.type, object=AAS["Submodel"])]
assetadministrationshell_subjects = [subject for subject in g.subjects(predicate=RDF.type, object=AAS["AssetAdministrationShell"])]
conceptdescription_subjects = [subject for subject in g.subjects(predicate=RDF.type, object=AAS["ConceptDescription"])]

output = {
    "assetAdministrationShells": [ 
        AssetAdministrationShell.from_rdf(g, subject).model_dump(exclude_none=True)
        for subject in assetadministrationshell_subjects 
    ],
    "submodels": [
        Submodel.from_rdf(g, subject).model_dump(exclude_none=True)
        for subject in submodels_subjects
    ],
    "conceptDescriptions": [
        ConceptDescription.from_rdf(g, subject).model_dump(exclude_none=True)
        for subject in conceptdescription_subjects
    ]
}


# validate the output against the json schema of aas
validate(output, requests.get(aas_json_schema).json())

# write output files
with open(output_path, "w", encoding="utf-8") as file:
    file.write(json.dumps(output, indent=2))
