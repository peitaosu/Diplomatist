import os, sys
import speech_recognition


class Diplomatist():
    def __init__(self):
        pass
    
    def transcribe(self, audio_file):
        recognizer = speech_recognition.Recognizer()
        with speech_recognition.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        try:
            return recognizer.recognize_sphinx(audio)
        except speech_recognition.UnknownValueError:
            print "Could Not Understand"
            return False
        except speech_recognition.RequestError as e:
            print "Request Error: {0}".format(e)
            return False

if __name__ == "__main__":
    diplomatist = Diplomatist()
    audio_file = sys.argv[1]
    result = diplomatist.transcribe(audio_file)
    if result:
        print result
