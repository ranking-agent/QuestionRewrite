import os
import jsonschema
import yaml
import json
from sanic import Sanic, response
from apidocs import bp as apidocs_blueprint

""" Sanic server for Question Rewrite placeholder - A Swagger UI/web service. """

# initialize this web app
app = Sanic()

# suppress access logging
app.config.ACCESS_LOG = False

# init the app using the paramters defined in
app.blueprint(apidocs_blueprint)

"""
a couple json segments to test the request and response

request:

    {
        "asynchronous": "false",
        "bypass_cache": "true",
        "max_results": 10,
        "page_number": 1,
        "query_message":
        {
            "original_question": "A question?"
        }
    }

{"asynchronous":"false","bypass_cache":"true","max_results":10,"page_number":1,"query_message":{"original_question":"A question?"}}
    
    
response:

    {
        ?
    }

"""


@app.route('/get')
async def get_handler(request):
    """ Handler for question rewrite operations. """

    # get the localtion of the Translator specification file
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # load the Translator specification
    with open(os.path.join(dir_path, 'translator_interchange_0.9.0.yaml')) as f:
        spec = yaml.load(f, Loader=yaml.SafeLoader)

    # load the query specification
    schema = spec["components"]["schemas"]["Query"]

    try:
        # load the input into a json object
        incoming = json.loads(request.args['query'][0])

        # validate the incoming json against the spec
        jsonschema.validate(instance=incoming, schema=schema)

    # all validation errors are manifested as a thrown exception
    except Exception as error:
        # jsonschema.exceptions.ValidationError as error:
        # print (f"ERROR: {str(error)}")
        return response.json({'Query_failed_validation_message': str(error)}, status=400)

    # do the real work here. get a list of rewritten questions related to the requested one
    query_rewritten = json.loads('{}')

    # load the query response specification
    rewrite_validate = spec["components"]["schemas"]["Result"]

    try:
        # validate what is to be returned to insure it is also conforms to the Translator spec
        # jsonschema.validate(request.json, rewrite_validate)

        # if we are here the response validated properly
        return response.json("Success", status=200)

    # all validation errors are manifested as a thrown exception
    except jsonschema.exceptions.ValidationError as error:
        # print (f"ERROR: {str(error)}")
        return response.json({'Response_failed_validation_message': str(error)}, status=400)
