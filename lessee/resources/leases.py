import datetime

from flask_restful import reqparse, Resource
from sqlalchemy import desc

from lessee import db
from lessee.models import Platform, Hardware, Lease
from lessee.schemas import LeaseSchema


class LeaseResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('active', type=bool)
        data = parser.parse_args()
        if data['active']:
            now = datetime.datetime.now()
            leases = Lease.query.filter(
                Lease.start < now,
                Lease.end > now,
            ).order_by(desc(Lease.end))
        else:
            leases = Lease.query.order_by(desc(Lease.end)).all()
        result = LeaseSchema(many=True).dump(leases)
        return result

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument(
            'duration',
            required=True,
            help="Duration is required"
        )
        parser.add_argument(
            'platform',
            type=int,
            required=True,
            help="Platform is required"
        )
        data = parser.parse_args()

        platform = Platform.query.get(data['platform'])

        if not platform:
            return {'message': 'Specify an existing platform'}, 400

        hardware_list = db.session.query(Hardware).filter(
            Hardware.platform == platform,
        )

        available_hardware = None

        # Find first available hardware
        for hardware in hardware_list:
            if hardware.status == 'available':
                available_hardware = hardware
                break

        if not available_hardware:
            return {'message': 'Hardware not available for lease'}, 400

        now = datetime.datetime.now()
        new_lease = Lease(
            hardware=available_hardware,
            start=now,
            end=now + datetime.timedelta(minutes=int(data['duration']))
        )
        db.session.add(new_lease)
        db.session.commit()

        return LeaseSchema().dump(new_lease), 201
