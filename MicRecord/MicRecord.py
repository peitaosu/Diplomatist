import wave, pyaudio

def record_sounds(output_file="record.wav", time=0):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    if time is not 0:
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
        frames = []
        for i in range(0, int(RATE / CHUNK * time / 1000)):
            data = stream.read(CHUNK)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        audio.terminate()

        out_file = wave.open(output_file, 'wb')
        out_file.setnchannels(CHANNELS)
        out_file.setsampwidth(audio.get_sample_size(FORMAT))
        out_file.setframerate(RATE)
        out_file.writeframes(b''.join(frames))
        out_file.close()
        exit_code = 0
    else:
        exit_code = 0 
    return exit_code