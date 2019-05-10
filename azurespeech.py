import sys, subprocess
import azure.cognitiveservices.speech as speechsdk

class AzureSpeechRecognizer():
    def __init__(self, speech_key, service_region):
        self.speech_key = speech_key
        self.service_region = service_region
        self.speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.service_region)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config)

    def recognize(self, audio_file):
        """recognize audio file

        args:
            audio_file (str)

        return:
            result (str/False)
        """
        return None

