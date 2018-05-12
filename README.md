# flask_clova

[![PyPI](https://img.shields.io/pypi/v/flask_clova.svg?v=1&maxAge=3601)](https://pypi.python.org/pypi/flask_clova)
[![PyPI](https://img.shields.io/pypi/l/flask_clova.svg?v=1&maxAge=2592000?)](https://pypi.python.org/pypi/flask_clova)

SDK of CEK (Clova Extension Kit) for Python <br>
> All the structure and ideas were copied after seeing [flask-ask](https://github.com/johnwheeler/flask-ask)

# About flask_clova
## Table of Contents
* [Install](#install)
* [Basics](#basics)
* [WorkToDo](#worktodo)


## Install
```
git clone https://github.com/HwangWonYo/flask-clova.git
# install from PyPi will support soon
```

## Basics
```
from flask import Flask
from flask_clova import Clova, statement, question

app = Flask(__name__)
# must set CLOVA_VERIFY_REQUESTS False
# while testing wihtout application_id
# app.confing['CLOVA_VERIFY_REQUESTS'] = False

clova = Clova(app, '/user_defined')

@clova.launch
def launch():
    return question('시작했습니다')

@clova.intent('HelloIntent')
def play_game(user_name):
    speech = "안녕하세요 %s" % username
    return statement(speech).add_speech("Hello", lang='en')
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