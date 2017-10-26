import os
import sys
import time
import subprocess
import optparse
import threading
import platform
import pydub

import speech_recognition

if platform.system() == "Darwin":
    from LoopbackCapture.mac.LoopbackCapture import record_sounds
elif platform.system() == "Linux":
    from LoopbackCapture.linux.LoopbackCapture import record_sounds
elif platform.system() == "Windows":
    from LoopbackCapture.win32.LoopbackCapture import record_sounds


class Diplomatist():
    def __init__(self):
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            import google.cloud.translate
            self.translate_client = google.cloud.translate.Client()
        if "OUT_SRT" in os.environ:
            self.out = open(os.environ["OUT_SRT"], "a")

    def transcribe(self, api=0, audio_file=None, cred=None, language="en-US"):
        """transcribe audio to text

        args:
            api (0 - CMU Sphinx, 1 - Google Cloud, 2 - Bing API, 3 - Houndify API)
            audio_file (str)
            cred (str)
            language (str)

        return:
            result (str/False)
        """
        audio_file_ext = audio_file.split(".")[-1]
        if audio_file_ext is not "wav" and audio_file_ext is not "aif":
            ori_audio_file = pydub.AudioSegment.from_file(
                audio_file, audio_file_ext)
            audio_file = audio_file.replace(audio_file_ext, "wav")
            exp_audio_file = ori_audio_file.export(audio_file, format="wav")
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

    def record_mic(self, audio_file=None):
        """record microphone and save to file

        args:
            audio_file (str)
        """
        recognizer = speech_recognition.Recognizer()
        with speech_recognition.Microphone() as source:
            print "Say something!"
            audio = recognizer.listen(source)
        if audio_file is None:
            audio_file = "record.wav"
        with open(audio_file, "wb") as f:
            f.write(audio.get_wav_data())

    def capture_loopback(self, audio_file, milliseconds):
        """capture system loopback with specific milliseconds and save to file

        args:
            audio_file (str)
            milliseconds (int)

        return:
            exit_code (int)
        """
        exit_code = record_sounds(audio_file, milliseconds)
        return exit_code

    def translate(self, text, language):
        """translate text to another language

        args:
            text (str)
            language (str)

        return:
            translated_text (str)
        """
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            return self.translate_client.translate(text, target_language=language)['translatedText']

    def async_transcribe(self, api=0, audio_file=None, cred=None, language="en-US"):
        """transcribe function for async running

        args:
            api (0 - CMU Sphinx, 1 - Google Cloud, 2 - Bing API, 3 - Houndify API)
            audio_file (str)
            cred (str)
            language (str)
        """
        transc = self.transcribe(api, audio_file, cred, language)
        if transc == False:
            transc = "Could Not Be Transcribed!"
        if hasattr(self, "out"):
            self.out.write(transc + "\n")
        print transc

    def async_transcribe_translate(self, api=0, audio_file=None, cred=None, transc_lan="en-US", transl_lan="zh"):
        """transcribe with translate function for async running

        args:
            api (0 - CMU Sphinx, 1 - Google Cloud, 2 - Bing API, 3 - Houndify API)
            audio_file (str)
            cred (str)
            transc_lan (str)
            transl_lan (str)
        """
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

    def keep_running(self, cred, options):
        """keep the process running until abort it

        args:
            cred (str)
            options (OptionParser)
        """
        init_time = 0
        record_file = "record.wav"
        records_folder = "records"
        if not os.path.isdir(records_folder):
            os.mkdir(records_folder)
        try:
            while True:
                start_time = time.time()
                if options.use_mic:
                    self.record_mic(record_file)
                else:
                    self.capture_loopback(record_file, options.time_slice)
                end_time = time.time()
                time_str = "{} --> {}".format(time.strftime("%H:%M:%S", time.gmtime(
                    init_time)), time.strftime("%H:%M:%S", time.gmtime(end_time - start_time + init_time)))
                if hasattr(self, "out"):
                    self.out.write(time_str + "\n")
                print time_str
                init_time = end_time - start_time + init_time
                saved_file_name = str(time.time()) + ".wav"
                saved_audio_file = os.path.join(
                    records_folder, saved_file_name)
                os.rename(record_file, saved_audio_file)
                if options.translate:
                    thr = threading.Thread(target=self.async_transcribe_translate, args=(
                        [options.api, saved_audio_file, cred, options.language, options.translate]), kwargs={})
                    thr.start()
                else:
                    thr = threading.Thread(target=self.async_transcribe, args=(
                        [options.api, saved_audio_file, cred, options.language]), kwargs={})
                    thr.start()
        except KeyboardInterrupt:
            print "Process was exited."

    def run_one_time(self, cred, options):
        """run the process one time

        args:
            cred (str)
            options (OptionParser)
        """
        if options.translate:
            self.async_transcribe_translate(
                options.api, options.audio_file, cred, options.language, options.translate)
        else:
            self.async_transcribe(
                options.api, options.audio_file, cred, options.language)


def get_options():
    """get options
    """
    parser = optparse.OptionParser()
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
    parser.add_option("-p", "--proxy", dest="proxy", default=None,
                      help="set http/https proxy")    
    (options, args) = parser.parse_args()
    return options


if __name__ == "__main__":
    if platform.system() == "Windows":
        os.environ["LOOPBACK_CAPTURE"] = r"LoopbackCapture\win32\csharp\LoopbackCapture\LoopbackCapture\bin\Debug\LoopbackCapture.exe"
    opt = get_options()
    if opt.proxy:
        os.environ["http_proxy"] = opt.proxy
        os.environ["https_proxy"] = opt.proxy
    if opt.credential:
        if os.path.isfile(opt.credential):
            cred = open(opt.credential, "r").read()
        else:
            cred = opt.credential
        if opt.translate:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = opt.credential
        else:
            cred = None
    else:
        cred = None
    if opt.output:
        os.environ["OUT_SRT"] = opt.output
    diplomatist = Diplomatist()
    if opt.audio_file:
        diplomatist.run_one_time(cred, opt)
        sys.exit(0)
    diplomatist.keep_running(cred, opt)
