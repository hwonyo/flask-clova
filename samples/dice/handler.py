"""
    Implemented example from
    https://github.com/naver/clova-extension-sample-dice
    by flask_clova
"""
import logging
import os

from flask import Flask
from flask_clova import Clova, question, statement, session, say

app = Flask(__name__)
clova = Clova(app, "/")
logging.getLogger('flask_clova').setLevel(logging.DEBUG)


@clova.launch
def launch():
    speech_text = "몇개의 주사위를 던질까요?"
    session.sessionAttributes['intent'] = 'ThrowDiceIntent'

    return question(say.Korean(speech_text))


@clova.intent('ThrowDiceIntent',
            mapping={'dice_cnt': 'diceCount'},
            convert={'dice_cnt': int},
            default={'dice_cnt': 1})
def throw_handler(dice_cnt):
    speech = "주사위를 " + str(dice_cnt) + "개 던집니다."
    dice_sound = os.path.join(os.getcwd(), "rolling_dice_sound.mp3")
    result_text = get_answer(dice_cnt)

    return statement(say.Korean(speech))\
        .add_speech(say.Link(dice_sound))\
        .add_speech(say.Korean(result_text))


@clova.intent('Clova.GuideIntent')
def guide_intent():
    return question(say.Korean("주사위 한 개 던져줘, 라고 시도해보세요."))


@clova.session_ended
def session_ended():
    return statement(say.Korean("주사위 놀이 익스텐션을 종료합니다."))


def get_answer(dice_cnt):
    text, total = throw_dice(dice_cnt)
    if dice_cnt == 1:
        return "결과는 {}입니다.".format(total)
    if dice_cnt < 4:
        return "결과는 {}이며 합은 {}입니다.".format(text, total)
    return "주사위 {}개의 합은 {}입니다.".format(dice_cnt, total)


import random
import math
def throw_dice(dice_cnt):
    text = ''
    total = 0
    for i in range(dice_cnt):
        rand = math.floor(random.random() * 6 + 1)
        total += rand
        text += "{}, ".format(rand)
    else:
        text = text[:-2]
    return text, total


if __name__ == '__main__':
    if 'CLOVA_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('CLOVA_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)