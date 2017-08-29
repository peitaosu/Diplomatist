import os, sys, time, subprocess
import speech_recognition
from optparse import OptionParser
import google.cloud.translate
import threading

Loopback_Capture_Path = r"LoopbackCapture\win32\csharp\LoopbackCapture\LoopbackCapture\bin\Debug\LoopbackCapture.exe"

class Diplomatist():
    def __init__(self):
        self.translate_client = google.cloud.translate.Client()
    
    def transcribe(self, api=0, audio_file=None, cred=None):
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
                return recognizer.recognize_google_cloud(audio, cred)
            elif api == 2:
                return recognizer.recognize_bing(audio, cred)
            elif api == 3:
                return recognizer.recognize_houndify(audio, cred.split(",")[0], cred.split(",")[1])
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
    
    def translate(self, text, language):
        return self.translate_client.translate(text, target_language=language)['translatedText']
    
    def async_transcribe_translate(self, api=0, audio_file=None, cred=None, language="zh"):
        transc = self.transcribe(api, audio_file, cred)
        print transc
        transl = self.translate(transc, language)
        print transl

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
    parser.add_option("-c", "--cred", dest="credential", default=None,
                help="credential file if is API required")
    parser.add_option("-t", "--tran", dest="translate", default="en_zh",
                help="translate to another language")
    (options, args) = parser.parse_args()
    return options


if __name__ == "__main__":
    opt = get_options()
    if opt.credential:
        if os.path.isfile(opt.credential):
            cred = open(opt.credential, "r").read()
        else:
            cred = opt.credential
        if opt.translate:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = opt.credential
    else:
        cred = None
    diplomatist = Diplomatist()
    if opt.use_mic:
        while True:
            result = diplomatist.transcribe()
            if result:
                print result
    while True:
        diplomatist.capture_loopback(opt.audio_file, opt.time_slice)
        if opt.translate:
            diplomatist.async_transcribe_translate(opt.api, opt.audio_file, cred, opt.translate.split("_")[1])
        else:
            result = diplomatist.transcribe(opt.api, opt.audio_file, cred)
            if result:
                print result
                if opt.translate:
                    thr = threading.Thread(target=diplomatist.translate, args=([result, opt.translate.split("_")[1]]), kwargs={})
                    thr.start()
