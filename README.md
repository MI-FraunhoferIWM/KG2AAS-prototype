# Knowledge Graph to AAS Demonstration

This repository is demonstrating a simple proof of concept for the transformation of a knowledge graph (KG) written in RDF (Resource Description Framework) - which can be formulated according to PMDCo (Platform Material Digital Core Ontology), EMMO (Elementary Multiperspective Materials Ontology) or other ontologies - to an Asset Administration Shell (AAS).

This repository **does not** contain modularized and packaged software, but more of a guideline how semantic technologies like **SPARQL** and **JSON LD** can be used to transform data models between both reference frameworks, TLOs (Top level ontologies) and AAS.

## 1. General workflow

![figure1](static/AAS_KG.png)

### 1.1 As input we expecting the following implementations:

* The Knowledge graph expressed in OWL
* A SPARQL Construct Query
* A JSON LD Context Mapping
* Some minimal manual wrangling using REGEX, executed in a suitable programming language (e.g. Python) 
* The AAS Metamodel JSON Schema

### 1.2 Expected output:

* A validated AAS (serialized in JSON) with metadata from the input KG 

### 1.3 Prodcedure

#### 1.3.1 SPARQL Construct

The SPARQL query generally needs to have two parts:

* The select-part, which is traversing nodes of the input KG in OWL and fetching the metadata to be reflected in the AAS (Lower part)
* The construct-part, which is setting up the AAS datamodel according to the official AAS metamodel ontology and the corresponding AAS template of interest (Upper part)

```{sparql}
CONSTRUCT {
  <The AAS model according to the template goes here>
}
WHERE {
  <The query for fetching metadata from the KG goes here>
}
```

By using any SPARQL Engine in reference implementations like RDFLib, pyoxigraph, etc. and the SPARQL Construct defined in the previous section, we can transform the KG model into the AAS model we have defined in the query.

```{python}
import json
from rdflib import Graph

g = rdflib.Graph()
g.parse(<your-input-kg>)

result = g.query(<your-sparql-construct>).serialize(format="json-ld")
json_ld = json.loads(result)
```

The output is a AAS serialized in JSON-LD.

#### 1.3.2 JSON LD Framing

The JSON LD context is used for framing the resulting AAS in JSON LD from the previous step into the official AAS JSON Schema according. 

An extraction of an example context may look like this:

```{json}
{
  "@context": {
    "aas": "https://admin-shell.io/aas/3/0/",
    "xs": "http://www.w3.org/2001/XMLSchema#",
    "aas:value": {
        "@type": "xs:float"
    },
    "idShort": "aas:Referable/idShort",
    "modelType": {
      "@id": "@type",
      "@type": "@vocab"
    },
    "id": "aas:Identifiable/id",
    "kind": {
      "@id": "aas:HasKind/kind",
      "@type": "@vocab"
    },
    
    "qualifiers": {
      "@id": "aas:Qualifiable/qualifiers",
      "@container": "@set",
      "@context": {
        "semanticId": {
          "@id": "aas:HasSemantics/semanticId",
          "@context": {
            "type": {
              "@id": "aas:Reference/type",
              "@type": "@vocab"
            },
            "keys": {
              ...
              }
            }
          }
        }
      }

    ...

    }
```

We are working here with global and local `@contexts` in the frame, since the official AAS Json Schema is expecting keys like `value`, `type` or `valueType` in multiple objects like `Property`, `Referable` and `Qualifier`, which are expressed through different IRIs in the different contexts, such as `aas:Property/value`, `aas:Property/valueType`, `aas:Qualifier/valueType`, `aas:Qualifier/value`, etc.

The framing can be executed by using the `pyld` library in the following code snippet:

```{python}
from pyld import jsonld

json_ld = jsonld.frame(json_ld, frame)
output = jsonld.compact(json_ld, frame["@context"])
```

Depending on how well the `@context` is defined, the framing still might not lead to a JSON body, which is 100%-ly following the AAS JSON Schema. 

The current frame we have provided in this repository has issues with resolving the IRIs properly in the global and the local context hence, there still will be keys like `aas:Property/value` in the framed JSON document, which are not compliant to the AAS JSON Schema.

This leads to the current need to perfrom small operations like string replacement using REGEX and array filtering. 

At the moment, it is solved like this:

```{python}
import re
import json

# replace strings according to regex patterns
patterns = [ r'"aas:[^/"]+/([^/"]+)"', r'"aas:([^/"]+)"' ]
result = json.dumps(output,indent=2)
for pattern in patterns:
    result = re.sub(pattern["regex"], r'"\1"', result)
output = json.loads(result)

# get submodel node
for node in output["@graph"]:
    node_type = node.get("@type")
    if node_type == target_type:
        output = node
        break

```

### 1.3.3 JSON Schema validation

In order to make sure that the JSON body after framing is compliant to the AAS metamodel schema, we are applying a schema validation of our document against the official [AAS JSON Schema](https://raw.githubusercontent.com/admin-shell-io/aas-specs/refs/heads/master/schemas/json/aas.json). We can do this by using the JSON-Schema library in Python:

```{python}
import requests
from jsonschema import validate

aas_json_schema = "https://raw.githubusercontent.com/admin-shell-io/aas-specs/refs/heads/master/schemas/json/aas.json"

validate(output, requests.get(aas_json_schema).json())
```

If no error if thrown, the JSON document should be compliant towards the standard. However, the validation is expecting that the top-level object is an `AssetAdministrationShell`, not any other type like `Submodel`, `SubmodelElementCollection`, etc. since they **MUST** be embedded into the `AssetAdministrationShell`-Object.

## License

This project is licensed under the BSD 3-Clause. See the LICENSE file for more information.


## Disclaimer

Copyright (c) 2014-2024, Fraunhofer-Gesellschaft zur Förderung der angewandten Forschung e.V. acting on behalf of its Fraunhofer IWM.

Contact: [Matthias Büschelberger](mailto:matthias.bueschelberger@iwm.fraunhofer.de)
