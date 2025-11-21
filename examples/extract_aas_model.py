"""Demo how to write an AAS to RDF"""

import os

from basyx.aas import model
from basyx.aas.adapter.aasx import AASXReader, DictSupplementaryFileContainer
from basyx.aas.adapter.json import write_aas_json_file
from basyx.aas.adapter.rdf import write_aas_rdf_file

cwd = os.path.dirname(__file__)

aasx_path = os.path.join(cwd, "aas", "model.aasx")
json_path = os.path.join(cwd, "aas", "model.json")
ttl_path = os.path.join(cwd, "aas", "model.ttl")

objects = model.DictObjectStore()
files = DictSupplementaryFileContainer()
with AASXReader(aasx_path) as reader:
    metadata = reader.get_core_properties()
    reader.read_into(objects, files)

    write_aas_rdf_file(ttl_path, objects)
    write_aas_json_file(json_path, objects, indent=4)
