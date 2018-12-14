from diplomatist import *
import thread
import platform
try:
    import tkinter
except:
    import Tkinter as tkinter

os.environ["LOOPBACK_CAPTURE"] = r"LoopbackCapture\win32\csharp\LoopbackCapture\LoopbackCapture\bin\Debug\LoopbackCapture.exe"

options = get_options()
diplomatist = Diplomatist(options.api)

diplomatist_ui = tkinter.Tk()
diplomatist_ui.title("Diplomatist")
diplomatist_ui.attributes("-alpha", 0.8)
transc_str = tkinter.StringVar()
transc_label = tkinter.Label(
    diplomatist_ui, textvariable=transc_str).pack(side=tkinter.TOP)
transl_str = tkinter.StringVar()
transl_label = tkinter.Label(
    diplomatist_ui, textvariable=transl_str).pack(side=tkinter.BOTTOM)


def async_transcribe(language="en-US", audio_file=None):
    transc = diplomatist.transcribe(language, audio_file)
    if transc == False:
        transc = "Could Not Be Transcribed!"
    if hasattr(diplomatist, "str_out"):
        diplomatist.str_out.write(transc + "\n")
    transc_str.set(transc)


def async_transcribe_translate(transc_lan="en-US", audio_file=None, transl_lan="zh"):
    transc = diplomatist.transcribe(transc_lan, audio_file)
    if transc == False:
        transc = "Could Not Be Transcribed!"
    if hasattr(diplomatist, "str_out"):
        diplomatist.str_out.write(transc + "\n")
    transc_str.set(transc)
    transl = diplomatist.translate(transc, transl_lan)
    if hasattr(diplomatist, "str_out"):
        diplomatist.str_out.write(transl + "\n")
    transl_str.set(transl)


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
diplomatist_ui.mainloop()
