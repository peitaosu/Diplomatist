import os, sys, time, subprocess
import speech_recognition
from optparse import OptionParser

Loopback_Capture_Path = r"LoopbackCapture\win32\csharp\LoopbackCapture\LoopbackCapture\bin\Debug\LoopbackCapture.exe"

class Diplomatist():
    def __init__(self):
        pass
    
    def transcribe(self, api=0, audio_file=None, cert=None):
        recognizer = speech_recognition.Recognizer()
        if audio_file:
            with speech_recognition.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
        else:
            with speech_recognition.Microphone() as source:
                print "Say something!"
                audio = recognizer.listen(source)
        try:
            if api == 0:
                return recognizer.recognize_sphinx(audio)
            elif api == 1:
                return recognizer.recognize_google_cloud(audio, cert)
            elif api == 2:
                return recognizer.recognize_bing(audio, cert)
            elif api == 3:
                return recognizer.recognize_houndify(audio, cert.split(",")[0], cert.split(",")[1])
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

def get_options():
    parser = OptionParser()
    parser.add_option("-m", "--mic", dest="use_mic", action="store_true", default=False, 
                help="record sounds from microphone")
    parser.add_option("-f", "--file", dest="audio_file", default="record.wav", 
                help="capture sounds and save as wave file temporary")
    parser.add_option("-s", "--slice", dest="time_slice", default=10000, type="int", 
                help="time slice of each wave file")
    parser.add_option("-a", "--api", dest="api", default=0, type="int",
                help="0 - CMU Sphinx, 1 - Google Cloud, 2 - Bing API, 3 - Houndify API")
    parser.add_option("-c", "--cert", dest="cert_file", default=None,
                help="certification file if is API required")
    (options, args) = parser.parse_args()
    return options

if __name__ == "__main__":
    diplomatist = Diplomatist()
    opt = get_options()
    if opt.use_mic:
        while True:
            result = diplomatist.transcribe()
            if result:
                print result
    if opt.cert_file:
        if os.path.isfile(opt.cert_file):
            cert = open(opt.cert_file, "r").read()
        else:
            cert = opt.cert_file
    else:
        cert = None
    while True:
        diplomatist.capture_loopback(opt.audio_file, opt.time_slice)
        result = diplomatist.transcribe(opt.api, opt.audio_file, cert)
        if result:
            print result