import datetime

from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import IPAddressType

from lessee import db

PLATFORM_LIST = (
    'PC',
    'PS4',
    'XboxOne',
)


def populate_platforms():
    platforms = Platform.query.all()
    if not platforms:
        for platform_name in PLATFORM_LIST:
            new_platform = Platform(name=platform_name)
            db.session.add(new_platform)
            db.session.commit()


class BaseMixin(object):
    id = db.Column(
        db.Integer,
        index=True,
        autoincrement=True,
        primary_key=True
    )


class TimestampMixin(object):
    created_at = db.Column(
        db.DateTime,
        default=func.now()
    )
    modified_at = db.Column(
        db.DateTime,
        default=func.now(),
        onupdate=func.now()
    )


class Platform(db.Model, BaseMixin):
    name = db.Column(db.String(50), unique=True)
    hardwares = db.relationship('Hardware', backref='platform', lazy=True)

    def __init__(self, name):
        self.name = name


class Hardware(db.Model, BaseMixin, TimestampMixin):
    name = db.Column(
        db.String(80),
        unique=True,
    )
    ip = db.Column(
        IPAddressType,
        unique=True,
    )
    platform_id = db.Column(
        db.Integer,
        db.ForeignKey('platform.id'),
    )
    leases = db.relationship('Lease', backref='hardware', lazy='dynamic')
    __table_args__ = (
        db.UniqueConstraint(
            'ip',
            'platform_id',
            'name',
        ),
    )

    def __init__(self, name, ip, platform):
        self.name = name
        self.ip = ip
        self.platform = platform

    @hybrid_property
    def leased(self):
        if self.status == 'leased':
            return True
        return False

    @hybrid_property
    def status(self):
        lease_query = Lease.query.filter_by(
            hardware_id=self.id
        )
        if lease_query.count():
            now = datetime.datetime.now()
            if lease_query.filter(
                Lease.start < now,
                Lease.end > now,
            ).count():
                return 'leased'
        return 'available'


class Lease(db.Model, BaseMixin, TimestampMixin):
    hardware_id = db.Column(
        db.Integer,
        db.ForeignKey('hardware.id'),
    )
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    def __init__(self, hardware, start, end):
        self.hardware = hardware
        self.start = start
        self.end = end