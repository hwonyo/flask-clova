"""
Smoke test using the samples.
"""

import unittest
import os
import six
import sys
import time
import subprocess

from requests import post

import flask_clova

launch = {
  "version": "0.1.0",
  "session": {
    "new": True,
    "sessionAttributes": {},
    "sessionId": "a29cfead-c5ba-474d-8745-6c1a6625f0c5",
    "user": {
      "userId": "V0qe",
      "accessToken": "XHapQasdfsdfFsdfasdflQQ7"
    }
  },
  "context": {
    "System": {
      "application": {
        "applicationId": "com.yourdomain.extension.fakebot"
      },
      "user": {
        "userId": "V0qe",
        "accessToken": "XHapQasdfsdfFsdfasdflQQ7"
      },
      "device": {
        "deviceId": "096e6b27-1717-33e9-b0a7-510a48658a9b",
        "display": {
          "size": "l100",
          "orientation": "landscape",
          "dpi": 96,
          "contentLayer": {
            "width": 640,
            "height": 360
          }
        }
      }
    }
  },
  "request": {
    "type": "LaunchRequest"
  }
}

intent_req = {
  "version": "0.1.0",
  "session": {
    "new": False,
    "sessionAttributes": {},
    "sessionId": "a29cfead-c5ba-474d-8745-6c1a6625f0c5",
    "user": {
      "userId": "V0qe",
      "accessToken": "XHapQasdfsdfFsdfasdflQQ7"
    }
  },
  "context": {
    "System": {
      "application": {
        "applicationId": "com.yourdomain.extension.pizzabot"
      },
      "user": {
        "userId": "V0qe",
        "accessToken": "XHapQasdfsdfFsdfasdflQQ7"
      },
      "device": {
        "deviceId": "096e6b27-1717-33e9-b0a7-510a48658a9b",
        "display": {
          "size": "l100",
          "orientation": "landscape",
          "dpi": 96,
          "contentLayer": {
            "width": 640,
            "height": 360
          }
        }
      }
    }
  },
  "request": {
    "type": "IntentRequest",
    "intent": {
      "name": "TestIntent",
      "slots": {
        "TestSlotType": {
          "name": "TestSlot",
          "value": "TestValue"
        }
      }
    }
  }
}

session_end = {
  "version": "0.1.0",
  "session": {
    "new": False,
    "sessionAttributes": {},
    "sessionId": "a29cfead-c5ba-474d-8745-6c1a6625f0c5",
    "user": {
      "userId": "V0qe",
      "accessToken": "XHapQasdfsdfFsdfasdflQQ7"
    }
  },
  "context": {
    "System": {
      "application": {
        "applicationId": "com.yourdomain.extension.pizzabot"
      },
      "user": {
        "userId": "V0qe",
        "accessToken": "XHapQasdfsdfFsdfasdflQQ7"
      },
      "device": {
        "deviceId": "096e6b27-1717-33e9-b0a7-510a48658a9b",
        "display": {
          "size": "l100",
          "orientation": "landscape",
          "dpi": 96,
          "contentLayer": {
            "width": 640,
            "height": 360
          }
        }
      }
    }
  },
  "request": {
    "type": "SessionEndedRequest"
  }
}


project_root = os.path.abspath(os.path.join(flask_clova.__file__, '../..'))


@unittest.skipIf(six.PY2, "Not yet supported on Python 2.x")
class SmokeTestUsingSamples(unittest.TestCase):
    """ Try launching each sample and sending some requests to them. """

    def setUp(self):
        self.python = sys.executable
        self.env = {'PYTHONPATH': project_root,
                    'ASK_VERIFY_REQUESTS': 'false'}

    def _launch(self, sample):
        prefix = os.path.join(project_root, 'samples/')
        path = prefix + sample
        process = subprocess.Popen([self.python, path], env=self.env)
        time.sleep(1)
        self.assertIsNone(process.poll(),
                          msg='Poll should work,'
                          'otherwise we failed to launch')
        self.process = process

    def _post(self, route='/', data={}):
        url = 'http://127.0.0.1:5000' + str(route)
        print('POSTing to %s' % url)
        response = post(url, json=data)
        self.assertEqual(200, response.status_code)
        return response

    @staticmethod
    def _get_text(http_response):
        data = http_response.json()
        return data.get('response', {})\
                   .get('outputSpeech', {})

    @staticmethod
    def _get_reprompt(http_response):
        data = http_response.json()
        return data.get('response', {})\
                   .get('reprompt', {})\
                   .get('outputSpeech', {})

    @staticmethod
    def _get_response(http_response):
        data = http_response.json()
        return data.get('response')

    def tearDown(self):
        try:
            self.process.terminate()
            self.process.communicate(timeout=1)
        except Exception as e:
            try:
                print('[%s]...trying to kill.' % str(e))
                self.process.kill()
                self.process.communicate(timeout=1)
            except Exception as e:
                print('Error killing test python process: %s' % str(e))
                print('*** it is recommended you manually kill with PID %s',
                      self.process.pid)

    def test_helloworld(self):
        """ Test the HelloWorld sample project """
        self._launch('helloworld/helloworld.py')
        response = self._post(data=launch)
        self.assertEqual(
            {
                'card': {},
                'directives': [],
                'outputSpeech':{
                    'type': 'SimpleSpeech',
                    'values': {
                        'type': 'PlainText',
                        'lang': 'en',
                        'value': 'Welcome to the CEK World'
                    }
                },
                'reprompt': {
                    'outputSpeech': {
                        'type': 'SimpleSpeech',
                        'values': {
                            'type': 'PlainText',
                            'lang': 'en',
                            'value': 'Re Welcome to the CEK World'
                        }
                    }
                },
                'shouldEndSession': False,
            },
            self._get_response(response)
        )

        #check intent
        response = self._post(data=intent_req)
        self.assertEqual(
            {
                'card': {},
                'directives': [],
                'outputSpeech': {
                    'type': 'SpeechList',
                    'values': [
                        {
                            'type': 'PlainText',
                            'lang': 'en',
                            'value': 'Hello world'
                        },
                        {
                            'type': 'PlainText',
                            'lang': 'en',
                            'value': 'TestValue'
                        }
                    ]
                },
                'shouldEndSession': True,
            },
            self._get_response(response)
        )

    #
    # def test_session_sample(self):
    #     """ Test the Session sample project """
    #     self._launch('session/session.py')
    #     response = self._post(data=launch)
    #     self.assertTrue('favorite color' in self._get_text(response))

    def test_blueprints_demo(self):
        """ Test the sample project using Flask Blueprints """
        self._launch('blueprint_demo/demo.py')

        response = self._post(route='/clova', data=launch)
        self.assertTrue(
            {
                'card': {},
                'directives': [],
                'outputSpeech': {
                    'type': 'SimpleSpeech',
                    'values': {
                        'type': 'PlainText',
                        'lang': 'en',
                        'value': 'Welcome to the Clova Extension Kit, you can say hello'
                    }
                },
                'reprompt': {
                    'outputSpeech': {
                        'type': 'SimpleSpeech',
                        'values': {
                            'type': 'PlainText',
                            'lang': 'ko',
                            'value': '아무도 없나요~?'
                        }
                    }
                },
                'shouldEndSession': False,
            },
            self._get_response(response)
        )

        response = self._post(route='/clova', data=intent_req)
        self.assertEqual(
            {
                'card': {},
                'directives': [],
                'outputSpeech': {
                    'type': 'SimpleSpeech',
                    'values': {
                        'type': 'PlainText',
                        'lang': 'en',
                        'value': 'Hello world!'
                    }
                },
                'shouldEndSession': True,
            },
            self._get_response(response)
        )

        response = self._post(route='/clova', data=session_end)
        print(response.headers)
        self.assertIsNone(self._get_response(response))