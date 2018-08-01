from os.path import join, isfile
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)

if isfile(join('instance', 'flask_full.cfg')):
    app.config.from_pyfile('flask_full.cfg')
else:
    app.config.from_pyfile('flask.cfg')

app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

api = Api(app)

CORS(app)

from lessee.resources.hardwares import HardwareResource, PlatformResource
from lessee.resources.leases import LeaseResource

api.add_resource(HardwareResource, '/hardwares/')
api.add_resource(PlatformResource, '/platforms/')
api.add_resource(LeaseResource, '/leases/')


@app.route('/')
def hello_world():
    return 'Hello, World!'

