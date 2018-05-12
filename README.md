# flask_clova

SDK of CEK (Clova Extension Kit) for Python <br>
> All the structure and ideas were copied after seeing [flask-ask](https://github.com/johnwheeler/flask-ask)

# About flask_clova
## Table of Contents
* [Install](#install)
* [Basics](#basics)


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