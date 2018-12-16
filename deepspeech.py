import subprocess

class DeepSpeechRecognizer():
    def __init__(self, model=None, alphabet=None, lm=None, trie=None):
        self.model = model
        self.alphabet = alphabet
        self.lm = lm
        self.trie = trie

    def recognize(self, audio_file):
        """recognize audio file

        args:
            audio_file (str)

        return:
            result (str/False)
        """
        output = subprocess.check_output("deepspeech --model {} --alphabet {} --lm {} --trie {} --audio {}".format(self.model, self.alphabet, self.lm, self.trie, audio_file), shell=True, stderr=subprocess.STDOUT)
        for line in output.split("\n"):
            if line[0].islower():
                return line
        return None

if __name__=="__main__":
    recognizer = DeepSpeechRecognizer(r"models/output_graph.pbmm", r"models/alphabet.txt", r"models/lm.binary", r"models/trie")
    result = recognizer.recognize("audio/8455-210777-0068.wav")
    print(result)
                

