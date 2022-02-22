import os
from benchmark_reader import Benchmark
os.chdir('indicTrans')
from indicTrans.inference.engine import Model

class Translate:
    def __init__(self, path='../en-indic'):
        self.indic2en_model = Model(expdir = path)

    def translate_text(self,text, src='en', tgt='hi'):
        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        result = self.indic2en_model.translate_paragraph(text, src, tgt)
        return result


    def create_hindi_benchmark2xml(self,sourcepath, desinationpath, filename):
        b_en = Benchmark()
        b_hi = Benchmark()

        files = sourcepath
        b_en.fill_benchmark(sourcepath)
        b_hi.fill_benchmark(sourcepath)
        for e, entries in enumerate(b_en.entries):
            for l in range(0, len(entries.lexs), 2):
                b_hi.entries[e].lexs[l + 1].lex = translate_text(entries.lexs[l].lex)
                b_hi.entries[e].lexs[l + 1].lang = 'hi'
                # print(b_hi.entries[e].lexs[l].lex)

        b_hi.b2xml(desinationpath, filename)
