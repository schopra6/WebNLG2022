import os
from benchmark_reader import Benchmark
os.chdir('indicTrans') #swap for french dir
from indicTrans.inference.engine import Model #to be swapped with fr nmt

class Translate:
    def __init__(self, path='../en-indic'): #change path to ../en-french
        self.indic2en_model = Model(expdir = path)

    def translate_text(self,text, src='en', tgt='fr'):
        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        result = self.indic2en_model.translate_paragraph(text, src, tgt) #replace with french model(text, source, target)
        return result


    def create_french_benchmark2xml(self,sourcepath, desinationpath, filename):
        b_en = Benchmark()
        b_fr = Benchmark()

        files = sourcepath
        b_en.fill_benchmark(sourcepath)
        b_fr.fill_benchmark(sourcepath)
        for e, entries in enumerate(b_en.entries):
            for l in range(0, len(entries.lexs), 2):
                b_fr.entries[e].lexs[l + 1].lex = translate_text(entries.lexs[l].lex)
                b_fr.entries[e].lexs[l + 1].lang = 'fr'
                # print(b_fr.entries[e].lexs[l].lex)

        b_fr.b2xml(desinationpath, filename)