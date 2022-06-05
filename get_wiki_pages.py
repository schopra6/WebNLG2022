import os

import wikipediaapi
from benchmark_reader import Benchmark

base_url = "https://wikipedia.com/wiki/"
base_path = "wk/en/"
base = "wk/"
metrics = {'en': 0}
language = ["fr", "hi", "ru", "pt", "br", "de"]
wiki_html = wikipediaapi.Wikipedia(
    language='en',
    extract_format=wikipediaapi.ExtractFormat.HTML
)
for x in language:
    metrics.update({x: 0})


def get_all_pages(pageName):
    page = wiki_html.page(pageName)
    if page.exists():
        metrics["en"] += 1
        title = page.title.replace("/", "")
        file = open(base_path + title + ".html", "w", encoding="utf-8")
        file.write(page.text)
        file.close()

        for link in page.langlinks:
            lpage = page.langlinks[link]
            if lpage.language in language:
                metrics[lpage.language] += 1
                print(lpage.title)
                title = lpage.title.replace("/", "")
                file = open(base + lpage.language + "/" + title + ".html", "w", encoding="utf-8")
                file.write(lpage.text)
                file.close()


if __name__ == '__main__':

    if not os.path.exists(base):
        os.makedirs(base_path)
        for x in language:
            os.makedirs(base + x + "/")

    # where to find the corpus
    path_to_corpus = 'corpus/en/train/'
    # initialise Benchmark object
    b = Benchmark()
    for split in ['train', 'dev', 'test']:
        b.fill_benchmark([('corpus/xml', f'webnlg_release_v2.1_{split}_wkdt.xml')])

    try:
        urls = []
        for entry in b.entries:
            for x in entry.modifiedtripleset.triples:
                get_all_pages(x.o)
                get_all_pages(x.s)
    except BaseException as e:
        print(e)
        print(metrics)

    print(metrics)
