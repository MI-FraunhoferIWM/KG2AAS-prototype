"""RDF-Knowledge Graph to AAS Demo"""

import json
import os

import requests
from jsonschema import validate
from py_aas_rdf.models.asset_administraion_shell import \
    AssetAdministrationShell
from py_aas_rdf.models.concept_description import ConceptDescription
from py_aas_rdf.models.submodel import Submodel
from pyoxigraph import RdfFormat, Store
from rdflib import RDF, Graph, Namespace

AAS = Namespace("https://admin-shell.io/aas/3/0/")
unique_id = "https://materials-data.space/uid456"
placeholder = "https://example.org"
aas_json_schema = "https://raw.githubusercontent.com/admin-shell-io/aas-specs/refs/heads/master/schemas/json/aas.json"


# set paths for input data
cwd = os.path.dirname(__file__)
mapping_path = os.path.join(cwd, "input", "mapping3.sparql")
graph_path = os.path.join(cwd, "input", "test2.ttl")
output_path = os.path.join(cwd, "output", "output3.json")

# open mapping
with open(mapping_path, "r", encoding="utf-8") as file:
    query = file.read().replace(placeholder, unique_id)

store = Store()
store.load(path=graph_path, format=RdfFormat.TURTLE)
result = store.query(query)


g = Graph().parse(data=result.serialize(format=RdfFormat.TURTLE), format="turtle")
submodels_subjects = [
    subject for subject in g.subjects(predicate=RDF.type, object=AAS["Submodel"])
]
assetadministrationshell_subjects = [
    subject
    for subject in g.subjects(
        predicate=RDF.type, object=AAS["AssetAdministrationShell"]
    )
]
conceptdescription_subjects = [
    subject
    for subject in g.subjects(predicate=RDF.type, object=AAS["ConceptDescription"])
]

output = {
    "assetAdministrationShells": [
        AssetAdministrationShell.from_rdf(g, subject).model_dump(
            exclude_none=True, mode="json"
        )
        for subject in assetadministrationshell_subjects
    ],
    "submodels": [
        Submodel.from_rdf(g, subject).model_dump(exclude_none=True, mode="json")
        for subject in submodels_subjects
    ],
    "conceptDescriptions": [
        ConceptDescription.from_rdf(g, subject).model_dump(
            exclude_none=True, mode="json"
        )
        for subject in conceptdescription_subjects
    ],
}

# validate the output against the json schema of aas
# validate(output, requests.get(aas_json_schema).json())

# write output files
with open(output_path, "w", encoding="utf-8") as file:
    file.write(json.dumps(output, indent=2))
