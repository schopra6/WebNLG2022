import requests
from bs4 import BeautifulSoup

from benchmark_reader import Benchmark
from benchmark_reader import select_files

base_url = "https://wikipedia.com/wiki/"
base_path = "wk/en/"
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
        url = base_url + x.o.replace("\"", "").replace(" ", "_")
        urls.append(url)
        prod = BeautifulSoup(requests.request("GET", url).text, 'html.parser')
        if "Wikipedia does not have an article with this exact name. Please" not in prod.text:
            file = open(base_path + x.o.replace("\"", "").replace(" ", "_").replace("/", "") + ".html", "w")
            file.write(prod.prettify())
            file.close()
        else:
            print(url)
