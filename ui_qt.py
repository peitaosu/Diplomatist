import sys
import thread
import platform
if platform.system() == "Darwin":
    import site
    site.addsitedir("/usr/local/lib/python2.7/site-packages")
try:
    from PyQt4 import QtCore, QtGui, uic
    from PyQt4.QtGui import QMainWindow, QApplication
except:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic
    from PyQt5.QtWidgets import QMainWindow, QApplication
from diplomatist import *

qt_ui_file = "ui_qt.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_ui_file)


class Diplomatist_Qt(QMainWindow, Ui_MainWindow):
    transc_changed = QtCore.pyqtSignal(str)
    transl_changed = QtCore.pyqtSignal(str)

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

    def change_transc(self, transc):
        self.text_transc.setText(transc)

    def change_transl(self, transl):
        self.text_transl.setText(transl)


os.environ["LOOPBACK_CAPTURE"] = r"LoopbackCapture\win32\csharp\LoopbackCapture\LoopbackCapture\bin\Debug\LoopbackCapture.exe"

options = get_options()
diplomatist = Diplomatist(options.api)

app = QApplication(sys.argv)
diplomatist_ui = Diplomatist_Qt()
diplomatist_ui.transc_changed.connect(diplomatist_ui.change_transc)
diplomatist_ui.transl_changed.connect(diplomatist_ui.change_transl)

if not options.translate:
    diplomatist_ui.text_transl.hide()

diplomatist_ui.show()


def async_transcribe(language="en-US", audio_file=None):
    transc = diplomatist.transcribe(language, audio_file)
    if transc == False:
        transc = "Could Not Be Transcribed!"
    if hasattr(diplomatist, "str_out"):
        diplomatist.str_out.write(transc + "\n")
    diplomatist_ui.transc_changed.emit(transc)


def async_transcribe_translate(transc_lan="en-US", audio_file=None, transl_lan="zh"):
    transc = diplomatist.transcribe(transc_lan, audio_file)
    if transc == False:
        transc = "Could Not Be Transcribed!"
    if hasattr(diplomatist, "str_out"):
        diplomatist.str_out.write(transc + "\n")
    diplomatist_ui.transc_changed.emit(transc)
    transl = diplomatist.translate(transc, transl_lan)
    if hasattr(diplomatist, "str_out"):
        diplomatist.str_out.write(transl + "\n")
    diplomatist_ui.transl_changed.emit(transl)


def keep_running(language="en-US", time_slice=10000, use_mic=False, translate=None):
    init_time = 0
    records_folder = "records"
    if not os.path.isdir(records_folder):
        os.mkdir(records_folder)
    record_file = "record.wav"
    while True:
        start_time = time.time()
        if use_mic:
            record_mic(record_file, time_slice)
        else:
            capture_loopback(record_file, time_slice)
        end_time = time.time()
        time_str = "{} --> {}".format(time.strftime("%H:%M:%S", time.gmtime(
            init_time)), time.strftime("%H:%M:%S", time.gmtime(end_time - start_time + init_time)))
        if hasattr(diplomatist, "out"):
            diplomatist.out.write(time_str + "\n")
        print time_str
        init_time = end_time - start_time + init_time
        saved_file_name = str(time.time()) + ".wav"
        saved_audio_file = os.path.join(records_folder, saved_file_name)
        os.rename(record_file, saved_audio_file)
        if translate:
            thr = threading.Thread(target=async_transcribe_translate, args=(
                [language, saved_audio_file, translate]), kwargs={})
            thr.start()
        else:
            thr = threading.Thread(target=async_transcribe, args=(
                [language, saved_audio_file]), kwargs={})
            thr.start()


def run_one_time(language="en-US", audio_file=None, translate=None):
    if translate:
        async_transcribe_translate(
            language, audio_file, translate)
    else:
        async_transcribe(language, audio_file)


def dip_thread():
    if options.audio_file:
        run_one_time(options.language, options.audio_file, options.translate)
    else:
        keep_running(options.language, options.time_slice, options.use_mic, options.translate)


thread.start_new_thread(dip_thread, ())
sys.exit(app.exec_())
