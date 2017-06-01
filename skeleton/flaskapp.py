from flask import Flask
from flask_restful import Api

from skeleton.restresources import TestResource

SECRET_KEY = 'CHANGEME: flask-session-insecure-secret-key'

def create_app():

    app = Flask(__name__)
    app.config.from_object(__name__)

    api = Api(app)
    api.add_resource(TestResource, '/')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
