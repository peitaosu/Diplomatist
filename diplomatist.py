import os, sys, time, subprocess
import speech_recognition
from optparse import OptionParser
import google.cloud.translate
import threading

class Diplomatist():
    def __init__(self):
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            self.translate_client = google.cloud.translate.Client()
        if "OUT_SRT" in os.environ:
            self.out = open(os.environ["OUT_SRT"], "a")
    
    def transcribe(self, api=0, audio_file=None, cred=None, language="en-US"):
        recognizer = speech_recognition.Recognizer()
        with speech_recognition.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        try:
            if api == 0:
                return recognizer.recognize_sphinx(audio, language)
            elif api == 1:
                return recognizer.recognize_google_cloud(audio, cred, language)
            elif api == 2:
                return recognizer.recognize_bing(audio, cred, language)
            elif api == 3:
                return recognizer.recognize_houndify(audio, cred.split(",")[0], cred.split(",")[1])
        except speech_recognition.UnknownValueError:
            print "Could Not Understand"
            return False
        except speech_recognition.RequestError as e:
            print "Request Error: {0}".format(e)
            return False
    
    def record(self, audio_file=None):
        recognizer = speech_recognition.Recognizer()
        with speech_recognition.Microphone() as source:
            print "Say something!"
            audio = recognizer.listen(source)
        if audio_file is None:
            audio_file = "record.wav"
        with open(audio_file, "wb") as f:
            f.write(audio.get_wav_data())
    
    def capture_loopback(self, audio_file, milliseconds):
        if "LOOPBACK_CAPTURE" not in os.environ:
            print "Please set the %LOOPBACK_CAPTURE% before you start to capture."
        Loopback_Capture_Path = os.environ["LOOPBACK_CAPTURE"]
        process = subprocess.Popen("{} {} {}".format(Loopback_Capture_Path, audio_file, milliseconds), stdout=subprocess.PIPE)
        exit_code = process.wait()
        return exit_code
    
    def translate(self, text, language):
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            return self.translate_client.translate(text, target_language=language)['translatedText']
    
    def async_transcribe(self, api=0, audio_file=None, cred=None, language="en-US"):
        transc = self.transcribe(api, audio_file, cred, language)
        if transc == False:
            transc = "Could Not Be Transcribed!"
        if hasattr(self, "out"):
            self.out.write(transc + "\n")
        print transc

    def async_transcribe_translate(self, api=0, audio_file=None, cred=None, transc_lan="en-US", transl_lan="zh"):
        transc = self.transcribe(api, audio_file, cred, transc_lan)
        if transc == False:
            transc = "Could Not Be Transcribed!"
        if hasattr(self, "out"):
            self.out.write(transc + "\n")
        print transc
        transl = self.translate(transc, transl_lan)
        if hasattr(self, "out"):
            self.out.write(transl + "\n")
        print transl
    
    def keep_running(self, record_file, cred, options):
        init_time = 0
        while True:
            start_time = time.time()
            if options.use_mic:
                self.record(record_file)
            else:
                self.capture_loopback(record_file, options.time_slice)
            end_time = time.time()
            time_str = "{} --> {}".format(time.strftime("%H:%M:%S", time.gmtime(init_time)), time.strftime("%H:%M:%S", time.gmtime(end_time - start_time + init_time)))
            if hasattr(self, "out"):
                self.out.write(time_str + "\n")
            print time_str
            init_time = end_time - start_time + init_time
            saved_file_name = str(time.time()) + ".wav"
            saved_audio_file = os.path.join(records_folder, saved_file_name)
            os.rename(record_file, saved_audio_file)
            if options.translate:
                thr = threading.Thread(target=self.async_transcribe_translate, args=([options.api, saved_audio_file, cred, options.language, options.translate]), kwargs={})
                thr.start()
            else:
                thr = threading.Thread(target=self.async_transcribe, args=([options.api, saved_audio_file, cred, options.language]), kwargs={})
                thr.start()

    def run_one_time(self, cred, options):
        if options.translate:
            self.async_transcribe_translate(options.api, options.audio_file, cred, options.language, options.translate)
        else:
            self.async_transcribe(options.api, options.audio_file, cred, options.language)

def get_options():
    parser = OptionParser()
    parser.add_option("-m", "--mic", dest="use_mic", action="store_true", default=False, 
                help="record sounds from microphone")
    parser.add_option("-f", "--file", dest="audio_file", default=None, 
                help="audio file which to be transcribed and translated")
    parser.add_option("-s", "--slice", dest="time_slice", default=10000, type="int", 
                help="time slice of each wave file")
    parser.add_option("-a", "--api", dest="api", default=0, type="int",
                help="0 - CMU Sphinx, 1 - Google Cloud, 2 - Bing API, 3 - Houndify API")
    parser.add_option("-c", "--cred", dest="credential", default=None,
                help="credential file if is API required")
    parser.add_option("-l", "--lan", dest="language", default="en-US",
                help="language which to be transcribed")
    parser.add_option("-t", "--tran", dest="translate", default=None,
                help="translate to another language")
    parser.add_option("-o", "--out", dest="output", default=None,
                help="output the result as SRT file")
    (options, args) = parser.parse_args()
    return options


if __name__ == "__main__":
    os.environ["LOOPBACK_CAPTURE"] = r"LoopbackCapture\win32\csharp\LoopbackCapture\LoopbackCapture\bin\Debug\LoopbackCapture.exe"
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
    if opt.output:
        os.environ["OUT_SRT"] = opt.output
    diplomatist = Diplomatist()
    if opt.audio_file:
        diplomatist.run_one_time(cred, opt)
    records_folder = "records"
    if not os.path.isdir(records_folder):
        os.mkdir(records_folder)
    record_file = "record.wav"
    diplomatist.keep_running(record_file, cred, opt)