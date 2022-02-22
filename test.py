import wikipediaapi
from bs4 import BeautifulSoup

from benchmark_reader import Benchmark
from benchmark_reader import select_files


def find_in_page(pageName,research):
    soup = BeautifulSoup(open(pageName, "r"), "html.parser")
    for x in soup.text.splitlines():
        if research in x:
            print(x)
            if o in x:
                print("double !")


wiki = wikipediaapi.Wikipedia(
    language='en',
)
# where to find the corpus
path_to_corpus = 'corpus/ru/train/'
base = "wk/"
# initialise Benchmark object
b = Benchmark()

# collect xml files
files = select_files(path_to_corpus)

# load files to Benchmark
b.fill_benchmark(files)

languages = ["en", "fr", "hi", "ru", "pt", "br"]

for entry in b.entries:
    print("Properties: ", entry.relations())
    print("RDF triples: ", entry.list_triples())
    print("Subject:", entry.modifiedtripleset.triples[0].s)
    print("Predicate:", entry.modifiedtripleset.triples[0].p)
    print("Object:", entry.modifiedtripleset.triples[0].o)
    s = entry.modifiedtripleset.triples[0].s
    p = entry.modifiedtripleset.triples[0].p
    o = entry.modifiedtripleset.triples[0].o
    page = wiki.page(s)
    if page.exists():
        s_name = page.title
        print(page)
        print(page.title)
        page = wiki.page(o)
        if page.exists():
            o_name = page.title
        for x in languages:
            find_in_page(base + x + "/" + s_name + ".html",s_name)
            break
        # soup = BeautifulSoup(open(base + x + "/" + o_name + ".html", "r"))

    break
