class directive:
    @staticmethod
    def open_mike():
        return {
            "header": {
                "name": "KeepConversation",
                "namespace": "Clova"
            },
            "payload": {
                "explicit": True
            }
        }

    @staticmethod
    def emoji(label):
        """
        - Emoji directive for Briefing-ai's sentiment analysis api spec
        https://oss.navercorp.com/briefing-ai/briefing-ai-docs/wiki/감정-분석-한국어-API

        Args:
            label: 0(neutral), 1(positive), 2(negative)

        Returns:emoji character corresponding label
        """

        emoji_chars = ["U+1F610", "U+1F600", "U+1F61E"]  # neutral, happy, sad

        return {
            "header": {
                "name": "RenderTemplate",
                "namespace": "Clova"
            },
            "payload": {
                "emoji": {
                    "type": "string",
                    "value": emoji_chars[label]
                },
                "failureMessage": {
                    "type": "string",
                    "value": ""
                },
                "meta": {
                    "version": {
                        "type": "string",
                        "value": ""
                    }
                },
                "type": "TomorrowWeather"
            }
        }
