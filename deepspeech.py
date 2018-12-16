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
        output = subprocess.getoutput("deepspeech --model {} --alphabet {} --lm {} --trie {} --audio {}".format(self.model, self.alphabet, self.lm, self.trie, audio_file))
        for index, line in enumerate(output.split("\n")):
            if line.startswith("Inference took "):
                return output.split("\n")[index + 1]
        return None

if __name__=="__main__":
    recognizer = DeepSpeechRecognizer(r"models/output_graph.pbmm", r"models/alphabet.txt", r"models/lm.binary", r"models/trie")
    result = recognizer.recognize("audio/8455-210777-0068.wav")
    print(result)
                
