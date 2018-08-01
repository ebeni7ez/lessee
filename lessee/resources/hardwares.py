from flask_restful import reqparse, Resource
from sqlalchemy import or_

from lessee.models import db, Hardware, Platform
from lessee.schemas import HardwareSchema, PlatformSchema


PLATFORMS = [
    'PS4',
    'XboxOne',
    'PC',
]


class HardwareResource(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'platform',
            type=int
        )

        data = parser.parse_args()

        if data['platform']:
            platform = Platform.query.get(data['platform'])
            hardwares = db.session.query(Hardware).filter(Hardware.platform == platform)
        else:
            hardwares = Hardware.query.all()
        result = HardwareSchema(many=True).dump(hardwares)
        return result

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'name',
            type=str,
            required=True,
            help="Name is required"
        )
        parser.add_argument(
            'ip',
            required=True,
            help="IP is required"
        )
        parser.add_argument(
            'platform',
            type=int,
            required=True,
            help="Platform is required"
        )
        data = parser.parse_args()

        platform = Platform.query.get(data['platform'])
        if Hardware.query.filter(
                or_(Hardware.name == data['name'], Hardware.ip == data['ip']),
        ).count():
            return {'message': 'Hardware already exists'}, 400

        new_hardware = Hardware(
            name=data['name'],
            ip=data['ip'],
            platform=platform,
        )
        db.session.add(new_hardware)
        db.session.commit()

        return HardwareSchema().dump(new_hardware), 201


class PlatformResource(Resource):

    def get(self):
        platforms = Platform.query.all()
        result = PlatformSchema(many=True).dump(platforms)
        return result
