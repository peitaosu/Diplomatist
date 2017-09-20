import sys, thread, platform
if platform.system() == "Darwin":
    import site
    site.addsitedir("/usr/local/lib/python2.7/site-packages")
try:
    from PyQt4 import QtCore, QtGui, uic
    from PyQt4.QtCore import QMainWindow, QApplication
except:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic
    from PyQt5.QtWidgets import QMainWindow, QApplication
from diplomatist import *

qt_ui_file = "diplomatist.ui"

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
else:
    cred = None

if opt.output:
    os.environ["OUT_SRT"] = opt.output

diplomatist = Diplomatist()

app = QApplication(sys.argv)
diplomatist_ui = Diplomatist_Qt()
diplomatist_ui.transc_changed.connect(diplomatist_ui.change_transc)
diplomatist_ui.transl_changed.connect(diplomatist_ui.change_transl)
diplomatist_ui.show()

def async_transcribe(api=0, audio_file=None, cred=None, language="en-US"):
    transc = diplomatist.transcribe(api, audio_file, cred, language)
    if transc == False:
        transc = "Could Not Be Transcribed!"
    if hasattr(diplomatist, "out"):
        diplomatist.out.write(transc + "\n")
    diplomatist_ui.transc_changed.emit(transc)

def async_transcribe_translate(api=0, audio_file=None, cred=None, transc_lan="en-US", transl_lan="zh"):
    transc = diplomatist.transcribe(api, audio_file, cred, transc_lan)
    if transc == False:
        transc = "Could Not Be Transcribed!"
    if hasattr(diplomatist, "out"):
        diplomatist.out.write(transc + "\n")
    diplomatist_ui.transc_changed.emit(transc)
    transl = diplomatist.translate(transc, transl_lan)
    if hasattr(diplomatist, "out"):
        diplomatist.out.write(transl + "\n")
    diplomatist_ui.transl_changed.emit(transl)

def keep_running():
    init_time = 0
    records_folder = "records"
    if not os.path.isdir(records_folder):
        os.mkdir(records_folder)
    record_file = "record.wav"
    while True:
        start_time = time.time()
        if opt.use_mic:
            diplomatist.record(record_file)
        else:
            diplomatist.capture_loopback(record_file, opt.time_slice)
        end_time = time.time()
        time_str = "{} --> {}".format(time.strftime("%H:%M:%S", time.gmtime(init_time)), time.strftime("%H:%M:%S", time.gmtime(end_time - start_time + init_time)))
        if hasattr(diplomatist, "out"):
            diplomatist.out.write(time_str + "\n")
        print time_str
        init_time = end_time - start_time + init_time
        saved_file_name = str(time.time()) + ".wav"
        saved_audio_file = os.path.join(records_folder, saved_file_name)
        os.rename(record_file, saved_audio_file)
        if opt.translate:
            thr = threading.Thread(target=async_transcribe_translate, args=([opt.api, saved_audio_file, cred, opt.language, opt.translate]), kwargs={})
            thr.start()
        else:
            thr = threading.Thread(target=async_transcribe, args=([opt.api, saved_audio_file, cred, opt.language]), kwargs={})
            thr.start()

def run_one_time():
    if opt.translate:
        async_transcribe_translate(opt.api, opt.audio_file, cred, opt.language, opt.translate)
    else:
        async_transcribe(opt.api, opt.audio_file, cred, opt.language)

def dip_thread():
    if opt.audio_file:
        run_one_time()
    else:
        keep_running()

thread.start_new_thread(dip_thread,())
sys.exit(app.exec_())