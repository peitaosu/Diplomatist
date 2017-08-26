# Project Diplomatist

## What is Diplomatist ?

Diplomatist is an auto audio transcribe/translate tool.

## Key Features
* Audio Transcription
* Text Translation
* Loopback Capture (Windows)

## Requirements
* python 2.x
* ```pip install -r requirements.txt```

## Before Use

Compile LoopbackCapture under `/LoopbackCapture` and set the path of `LoopbackCapture.exe` as `Loopback_Capture_Path` in `diplomatist.py`.

`/LoopbackCapture` folder included 3 solutions of win32, one console application written by C++, one console application written by C# (recommended) and another one is a .dll library written by C#.

In Unix/Linux/MACOS, please find replacement tools to capture the loopback.

## Usage
   ```
   > python diplomatist.py -f temp.wav -s 15000 -a 1 -c cert.json -t en_zh

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
    -c CERT_FILE, --cert=CERT_FILE
                            certification file if is API required
    -t TRANSLATE, --tran=TRANSLATE
                            translate to another language
   ```