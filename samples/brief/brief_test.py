import logging
import os

from flask import Flask
from flask_clova import Clova, question, statement, brief

app = Flask(__name__)
clova = Clova(app, "/")
logging.getLogger('flask_clova').setLevel(logging.DEBUG)


@clova.intent('TestIntent', mapping={'test_slot': 'TestSlot'})
def brief_test(test_slot):
    return brief('This is test for brief', lang='en')\
        .add_speech(test_slot, lang='en')\
        .add_speech('두번째 테스트')


if __name__ == '__main__':
    if 'CLOVA_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('CLOVA_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)
