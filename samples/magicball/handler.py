"""
    Implemented example from
    https://github.com/naver/clova-extension-sample-magicball
    by flask_clova
"""
import logging
import os

from flask import Flask
from flask_clova import Clova, question, statement, say

app = Flask(__name__)
clova = Clova(app, "/")
logging.getLogger('flask_clova').setLevel(logging.DEBUG)


@clova.launch
def launch():
    speech_text = "안녕하세요? 마법구슬이에요. 무엇이든 저에게 물어보세요."
    return question(say.Korean(speech_text))


@clova.default_intent
def default_intent():
    magic_sound = "https://ssl.pstatic.net/static/clova/service/native_extensions/magicball/magic_ball_sound.mp3"
    speech = "마법 구슬이 " + get_answer() + " 라고 말합니다."
    return statement(say.Link(magic_sound))\
        .add_speech(say.Korean(speech))


@clova.session_ended
def session_ended():
    return "{}", 200


import random
def get_answer():
    ans = random.choice(answers)
    return ans


answers = [
	"그거 확실하게 될것같아", "그건 분명히 되겠어", "의심할 여지가 없어", "맞아! 확실해", "믿어도 좋겠어",
	"내가 보기엔 맞는것 같아", "거의 확실해보여", "전망이 좋아", "응, 그래", "괜찮아 보이네",
	"뭔가 흐릿흐릿하게 보이네", "지금은 잘 안보여, 나중에 다시 물어봐줘", "음...지금은 말하지 않는편이 나을것 같아",
    "지금은 잘 모르겠어", "정신을 집중하고 다시 물어봐줘",
	"꿈도 꾸지말게나", "아니라고 말해주겠네", "내가 가진 정보로는 별로야", "전망이 그리 좋진 않아", "뭔가 좀 의심스러워",
]


if __name__ == '__main__':
    if 'CLOVA_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('CLOVA_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)
