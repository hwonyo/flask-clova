import unittest
import six
import mock

from flask import Flask
from flask_clova import Clova, session, request

@unittest.skipIf(six.PY2, "Not yet supported on Python 2.x")
class SmokeTestUsingSamples(unittest.TestCase):
    def setUp(self):
        _app = Flask('__TEST__')
        self.app = _app
        self.clova = Clova(app=_app, route="/")

    def tearDown(self):
        pass

    def test_configuration_variables(self):

        #test CLOVA_APPLICATION_ID
        with self.app.app_context():
            self.assertIsNone(self.clova.clova_application_id)

            self.app.config['CLOVA_APPLICATION_ID'] = 1234
            self.assertEqual(self.clova.clova_application_id, 1234)

        #test CLOVA_VERIFY_REQUESTS
        with self.app.app_context():
            self.assertTrue(self.clova.clova_verify_requests)

            self.app.config['CLOVA_VERIFY_REQUESTS'] = False
            self.assertFalse(self.clova.clova_verify_requests)

        #test CLOVA_PRETTY_DEBUG_LOGS
        with self.app.app_context():
            self.assertIsNone(self.app.config.get('CLOVA_PRETTY_DEBUS_LOGS'))

    def test_launch_request(self):
        counter = mock.MagicMock()
        @self.clova.launch
        def launch():
            counter()
            return "ok"

        req = {
            "version": "0.1.0",
            "context": {},
            "request": {
                "type": "LaunchRequest"
            }
        }
        with self.app.test_client() as client:
            rv = client.post('/', json=req)
            self.assertEqual('200 OK', rv.status)

        self.assertEqual(counter.call_count, 1)

    def test_default_intent_request(self):
        counter = mock.MagicMock()
        @self.clova.default_intent
        def default_intent():
            self.assertEqual(session, {'sessionAttributes': {}})
            counter()
            return "ok"

        req = {
            "version": "0.1.0",
            "session": {},
            "context": {},
            "request": {
                "type": "IntentRequest",
                "intent": {
                    "name": "test_intent",
                    "slots": {}
                }
            }
        }
        with self.app.test_client() as client:
            rv = client.post('/', json=req)
            self.assertEqual('200 OK', rv.status)

        self.assertEqual(counter.call_count, 1)

    def test_intent_request(self):
        counter = mock.MagicMock()
        # test intent using slots
        @self.clova.intent(
            'test_intent',
            mapping={'param1': 'parameterA', 'param2': 'parameterB'},
            convert={'param1': int, 'parma2': int},
            default={'param1': 1, 'param2': 2}
        )
        def test_intent(param1, param2):
            self.assertEqual(param1, 45)
            self.assertEqual(param2, 2)
            counter()
            return "ok"

        req = {
            "version": "0.1.0",
            "session": {},
            "context": {},
            "request": {
                "type": "IntentRequest",
                "intent": {
                    "name": "test_intent",
                    "slots": {
                        'parameterA': {
                            'name': 'parameterA',
                            'value': '45'
                        }
                    }
                }
            }
        }

        with self.app.test_client() as client:
            rv = client.post('/', json=req)
            self.assertEqual('200 OK', rv.status)

        self.assertEqual(counter.call_count, 1)

    def test_end_session(self):
        counter = mock.MagicMock()
        @self.clova.session_ended
        def end_session():
            counter()
            return "ok"
        req = {
            "version": "0.1.0",
            "session": {},
            "context": {},
            "request": {
                "type": "SessionEndedRequest",
            }
        }
        with self.app.test_client() as client:
            rv = client.post('/', json=req)
            self.assertEqual(rv.status, '200 OK')

        self.assertEqual(counter.call_count, 1)

    def test_on_session_callback(self):
        counter = mock.MagicMock()
        @self.clova.on_session_started
        def session_func():
            counter()
        req = {
            "version": "0.1.0",
            "session": {
                'new': False
            },
            "context": {},
            "request": {
                'type': 'fool'
            }
        }

        with self.app.test_client() as client:
            rv = client.post('/', json=req)

        self.assertEqual(counter.call_count, 0)

        with self.app.test_client() as client:
            req["session"]["new"] = True
            rv = client.post('/', json=req)

        self.assertEqual(counter.call_count, 1)

if __name__ == "__main__":
    unittest.run()