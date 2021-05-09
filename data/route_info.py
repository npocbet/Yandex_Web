import flask

blueprint = flask.Blueprint(
    'route_info',
    __name__,
    template_folder='templates'
)
