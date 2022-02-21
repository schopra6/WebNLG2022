import os

import wikipediaapi

from benchmark_reader import Benchmark
from benchmark_reader import select_files

base_url = "https://wikipedia.com/wiki/"
base_path = "wk/en/"
base = "wk/"

language = ["fr", "hi", "ru", "pt", "br"]

if not os.path.exists(base):
    os.makedirs(base_path)
    for x in language:
        os.makedirs(base + x + "/")

# where to find the corpus
path_to_corpus = 'corpus/ru/train/'

# initialise Benchmark object
b = Benchmark()

# collect xml files
files = select_files(path_to_corpus)

# load files to Benchmark
b.fill_benchmark(files)

urls = []
for entry in b.entries:
    for x in entry.modifiedtripleset.triples:
        wiki_html = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.HTML
        )
        page = wiki_html.page(x.o)
        if page.exists():
            file = open(base_path + page.title + ".html", "w", encoding="utf-8")
            file.write(page.text)
            file.close()

            for link in page.langlinks:
                lpage = page.langlinks[link]
                if lpage.language in language:
                    file = open(base + lpage.language + "/" + page.title + ".html", "w", encoding="utf-8")
                    file.write(lpage.text)
                    file.close()
