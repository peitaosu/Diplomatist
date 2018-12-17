# Project Diplomatist

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/peitaosu/Diplomatist/master/LICENSE)

## What is Diplomatist ?

Diplomatist is an auto audio transcribe(audio2text) and translate(lang2lang) tool.

## APIs
* 0 - CMU Sphinx
* 1 - Google Cloud
* 2 - Bing API
* 3 - Houndify API
* 4 - Baidu DeepSpeech (macOS/Linux Only)

## Key Features
* Audio Transcription
* Text Translation
* Loopback Capture and Microphone Record
* Output as SRT

## Support Format (Transcribe from File)

Actually, Diplomatist only support to transcribe from `.wav` file and `.aif` file. For other formats, it will try to convert from other format to WAVE which was supported by **pydub**, and the **FFmpeg** is required in your environment.

You can get **FFmpeg** from here: https://www.ffmpeg.org

## Requirements
* python 2.x/3.x
* ```pip install -r requirements.txt```
* ```pip install -r requirements[.osx|.linux].txt``` (for macOS/Linux)

## Before Use

***config.json***

Most of required configurations will be loaded from `config.json`, there are some default values already, if you want to change these configs please update `config.json`.
* API: name, cred, model, alphabet, etc.
* LOOPBACK_CAPTURE: location of LoopbackCapture
* SRT: save output string to srt file
* RECORD: location to save temp record files
* PROXY: http/https proxy servers

***LoopbackCapture***

In Windows, compile LoopbackCapture under `/LoopbackCapture` and set the path of `LoopbackCapture.exe` as `Loopback_Capture_Path` in `diplomatist.py`.

`/LoopbackCapture` folder included 3 solutions of win32, one console application written by C++, one console application written by C# (recommended) and another one is a .dll library written by C#.

In macOS, the `mac/LoopbackCapture.py` support to capture sounds from output device but not support to capture Loopback from device directly. The workaround is to route what is playing on the computer digitally back to the input without using a cable. Suggest to use Soundflower.

In Linux, the `linux/LoopbackCapture.py` support to capture sounds from system but it require a tool `avconv` which is a part from "libav-tools" package to support to record audio use command line with specific format specific duration and from specific device.

Detail: [LoopbackCapture README.md](https://github.com/peitaosu/LoopbackCapture/blob/master/README.md)

***Credentials***

Most of APIs required a credential to use the API. You can register a account in the website and get the credential file or key. Most of them have some free quota each month.

* Google Cloud API: https://cloud.google.com/speech/
* Bing API: https://azure.microsoft.com/en-ca/pricing/details/cognitive-services/speech-api/
* Houndify API: https://www.houndify.com

## Usage
   ```
   > python diplomatist.py -s 15000 -a 1 -l en-US -t zh -o sub.srt

   Usage: diplomatist.py [options]
   
   Options:
   -h, --help            show this help message and exit
   -m, --mic             record sounds from microphone
   -f AUDIO_FILE, --file=AUDIO_FILE
                           audio file which to be transcribed and translated
   -s TIME_SLICE, --slice=TIME_SLICE
                           time slice of each wave file
   -a API, --api=API     0 - CMU Sphinx, 1 - Google Cloud, 2 - Bing API, 3 -
                           Houndify API, 4 - Baidu DeepSpeech
   -l LANGUAGE, --lan=LANGUAGE
                           language which to be transcribed
   -t TRANSLATE, --tran=TRANSLATE
                           translate to another language
   --qt                  runs UI with QT
   --tk                  runs UI with Tk
   ```

## UI

Currently, Diplomatist has a very simple UI based on Tkinter or PyQt4. You can use it through `ui.py` with arguments `--tk` or `--qt`, other arguments are same as `diplomatist.py`:
```
> python ui.py -s 15000 -a 1 -l en-US -t zh -o sub.srt --tk

# or 

> python ui.py -s 15000 -a 1 -l en-US -t zh -o sub.srt --qt
```

Before you use `ui.py` with `--tk`, please install python-tk package:

In Linux:
1. `> sudo apt-get install python-tk`

Before you use `ui.py` with `--qt`, please make sure you have installed PyQt4/PyQt5 in your environment:

In Windows:
1. Get PyQt4/5-***.whl from http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4
2. `> pip install PyQt4/5-***.whl`

In macOS:
1. `> brew install PyQt`

In Linux:
1. `> sudo apt-get install python-qt4`