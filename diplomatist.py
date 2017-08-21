import os, sys, time, subprocess
import speech_recognition

Loopback_Capture_Path = r"LoopbackCapture\win32\csharp\LoopbackCapture\LoopbackCapture\bin\Debug\LoopbackCapture.exe"

class Diplomatist():
    def __init__(self):
        pass
    
    def transcribe(self, audio_file=None):
        recognizer = speech_recognition.Recognizer()
        if audio_file:
            with speech_recognition.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
        else:
            with speech_recognition.Microphone() as source:
                print "Say something!"
                audio = recognizer.listen(source)
        try:
            return recognizer.recognize_sphinx(audio)
        except speech_recognition.UnknownValueError:
            print "Could Not Understand"
            return False
        except speech_recognition.RequestError as e:
            print "Request Error: {0}".format(e)
            return False
    
    def record(self, audio_file):
        recognizer = speech_recognition.Recognizer()
        with speech_recognition.Microphone() as source:
            print "Say something!"
            audio = recognizer.listen(source)
        with open(audio_file, "wb") as f:
            f.write(audio.get_wav_data())
    
    def capture_loopback(self, audio_file, milliseconds):
        process = subprocess.Popen("{} {} {}".format(Loopback_Capture_Path, audio_file, milliseconds), stdout=subprocess.PIPE)
        exit_code = process.wait()
        return exit_code

if __name__ == "__main__":
    diplomatist = Diplomatist()
    audio_file = None
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    if len(sys.argv) > 2:
        milliseconds = sys.argv[2]
        diplomatist.capture_loopback(audio_file, milliseconds)
    result = diplomatist.transcribe(audio_file)
    if result:
        print result
