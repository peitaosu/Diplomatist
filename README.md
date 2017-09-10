# Project Diplomatist

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/peitaosu/Diplomatist/master/LICENSE)

## What is Diplomatist ?

Diplomatist is an auto audio transcribe/translate tool.

## Key Features
* Audio Transcription
* Text Translation
* Loopback Capture (Windows)
* Output as SRT

## Requirements
* python 2.x
* ```pip install -r requirements.txt```

## Before Use

*LoopbackCapture*

Compile LoopbackCapture under `/LoopbackCapture` and set the path of `LoopbackCapture.exe` as `Loopback_Capture_Path` in `diplomatist.py`.

`/LoopbackCapture` folder included 3 solutions of win32, one console application written by C++, one console application written by C# (recommended) and another one is a .dll library written by C#.

In Unix/Linux/MacOS, please find replacement tools to capture the loopback.

*Credentials*

Most of APIs required a credentials to use the API. You can register a account in the website and get the credentials file or keys. Most of them have some free quota each month.

* Google Cloud API: https://cloud.google.com/speech/
* Bing API: https://azure.microsoft.com/en-ca/pricing/details/cognitive-services/speech-api/
* Houndify API: https://www.houndify.com

## Usage
   ```
   > python diplomatist.py -s 15000 -a 1 -c cert.json -l en-US -t zh -o sub.srt

    Usage: diplomatist.py [options]

    Options:
    -h, --help            show this help message and exit
    -m, --mic             record sounds from microphone
    -f AUDIO_FILE, --file=AUDIO_FILE
                            capture sounds and save as wave file temporary
    -s TIME_SLICE, --slice=TIME_SLICE
                            time slice of each wave file
    -a API, --api=API     0 - CMU Sphinx, 1 - Google Cloud, 2 - Bing API, 3 -
                            Houndify API
    -c CREDENTIAL, --cred=CREDENTIAL
                            credential file if is API required
    -l LANGUAGE, --lan=LANGUAGE
                            language which to be transcribed
    -t TRANSLATE, --tran=TRANSLATE
                            translate to another language
    -o OUTPUT, --out=OUTPUT
                            output the result as SRT file
   ```

## UI

Currently, Diplomatist has a very simple UI based on Tkinter, you can use it through `ui.py`, arguments are same as `diplomatist.py`:
```
> python ui.py -s 15000 -a 1 -c cert.json -l en-US -t zh -o sub.srt
```