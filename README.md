# flask_clova

[![PyPI](https://img.shields.io/pypi/v/flask_clova.svg?v=1&maxAge=3601)](https://pypi.python.org/pypi/flask_clova)
[![PyPI](https://img.shields.io/pypi/l/flask_clova.svg?v=1&maxAge=2592000?)](https://pypi.python.org/pypi/flask_clova)

SDK of CEK (Clova Extension Kit) for Python <br>
> All the structure and ideas were copied after seeing [flask-ask](https://github.com/johnwheeler/flask-ask)

# About flask_clova
## Table of Contents
* [Install](#install)
* [Basics](#basics)
* [Test](#test)
* [WorkToDo](#worktodo)


## Install
```
# setup requires will automatically installed in version >= 0.0.4
# pip install PyYAML
# pip install Flask

pip install flask_clova
```

## Basics
```python
from flask import Flask
from flask_clova import Clova, statement, question, say

app = Flask(__name__)
# must set CLOVA_VERIFY_REQUESTS False
# while testing wihtout application_id
# app.config['CLOVA_VERIFY_REQUESTS'] = False

clova = Clova(app, '/user_defined')

@clova.launch
def launch():
    return question(say.Korean('시작했습니다'))

@clova.intent('HelloIntent')
def play_game():
    speech = "안녕하세요"
    return statement(say.Korean(speech)).add_speech(say.English("Hello"))

if __name__ == "__main__":
    app.config['CLOVA_VERIFY_REQUESTS'] = False
    app.run(port='5000', debug=True)
```

## Test
```
>> pip install -r requirements-dev.txt
>> python -m unittest discover test/
```


## WorkToDO

### Response
* not in progress
    - card
    - directives

#### statement
* support shouldEndSession true
    - [x] SimpleSpeech
    - [x] SpeechList
    - [ ] SpeechSet

#### question
* support shouldEndSession false
    - [x] SimpleSpeech
    - [x] SpeechList
    - [ ] SpeechSet

#### repromt
* support repromt message
    - [x] SimpleSpeech
    - [ ] SpeechList
    - [ ] SpeechSet


### Request

#### Verify
* verify application id
    - [x] verify

#### LaunchRequest
* when extension launched
    - [x] handler

#### SessionEndedRequest
* when extension terminated
    - [x] handler

#### IntentRequest
* request with user intent
    - [x] handler

#### Glboal Request Attr
* Globalize variables in request
    - [x] request
    - [x] session
    - [x] version
    - [x] context