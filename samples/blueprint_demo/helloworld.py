import logging

from flask import Blueprint, render_template
from flask_clova import Clova, question, statement, say


blueprint = Blueprint('blueprint_api', __name__, url_prefix="/clova")
clova = Clova(blueprint=blueprint)

logging.getLogger('flask_clova').setLevel(logging.DEBUG)


@clova.launch
def launch():
    speech_text = render_template('welcome')
    return question(say.English(speech_text)).reprompt(say.Korean('아무도 없나요~?'))


@clova.intent('TestIntent')
def hello_world():
    speech_text = render_template('hello')
    return statement(say.English(speech_text))


@clova.session_ended
def session_ended():
    return "{}", 200