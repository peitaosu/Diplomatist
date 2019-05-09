import os
import sys
import time
import subprocess
import optparse
import threading
import platform
import pydub
import json

import speech_recognition

if platform.system() == "Darwin":
    from LoopbackCapture.mac.LoopbackCapture import record_sounds
elif platform.system() == "Linux":
    from LoopbackCapture.linux.LoopbackCapture import record_sounds
elif platform.system() == "Windows":
    from LoopbackCapture.win32.LoopbackCapture import record_sounds

from mic import record_mic

class Diplomatist():
    def __init__(self, transcribe_api=0):
        self.load_config()
        self.set_transcribe_api(transcribe_api)
        if self.config["API"]["1"]["cred"] != "":
            import google.cloud.translate
            self.translate_client = google.cloud.translate.Client()
        os.environ["LOOPBACK_CAPTURE"] = self.config["LOOPBACK_CAPTURE"]
        if platform.system() == "Windows":
            if not os.path.isfile(os.environ["LOOPBACK_CAPTURE"]):
                print("LOOPBACK_CAPTURE error: File Not Found")
                sys.exit(-1)
        if self.config["SRT"] != "":
            self.srt_out = open(self.config["SRT"], "a")
        for proxy in self.config["PROXY"]:
            os.environ[proxy] = self.config["PROXY"][proxy]

    def load_config(self):
        with open("config.json") as in_file:
            self.config = json.load(in_file)

    def save_config(self):
        with open("config.json", "w") as out_file:
            json.dump(self.config, out_file, sort_keys=True, indent=4)

    def set_transcribe_api(self, api=0):
        self.api = api
        self.cred = None
        if "cred" in self.config["API"][str(api)] and self.config["API"][str(api)]["cred"] != "":
            cred_config = self.config["API"][str(api)]["cred"]
            if os.path.isfile(cred_config):
                with open(cred_config) as in_file:
                    self.cred = cred_config.read()
            else:
                self.cred = cred_config
        if self.api == 4:
            if platform.system() == "Windows":
                print("DeepSpeech not support Windows for now, please use other APIs.")
                sys.exit(-1)
            from deepspeech import DeepSpeechRecognizer
            self.deepspeech_recognizer = DeepSpeechRecognizer(self.config["API"]["4"]["model"], self.config["API"]["4"]["alphabet"], self.config["API"]["4"]["lm"], self.config["API"]["4"]["trie"])
        if self.api == 5:
            from azurespeech import AzureSpeechRecognizer
            self.azurespeech_recognizer = AzureSpeechRecognizer()

    def transcribe(self, language="en-US", audio_file=None):
        """transcribe audio to text

        args:
            language (str)
            audio_file (str)

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
            if self.api == 0:
                return recognizer.recognize_sphinx(audio, language)
            elif self.api == 1:
                return recognizer.recognize_google_cloud(audio, self.cred, language)
            elif self.api == 2:
                return recognizer.recognize_bing(audio, self.cred, language)
            elif self.api == 3:
                return recognizer.recognize_houndify(audio, self.cred.split(",")[0], self.cred.split(",")[1])
            elif self.api == 4:
                return self.deepspeech_recognizer.recognize(audio_file)
            elif self.api == 5:
                return self.azurespeech_recognizer.recognize(audio_file)
        except speech_recognition.UnknownValueError:
            print("Could Not Understand")
            return False
        except speech_recognition.RequestError as e:
            print("Request Error: {0}".format(e))
            return False

    def translate(self, text, language):
        """translate text to another language

        args:
            text (str)
            language (str)

        return:
            translated_text (str)
        """
        if hasattr(self, "translate_client"):
            return self.translate_client.translate(text, target_language=language)['translatedText']

    def async_transcribe(self, language="en-US", audio_file=None):
        """transcribe function for async running

        args:
            language (str)
            audio_file (str)
        """
        transc = self.transcribe(language, audio_file)
        if transc == False:
            transc = "Could Not Be Transcribed!"
        if hasattr(self, "srt_out"):
            self.srt_out.write(transc + "\n")
        print(transc)

    def async_transcribe_translate(self, transc_lan="en-US", audio_file=None, transl_lan="zh"):
        """transcribe with translate function for async running

        args:
            transc_lan (str)
            audio_file (str)
            transl_lan (str)
        """
        transc = self.transcribe(transc_lan, audio_file)
        if transc == False:
            transc = "Could Not Be Transcribed!"
        if hasattr(self, "srt_out"):
            self.srt_out.write(transc + "\n")
        print(transc)
        transl = self.translate(transc, transl_lan)
        if hasattr(self, "srt_out"):
            self.srt_out.write(transl + "\n")
        print(transl)

    def keep_running(self, language="en-US", time_slice=10000, use_mic=False, translate=None):
        """keep the process running until abort it

        args:
            language (str)
            time_slice (int)
            use_mic (bool)
            translate (str)
        """
        init_time = 0
        record_file = "record.wav"
        records_folder = self.config["RECORD"]
        if not os.path.isdir(records_folder):
            os.mkdir(records_folder)
        try:
            while True:
                start_time = time.time()
                if use_mic:
                    record_mic(record_file, time_slice)
                else:
                    record_sounds(record_file, time_slice)
                end_time = time.time()
                time_str = "{} --> {}".format(time.strftime("%H:%M:%S", time.gmtime(
                    init_time)), time.strftime("%H:%M:%S", time.gmtime(end_time - start_time + init_time)))
                if hasattr(self, "srt_out"):
                    self.srt_out.write(time_str + "\n")
                print(time_str)
                init_time = end_time - start_time + init_time
                saved_file_name = str(time.time()) + ".wav"
                saved_audio_file = os.path.join(
                    records_folder, saved_file_name)
                os.rename(record_file, saved_audio_file)
                if translate:
                    thr = threading.Thread(target=self.async_transcribe_translate, args=(
                        [language, saved_audio_file, translate]), kwargs={})
                    thr.start()
                else:
                    thr = threading.Thread(target=self.async_transcribe, args=(
                        [language, saved_audio_file]), kwargs={})
                    thr.start()
        except KeyboardInterrupt:
            print("Process was exited.")

    def run_one_time(self, language="en-US", audio_file=None, translate=None):
        """run the process one time

        args:
            language (str)
            audio_file (str)
            translate (str)
        """
        if translate:
            self.async_transcribe_translate(
                language, audio_file, translate)
        else:
            self.async_transcribe(
                language, audio_file)


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
                      help="0 - CMU Sphinx, 1 - Google Cloud, 2 - Bing API, 3 - Houndify API, 4 - Baidu DeepSpeech")
    parser.add_option("-l", "--lan", dest="language", default="en-US",
                      help="language which to be transcribed")
    parser.add_option("-t", "--tran", dest="translate", default=None,
                      help="translate to another language")
    parser.add_option("--qt", dest="ui_qt", action="store_true", default=False,
                      help="runs UI with QT")
    parser.add_option("--tk", dest="ui_tk", action="store_true", default=False,
                      help="runs UI with Tk")
    (options, args) = parser.parse_args()
    return options


if __name__ == "__main__":
    options = get_options()
    diplomatist = Diplomatist(options.api)
    if options.audio_file:
        diplomatist.run_one_time(options.language, options.audio_file, options.translate)
        sys.exit(0)
    diplomatist.keep_running(options.language, options.time_slice, options.use_mic, options.translate)
