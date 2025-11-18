"""Pytest for KG2AAS conversion"""

import os
import json
from jsonschema import validate
import os
import requests

from rdflib import Graph, RDF, Namespace
from pyoxigraph import Store, RdfFormat

from py_aas_rdf.models.submodel import Submodel
from py_aas_rdf.models.concept_description import ConceptDescription
from py_aas_rdf.models.asset_administraion_shell import AssetAdministrationShell


PATH = os.path.dirname(__file__)
EXAMPLES_PATH = os.path.join(PATH, "..", "examples")
INPUTS_PATH = os.path.join(EXAMPLES_PATH, "input")
OUTPUTS_PATH = os.path.join(EXAMPLES_PATH, "output")
AAS_PATH = os.path.join(EXAMPLES_PATH, "aas")

def test_conversion():
    mapping_file = os.path.join(INPUTS_PATH, "mapping2.sparql")
    test_file = os.path.join(INPUTS_PATH, "test.ttl")
    expected_output = os.path.join(OUTPUTS_PATH, "output2.json")

    AAS = Namespace("https://admin-shell.io/aas/3/0/")

    aas_json_schema = "https://raw.githubusercontent.com/admin-shell-io/aas-specs/refs/heads/master/schemas/json/aas.json"
    unique_id = "https://materials-data.space/uid123"
    placeholder = "https://example.org"

    with open(mapping_file, "r", encoding="utf-8") as file:
        query = file.read()
    query = query.replace(placeholder, unique_id)

    store = Store()
    store.load(path=test_file, format=RdfFormat.TURTLE)
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
    with open(expected_output, "r", encoding="utf-8") as file:
        assert json.load(file) == output
