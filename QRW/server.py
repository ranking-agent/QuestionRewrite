"""Sanic server for Question Rewrite placeholder - A Swagger UI/web service."""
import json
import os

from sanic import Sanic, response

from apidocs import bp as apidocs_blueprint

app = Sanic()
app.config.ACCESS_LOG = False
app.blueprint(apidocs_blueprint)

async def service_startup(app, loop):
    """Start up any DB or service connections."""
    pass


async def service_shutdown(app, loop):
    """Shut down any DB or service connection."""
    pass


@app.route('/get')
async def get_handler(request):
    """ place holder for Question rewrite operations.
        Use GET for single item, MGET for multiple.
    """
    if isinstance(request.args['key'], list):
        return response.json({"returned payload, multiple items passed in"})
    else:
        return response.json({"returned payload, single items passed in"})


app.register_listener(service_startup, 'after_start')
app.register_listener(service_shutdown, 'before_stop')
