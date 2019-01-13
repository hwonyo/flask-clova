# Say namespace for making Speech
class say:
    # LanguageType
    KOREAN   = "ko"
    ENGLISH  = "en"
    JAPANESE = "ja"

    @staticmethod
    def Korean(text):
        return SpeechText(text, say.KOREAN)

    @staticmethod
    def English(text):
        return SpeechText(text, say.ENGLISH)

    @staticmethod
    def Japanese(text):
        return SpeechText(text, say.JAPANESE)

    @staticmethod
    def Link(link):
        return SpeechLink(link)

class SpeechText:
    def __init__(self, value, lang):
        self.value = value
        self.lang  = lang

    def render_template(self):
        return {
            "type": "PlainText",
            "lang": self.lang,
            "value": self.value,
        }

class SpeechLink:
    def __init__(self, value):
        self.value = value

    def render_template(self):
        return {
            "type": "URL",
            "lang": "",
            "value": self.value
        }