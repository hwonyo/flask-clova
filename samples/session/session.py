import logging
import os

from flask import Flask, json, render_template
from flask_clova import Clova, request, session, question, statement


app = Flask(__name__)
ask = Clova(app, "/")
logging.getLogger('flask_clova').setLevel(logging.DEBUG)


COLOR_KEY = "COLOR"


@ask.launch
def launch():
    question_text = render_template('welcome')
    reprompt_text = render_template('welcome_reprompt')
    return question(question_text).reprompt(reprompt_text)


@ask.intent('MyColorIsIntent', mapping={'color': 'Color'})
def my_color_is(color):
    if color is not None:
        session.attributes[COLOR_KEY] = color
        question_text = render_template('known_color', color=color)
        reprompt_text = render_template('known_color_reprompt')
    else:
        question_text = render_template('unknown_color')
        reprompt_text = render_template('unknown_color_reprompt')
    return question(question_text).reprompt(reprompt_text)


@ask.intent('WhatsMyColorIntent')
def whats_my_color():
    color = session.attributes.get(COLOR_KEY)
    if color is not None:
        statement_text = render_template('known_color_bye', color=color)
        return statement(statement_text)
    else:
        question_text = render_template('unknown_color_reprompt')
        return question(question_text).reprompt(question_text)


@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'CLOVA_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('CLOVA_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['CLOVA_VERIFY_REQUESTS'] = False
    app.run(debug=True)

