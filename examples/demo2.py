""" RDF-Knowledge Graph to AAS Demo"""
import json
from jsonschema import validate
import os
import requests

from rdflib import Graph, RDF, Namespace
from pyoxigraph import Store, RdfFormat

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


with open(mapping_path, "r", encoding="utf-8") as file:
    query = file.read()

store = Store()
store.load(path=graph_path, format=RdfFormat.TURTLE)
result = store.query(query)


g = Graph().parse(data=result.serialize(format=RdfFormat.TURTLE), format="turtle")
submodels_subjects = [subject for subject in g.subjects(predicate=RDF.type, object=AAS["Submodel"])]
assetadministrationshell_subjects = [subject for subject in g.subjects(predicate=RDF.type, object=AAS["AssetAdministrationShell"])]
conceptdescription_subjects = [subject for subject in g.subjects(predicate=RDF.type, object=AAS["ConceptDescription"])]

output = {
    "assetAdministrationShells": [ 
        AssetAdministrationShell.from_rdf(g, subject).model_dump(exclude_none=True, mode="json")
        for subject in assetadministrationshell_subjects 
    ],
    "submodels": [
        Submodel.from_rdf(g, subject).model_dump(exclude_none=True, mode="json")
        for subject in submodels_subjects
    ],
    "conceptDescriptions": [
        ConceptDescription.from_rdf(g, subject).model_dump(exclude_none=True, mode="json")
        for subject in conceptdescription_subjects
    ]
}

# validate the output against the json schema of aas
validate(output, requests.get(aas_json_schema).json())

# write output files
with open(output_path, "w", encoding="utf-8") as file:
    file.write(json.dumps(output, indent=2))
