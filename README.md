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