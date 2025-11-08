import os
from rdflib import Graph, RDF, Namespace
import json
from py_aas_rdf.models.submodel import Submodel
from py_aas_rdf.models.concept_description import ConceptDescription
from py_aas_rdf.models.asset_administraion_shell import AssetAdministrationShell
AAS = Namespace("https://admin-shell.io/aas/3/0/")

cwd = os.path.dirname(__file__)

input_file = os.path.join(cwd, "aas", "model2.ttl")
json_file = os.path.join(cwd,"aas", "model.json")

with open(json_file, "r") as file:
    json_object = json.loads(file.read())

g = Graph()


for shell in json_object["assetAdministrationShells"]:
    AssetAdministrationShell(**shell).to_rdf(graph=g)

for submodel in json_object["submodels"]:
    Submodel(**submodel).to_rdf(graph=g)

for descr in json_object["conceptDescriptions"]:
    ConceptDescription(**descr).to_rdf(graph=g)

with open(input_file, "w") as file:
    file.write(g.serialize())

