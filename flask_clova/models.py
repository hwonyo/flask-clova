from flask import json
from .core import session, context, dbgdump


class _Field(dict):
    """Container to represent CEK Request Data.

    Initialized with request_json and creates a dict object with attributes
    to be accessed via dot notation or as a dict key-value.

    Parameters within the request_json that contain their data as a json object
    are also represented as a _Field object.

    Example:

    payload_object = _Field(cek_json_payload)

    request_type_from_keys = payload_object['request']['type']
    request_type_from_attrs = payload_object.request.type

    assert request_type_from_keys == request_type_from_attrs
    """

    def __init__(self, request_json={}):
        super(_Field, self).__init__(request_json)
        for key, value in request_json.items():
            if isinstance(value, dict):
                value = _Field(value)
            self[key] = value

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)


class _Response(object):

    def __init__(self, speech, url=False, lang='ko'):
        self._response = {
            'card': {},
            'directives': [],
            'outputSpeech':
                {
                    'type': 'SimpleSpeech',
                    'values': _output_speech(speech, url=url, lang=lang)
                }
        }

    def add_speech(self, speech, url=False, lang='ko'):
        return self._add(_output_speech(speech, url, lang))

    def _add(self, value):
        self._response['outputSpeech']['type'] = 'SpeechList'
        values = self._response['outputSpeech']['values']
        if not isinstance(values, list):
            values = [values]

        values.append(value)
        self._response['outputSpeech']['values'] = values
        return self

    def render_response(self):
        sessionAttributes = session.sessionAttributes
        if sessionAttributes is None:
            sessionAttributes = {}

        response_wrapper = {
            'version': '0.1.0',
            'response': self._response,
            'sessionAttributes': sessionAttributes
        }
        dbgdump(response_wrapper)

        return json.dumps(response_wrapper)


class statement(_Response):

    def __init__(self, speech, url=False, lang='ko'):
        super(statement, self).__init__(speech, url=url, lang=lang)

        self._response['shouldEndSession'] = True


class question(_Response):

    def __init__(self, speech, url=False, lang='ko'):
        super(question, self).__init__(speech, url, lang)

        self._response['shouldEndSession'] = False

    def reprompt(self, reprompt, url=False, lang='ko'):
        """
        Only support repromt type SimpleSpeech now
        """
        reprompt = {
            'outputSpeech': {
                'type': 'SimpleSpeech',
                'values': _output_speech(reprompt, lang=lang, url=url)
            }
        }
        self._response['reprompt'] = reprompt
        return self

    def reprompt_add(self):
        """
        In preparing...
        """
        return self


class brief(_Response):
    #To Do
    pass


def _copyattr(src, dest, attr, convert=None):
    if attr in src:
        value = src[attr]
        if convert is not None:
            value = convert(value)
        setattr(dest, attr, value)


def _output_speech(speech,  url=False, lang='ko'):
    return {
        'type': 'PlainText' if not url else 'URL',
        'lang': lang if not url else '',
        'value': speech
    }