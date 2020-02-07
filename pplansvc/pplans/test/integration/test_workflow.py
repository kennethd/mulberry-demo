"""
End-to-end integration tests include setting up an instance of the db,
launching an instance of the app listening on a local port, and making
requests over http to test the response
"""
import json
import os
import requests
import uuid

from morus.testing.base import MorusTestCase
from morus.testing.fixtures import background_instance, unused_port

from pplans.flask.app import DEFAULT_DSN, configured_app
from pplans.warranty import WARRANTY_ERRORS


class TestPplansvcIntegration(MorusTestCase):

    def setUp(self):
        self.dsn = os.environ.get("PPLANSVC_TEST_DSN", DEFAULT_DSN)
        # testing=True will cause app to recreate db & populate test data
        self.app = configured_app('pplansvc', self.dsn, testing=True)


    def test_heartbeat(self):
        with unused_port() as port:
            with background_instance(self.app, port) as base_url:
                r = requests.get(base_url)
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.headers['content-type'], 'application/json')
                #self.assertEqual(r.encoding, 'utf-8')
                self.assertEqual(r.json(), {"pplansvc-server": "ok"})

    def test_warranties(self):
        with unused_port() as port:
            with background_instance(self.app, port) as base_url:
                url = base_url + "warranties/"

                # GET with no search criteria returns 500
                r = requests.get(url)
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.json(), {"status": WARRANTY_ERRORS["filter req"]})

                # query electronics
                r = requests.get(url + '?item_type=electronics')
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.headers['content-type'], 'application/json')
                j = r.json()[0]
                self.assertEqual(j['item_sku'], 'ELEC-999')

                # test for data provided in spec
                amys_sku = "986kjeo8fy9qhu"
                data = {
                    "item_type": "furniture",
                    "item_cost": "150.00",
                    "item_sku": amys_sku,
                    "item_title": "Amy's Sectional Sofa",
                    "store_uuid": "b21ad0676f26439",
                }

                # Amy's sofa not yet in db
                r = requests.get('{}?item_sku={}'.format(url, amys_sku))
                self.assertEqual(r.status_code, 200)
                self.assertEqual(len(r.json()), 0)

                # malformed uuid raises 500
                r = requests.post(url, data=data)
                self.assertEqual(r.status_code, 500)

                data["store_uuid"] = str(uuid.uuid4())
                r = requests.post(url, data=data)
                self.assertEqual(r.status_code, 200)

                # (furniture, 150.00) is eligible for two warranties
                r = requests.get('{}?item_sku={}'.format(url, amys_sku))
                self.assertEqual(r.status_code, 200)
                self.assertEqual(len(r.json()), 2)


    def test_constraints(self):
        with unused_port() as port:
            with background_instance(self.app, port) as base_url:
                url = base_url + "warranties/constraints"
                r = requests.get(url)
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.headers['content-type'], 'application/json')
                self.assertEqual(len(r.json()), 7)

                url = base_url + "warranties/constraints?item_type=furniture"
                r = requests.get(url)
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.headers['content-type'], 'application/json')
                self.assertEqual(len(r.json()), 5)

                url = base_url + "warranties/constraints?item_type=electronics"
                r = requests.get(url)
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.headers['content-type'], 'application/json')
                self.assertEqual(len(r.json()), 2)

