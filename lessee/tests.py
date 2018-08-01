import json
import os

from lessee import app

import unittest

from lessee.models import db, Platform, populate_platforms, Hardware, Lease

TEST_DB = 'test.sqlite'


class BaseTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.config['BASE_DIR'], TEST_DB)

        db.drop_all()
        db.create_all()

        self.app = app.test_client()

        populate_platforms()

    def tearDown(self):
        db.session.close()
        db.drop_all()


class PlatformTest(BaseTest):

    def test_list_platforms(self):
        response = self.app.get('/platforms/')
        self.assertEqual(200, response.status_code)
        data_json = json.loads(response.data.decode())
        self.assertEqual(3, len(data_json))
        self.assertEqual(1, Platform.query.filter(Platform.name == "PC").count())
        self.assertIsNotNone(1, Platform.query.filter(Platform.name == "PS4").count())
        self.assertIsNotNone(1, Platform.query.filter(Platform.name == "XboxOne").count())


class HardwareTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.xo_platform = Platform.query.filter(Platform.name == 'XboxOne').first()
        self.ps4_platform = Platform.query.filter(Platform.name == 'PS4').first()
        self.pc_platform = Platform.query.filter(Platform.name == 'PC').first()
        Hardware(name="XYZ1", ip="123.45.6.7", platform=self.xo_platform)
        Hardware(name="XYZ2", ip="123.45.6.8", platform=self.xo_platform)
        Hardware(name="XYZ3", ip="123.45.6.9", platform=self.xo_platform)
        Hardware(name="XYZ4", ip="123.45.6.10", platform=self.ps4_platform)
        Hardware(name="XYZ5", ip="123.45.6.11", platform=self.pc_platform)

    def test_list_hardware(self):
        response = self.app.get('/hardwares/')
        self.assertEqual(200, response.status_code)
        data_json = json.loads(response.data.decode())
        self.assertEqual(5, len(data_json))

    def test_list_hardware_per_platform(self):
        url_xbox = '/hardwares/?platform={platform_id}'.format(
            platform_id=self.xo_platform.id
        )
        url_pc = '/hardwares/?platform={platform_id}'.format(
            platform_id=self.pc_platform.id
        )
        url_ps4 = '/hardwares/?platform={platform_id}'.format(
            platform_id=self.ps4_platform.id
        )
        xbox_size = Hardware.query.filter(Hardware.platform == self.xo_platform).count()
        ps4_size = Hardware.query.filter(Hardware.platform == self.ps4_platform).count()
        pc_size = Hardware.query.filter(Hardware.platform == self.pc_platform).count()

        response = self.app.get(url_xbox)
        self.assertEqual(200, response.status_code)
        data_json = json.loads(response.data.decode())
        self.assertEqual(xbox_size, len(data_json))

        response = self.app.get(url_pc)
        self.assertEqual(200, response.status_code)
        data_json = json.loads(response.data.decode())
        self.assertEqual(pc_size, len(data_json))

        response = self.app.get(url_ps4)
        self.assertEqual(200, response.status_code)
        data_json = json.loads(response.data.decode())
        self.assertEqual(ps4_size, len(data_json))

    def test_add_hardware(self):
        platform_id = self.xo_platform.id
        data = {
            "name": "XYZ12",
            "ip": "128.82.22.12",
            "platform": platform_id
        }

        response = self.app.post(
            "/hardwares/",
            json=data,
            content_type='application/json'
        )
        self.assertEqual(201, response.status_code)

        # Check hardware exists
        data_json = json.loads(response.data.decode())
        hardware = Hardware.query.get(data_json[0]['id'])
        self.assertEqual('XYZ12', hardware.name)
        self.assertEqual('128.82.22.12', str(hardware.ip))
        self.assertEqual(platform_id, hardware.platform.id)

    def test_add_hardware_same_name(self):
        platform_id = self.xo_platform.id
        data = {
            "name": "XYZ10",
            "ip": "128.82.22.10",
            "platform": platform_id
        }

        response = self.app.post(
            "/hardwares/",
            json=data,
            content_type='application/json'
        )
        self.assertEqual(201, response.status_code)

        data = {
            "name": "XYZ10",
            "ip": "128.82.22.10",
            "platform": platform_id
        }

        response = self.app.post(
            "/hardwares/",
            json=data,
            content_type='application/json'
        )
        data_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(data_json['message'], 'Hardware already exists')

    def test_add_hardware_incomplete_data(self):
        # Test name is missing
        platform_id = self.xo_platform.id
        data = {
            "ip": "128.82.22.1",
            "platform": platform_id
        }

        response = self.app.post(
            "/hardwares/",
            json=data,
            content_type='application/json'
        )
        self.assertEqual(400, response.status_code)

        data_json = json.loads(response.data.decode())
        self.assertEqual({"name": "Name is required"}, data_json['message'])

        # Test IP is missing
        data = {
            "name": "XQDW23",
            "platform": platform_id
        }

        response = self.app.post(
            "/hardwares/",
            json=data,
            content_type='application/json'
        )
        self.assertEqual(400, response.status_code)

        # Check hardware exists
        data_json = json.loads(response.data.decode())
        self.assertEqual({"ip": "IP is required"}, data_json['message'])

        # Test platform is missing
        data = {
            "name": "XQDW23",
            "ip": "128.82.22.1",
        }

        response = self.app.post(
            "/hardwares/",
            json=data,
            content_type='application/json'
        )
        self.assertEqual(400, response.status_code)

        # Check hardware exists
        data_json = json.loads(response.data.decode())
        self.assertEqual({"platform": "Platform is required"}, data_json['message'])

    def test_add_hardware_duplicated(self):
        platform_id = self.xo_platform.id
        data = {
            "name": "XYZ11",
            "ip": "128.82.22.11",
            "platform": platform_id
        }

        response = self.app.post(
            "/hardwares/",
            json=data,
            content_type='application/json'
        )
        self.assertEqual(201, response.status_code)

        # Check hardware exists
        data_json = json.loads(response.data.decode())
        hardware = Hardware.query.get(data_json[0]['id'])
        self.assertEqual(hardware.name, 'XYZ11')
        self.assertEqual(str(hardware.ip), '128.82.22.11')

        self.assertEqual(hardware.platform.id, platform_id)
        response = self.app.post(
            '/hardwares/',
            json=data,
            content_type='application/json'
        )
        data_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(data_json['message'], 'Hardware already exists')

    def test_list_hardware_empty(self):
        Hardware.query.delete()
        self.assertEqual(0, Hardware.query.count())
        response = self.app.get('/hardwares/')
        self.assertEqual(200, response.status_code)
        data_json = json.loads(response.data.decode())
        self.assertEqual(0, len(data_json))


class LeaseTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.xo_platform = Platform.query.filter(Platform.name == 'XboxOne').first()
        self.ps4_platform = Platform.query.filter(Platform.name == 'PS4').first()
        self.pc_platform = Platform.query.filter(Platform.name == 'PC').first()
        db.session.add(Hardware(name="XYZ1", ip="123.45.6.7", platform=self.xo_platform))
        db.session.commit()
        db.session.add(Hardware(name="XYZ2", ip="123.45.6.2", platform=self.xo_platform))
        db.session.commit()
        Hardware(name="XYZ4", ip="123.45.6.10", platform=self.ps4_platform)
        Hardware(name="XYZ5", ip="123.45.6.11", platform=self.pc_platform)

    def test_lease_hardware(self):
        data = {
            'duration': 20,
            'platform': self.xo_platform.id
        }
        response = self.app.post(
            '/leases/',
            json=data,
            content_type='application/json'
        )
        self.assertEqual(201, response.status_code)

    def test_lease_hardware_not_available(self):
        Hardware.query.delete()
        self.assertEqual(0, Hardware.query.count())
        data = {
            'duration': 20,
            'platform': self.xo_platform.id
        }
        response = self.app.post(
            '/leases/',
            json=data,
            content_type='application/json'
        )
        data_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)

        self.assertEqual(data_json['message'], 'Hardware not available for lease')

    def test_lease_hardware_already_leased(self):
        data = {
            'duration': 20,
            'platform': self.xo_platform.id
        }
        response = self.app.post(
            '/leases/',
            json=data,
            content_type='application/json'
        )
        self.assertEqual(201, response.status_code)

        data_json = json.loads(response.data.decode())
        hardware_first_lease = Hardware.query.get(data_json[0]['hardware']['id'])
        hardware_first_lease_id = data_json[0]['hardware']['id']
        self.assertTrue(hardware_first_lease.leased)

        response = self.app.post(
            '/leases/',
            json=data,
            content_type='application/json'
        )
        self.assertEqual(201, response.status_code)
        data_json = json.loads(response.data.decode())
        hardware_second_lease = Hardware.query.get(data_json[0]['hardware']['id'])
        hardware_second_lease_id = data_json[0]['hardware']['id']
        self.assertTrue(hardware_second_lease.leased)

        self.assertNotEqual(hardware_first_lease_id, hardware_second_lease_id)

        response = self.app.post(
            '/leases/',
            json=data,
            content_type='application/json'
        )
        self.assertEqual(400, response.status_code)
        data_json = json.loads(response.data.decode())
        self.assertEqual(data_json['message'], 'Hardware not available for lease')


if __name__ == "__main__":
    unittest.main()
