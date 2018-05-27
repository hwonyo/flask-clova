import logging
import os

from flask import Flask
from flask_clova import Clova, question, statement

app = Flask(__name__)
clova = Clova(app, "/")
logging.getLogger('flask_clova').setLevel(logging.DEBUG)


@clova.launch
def launch():
    speech_text = 'Welcome to the CEK World'
    return question(speech_text, lang='en').reprompt('Re ' + speech_text, lang='en')


@clova.intent('TestIntent', mapping={'test_slot': 'TestSlot'})
def hello_world(test_slot):
    speech_text = 'Hello world'
    return statement(speech_text, lang='en')\
                .add_speech(test_slot, lang='en')


@clova.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'CLOVA_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('CLOVA_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)
