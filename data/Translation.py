from benchmark_reader import Benchmark
from benchmark_reader import select_files
import six
from google.cloud import translate_v2 as translate
class Translate:
    def __init__(self):
        self.translate_client = translate.Client()

    def translate_text(target, text):
        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")

         # Text can also be a sequence of strings, in which case this method
         # will return a sequence of results for each text.
        result = self.translate_client.translate(text, target_language=target)
        return format(result["translatedText"])
def createHindiBenchmark2xml(sourcepath,destinationpath,filename):
        b_en = Benchmark()
        b_hi = Benchmark()
        t=Translate()
        files = select_files(sourcepath)
        b_en.fill_benchmark(files)
        b_hi.fill_benchmark(files)
        for e,entries in enumerate(b.entries):
            for l,lexs in enumerate(nentries.lexs):
                b_hi.entries[e].lexs[l].lex= t.translate_text('hi',b.entries[e].lexs[l].lex)
                print(b_hi.entries[e].lexs[l].lex)
                break
        b_hi.b2xml(destinationpath,filename)


