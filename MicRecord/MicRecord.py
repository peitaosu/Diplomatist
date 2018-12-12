import wave
import pyaudio


def record_sounds(output_file="record.wav", time=0):
    _chunk = 1024
    _format = pyaudio.paInt16
    _channels = 2
    _rate = 44100

    audio = pyaudio.PyAudio()
    stream = audio.open(format=_format,
                        channels=_channels,
                        rate=_rate,
                        input=True,
                        frames_per_buffer=_chunk)
    frames = []
    if time is not 0:
        for i in range(0, int(_rate / _chunk * time / 1000)):
            data = stream.read(_chunk)
            frames.append(data)
    else:
        import os, sys, select
        while True:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                try:
                    line = input()
                except:
                    line = raw_input()
                break
            data = stream.read(_chunk)
            frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    out_file = wave.open(output_file, 'wb')
    out_file.setnchannels(_channels)
    out_file.setsampwidth(audio.get_sample_size(_format))
    out_file.setframerate(_rate)
    out_file.writeframes(b''.join(frames))
    out_file.close()
    return 0
