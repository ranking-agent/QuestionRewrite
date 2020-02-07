import os
import jsonschema
import yaml
import json
from sanic import Sanic, response
from apidocs import bp as apidocs_blueprint

""" Sanic server for Question Rewrite - A Swagger UI/web service. """

# initialize this web app
app = Sanic("Question rewrite")

# suppress access logging
app.config.ACCESS_LOG = False

# init the app using the paramters defined in
app.blueprint(apidocs_blueprint)

"""
a couple json segments to test the request and response

request:
    
{
  "machine_question": {
    "edges": [
      {
        "source_id": "n0",
        "target_id": "n1"
      },
      {
        "source_id": "n1",
        "target_id": "n2"
      }
    ],
    "nodes": [
      {
        "curie": "MONDO:0005737",
        "id": "n0",
        "type": "disease"
      },
      {
        "id": "n1",
        "type": "gene"
      },
      {
        "id": "n2",
        "type": "genetic_condition"
      }
    ]
  },
  "name": "the name",
  "natural_question": "What genetic conditions might provide protection against Ebola?",
  "notes": "#ebola #q1"
}
                
response:

[
    {
      "machine_question": {
        "edges": [
          {
            "source_id": "n0",
            "target_id": "n1"
          },
          {
            "source_id": "n1",
            "target_id": "n2"
          }
        ],
        "nodes": [
          {
            "curie": "MONDO:0005737",
            "id": "n0",
            "type": "disease"
          },
          {
            "id": "n1",
            "type": "gene"
          },
          {
            "id": "n2",
            "type": "genetic_condition"
          }
        ]
      },
      "name": "the name",
      "natural_question": "What genetic conditions might provide protection against Ebola?",
      "notes": "#ebola #q1"
    },
    {
      "machine_question": {
        "edges": [
          {
            "source_id": "n0",
            "target_id": "n1"
          },
          {
            "source_id": "n1",
            "target_id": "n2"
          }
        ],
        "nodes": [
          {
            "curie": "MONDO:0005737",
            "id": "n0",
            "type": "disease"
          },
          {
            "id": "n1",
            "type": "gene"
          },
          {
            "id": "n2",
            "type": "genetic_condition"
          }
        ]
      },
      "name": "the name",
      "natural_question": "What genetic conditions might provide protection against Ebola?",
      "notes": "#ebola #q1"
    }
]

"""


@app.post('/query')
async def query_handler(request):
    """ Handler for question rewrite operations. """

    # get the localtion of the Translator specification file
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # load the Translator specification
    with open(os.path.join(dir_path, 'translator_interchange_0.9.0.yaml')) as f:
        spec = yaml.load(f, Loader=yaml.SafeLoader)

    # load the query specification, first get the question node
    to_validate = spec["components"]["schemas"]["Question"]

    # then get the components in their own array so the relative references are found
    to_validate["components"] = spec["components"]

    # remove the question node because we already have it at the top
    to_validate["components"].pop("Question", None)

    try:
        # load the input into a json object
        incoming = json.loads(request.body)

        # validate the incoming json against the spec
        jsonschema.validate(instance=incoming, schema=to_validate)

    # all validation errors are manifested as a thrown exception
    except jsonschema.exceptions.ValidationError as error:
        # print (f"ERROR: {str(error)}")
        return response.json({'Query_failed_validation_message': str(error)}, status=400)

    """
    Commented out for now.
    try:
        # do the real work here. get a list of rewritten questions related to the requested one
        query_rewritten = json.loads('{}')

        # load the query response specification
        rewrite_validate = spec["components"]["schemas"]["Result"]
        
        # validate what is to be returned to insure it is also conforms to the Translator spec
        jsonschema.validate(request.json, spec)

        # if we are here the response validated properly
        return response.json("Success", status=200)
        
    # all validation errors are manifested as a thrown exception
    except jsonschema.exceptions.ValidationError as error:
        return response.json({'Response_failed_validation_message': str(error)}, status=400)
    """
    # if we are here the response validated properly
    return response.json("Success", status=200)
