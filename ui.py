from diplomatist import *
import tkinter, thread


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

diplomatist_ui = tkinter.Tk()
transc_str = tkinter.StringVar()
transc_label = tkinter.Label(diplomatist_ui, textvariable=transc_str).pack(side=tkinter.TOP)
transl_str = tkinter.StringVar()
transl_label = tkinter.Label(diplomatist_ui, textvariable=transl_str).pack(side=tkinter.BOTTOM)

def async_transcribe(api=0, audio_file=None, cred=None, language="en-US"):
    transc = diplomatist.transcribe(api, audio_file, cred, language)
    if transc == False:
        transc = "Could Not Be Transcribed!"
    if hasattr(diplomatist, "out"):
        diplomatist.out.write(transc + "\n")
    transc_str.set(transc)

def async_transcribe_translate(api=0, audio_file=None, cred=None, transc_lan="en-US", transl_lan="zh"):
    transc = diplomatist.transcribe(api, audio_file, cred, transc_lan)
    if transc == False:
        transc = "Could Not Be Transcribed!"
    if hasattr(diplomatist, "out"):
        diplomatist.out.write(transc + "\n")
    transc_str.set(transc)
    transl = diplomatist.translate(transc, transl_lan)
    if hasattr(diplomatist, "out"):
        diplomatist.out.write(transl + "\n")
    transl_str.set(transl)

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
diplomatist_ui.mainloop()