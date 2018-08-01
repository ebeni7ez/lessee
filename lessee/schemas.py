import datetime

from flask_marshmallow import Marshmallow
from marshmallow import fields

from lessee import app

ma = Marshmallow(app)


class PlatformSchema(ma.Schema):
    name = fields.String(required=True)
    id = fields.Integer(dump_only=True)

    class Meta:
        fields = (
            'id',
            'name',
        )


class HardwareSchema(ma.Schema):
    platform = fields.Nested(PlatformSchema, only=["name"])
    ip = fields.String()

    class Meta:
        fields = (
            'id',
            'name',
            'leased',
            'platform',
            'ip',
        )


class LeaseSchema(ma.Schema):
    hardware = fields.Nested(HardwareSchema)
    active = fields.Function(lambda obj: obj.start < datetime.datetime.now() <= obj.end)

    class Meta:
        fields = (
            'hardware',
            'start',
            'end',
            'active',
        )