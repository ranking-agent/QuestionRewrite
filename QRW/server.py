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


response:


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
    query_validate = spec["components"]["schemas"]["Query"]

    try:
        # validate the incoming json against the spec
        jsonschema.validate(request.json, query_validate)

    # all validation errors are manifested as a thrown exception
    except jsonschema.exceptions.ValidationError as error:
        # print (f"ERROR: {str(error)}")
        return response.json({'Query_failed_validation_message': str(error)}, status=400)

    # do the real work here. get a list of rewritten questions related to the requested one
    query_rewritten = json.dumps({})

    # load the query response specification
    rewrite_validate = spec["components"]["schemas"]["Result"]

    try:
        # validate what is to be returned to insure it is also conforms to the Translator spec
        jsonschema.validate(request.json, rewrite_validate)

        # if we are here the response validated properly
        return response.json(query_rewritten.json, status=200)

    # all validation errors are manifested as a thrown exception
    except jsonschema.exceptions.ValidationError as error:
        # print (f"ERROR: {str(error)}")
        return response.json({'Response_failed_validation_message': str(error)}, status=400)
