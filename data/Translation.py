import os
from benchmark_reader import Benchmark
import torch


class Translate:
    def __init__(self, path='../en-french'):  # change path to ../en-french
        self.en2fr  = torch.hub.load('pytorch/fairseq', 'transformer.wmt14.en-fr', tokenizer='moses', bpe='subword_nmt')
        self.en2fr.cuda()

    def translate_text(self, text, src='en', tgt='fr'):
        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        fr = self.en2fr.translate(text, beam=5)
        #result = self.en2fr.translate_paragraph(text, src,   tgt)  # replace with french model(text, source, target)
        return fr

    def create_french_benchmark2xml(self, sourcepath, desinationpath, filename):
        b_en = Benchmark()
        b_fr = Benchmark()
        
        files = sourcepath
        b_en.fill_benchmark(sourcepath)
        b_fr.fill_benchmark(sourcepath)
        for e, entries in enumerate(b_en.entries):
            for l in range(0, len(entries.lexs), 1):
                b_fr.entries[e].lexs[l].lex = self.translate_text(entries.lexs[l].lex)
                b_fr.entries[e].lexs[l].lang = 'fr'
                #print(b_fr.entries[e].lexs[l].lex)

        b_fr.b2xml(desinationpath, filename)
