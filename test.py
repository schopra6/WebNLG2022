import os

import nltk
from bs4 import BeautifulSoup

import wikipediaapi
from benchmark_reader import Benchmark
from benchmark_reader import select_files


def find_in_page(pageName, s_alias, o_alias, language):
    if os.path.exists(pageName):
        sentence = []
        soup = BeautifulSoup(open(pageName, "r", encoding="utf8"), "html.parser")
        p = [nltk.sent_tokenize(x.text.strip()) for x in soup.find_all("p")]  # find better splitting technique
        p = [val for item in p for val in item]
        for x in p:
            for s_a in s_alias:
                if s_a in x:
                    temp = x.replace(s_a, " ( S ) ")
                    for o_a in o_alias:
                        if o_a in temp:
                            temp = temp.replace(o_a, " ( O ) ")
                            sentence.append(x)
                            break
        return set(sentence)
    return []


# where to find the corpus
path_to_corpus = 'corpus/ru/train/'
base = "wk/"
# initialise Benchmark object
b = Benchmark()
for split in ['train', 'dev', 'test']:
    b.fill_benchmark([('xml', f'webnlg_release_v2.1_{split}_wkdt.xml')])

languages = ["fr", "hi", "ru", "pt", "br"]


def extract_info_from_pages(s_lang, o_lang, language):
    s_al = s_lang.alias
    s_al.extend(s_lang.label)
    o_al = o_lang.alias
    o_al.extend(o_lang.label)
    sentence = find_in_page(base + language + "/" + s_name + ".html", s_al, o_al, language)
    for item in find_in_page(base + language + "/" + o_name + ".html", o_al, s_al, language):
        sentence.add(item)
    langaugesSentence[language] = sentence


for entry in b.entries:
    print("Properties: ", entry.relations())
    print("RDF triples: ", entry.list_triples())
    print("Subject:", entry.modifiedtripleset.triples[0].s)
    print("Predicate:", entry.modifiedtripleset.triples[0].p)
    print("Object:", entry.modifiedtripleset.triples[0].o.replace("\"", ""))
    s = entry.modifiedtripleset.triples[0].s
    p = entry.modifiedtripleset.triples[0].p
    o = entry.modifiedtripleset.triples[0].o.replace("\"", "")
    langaugesSentence = dict()
    wiki = wikipediaapi.Wikipedia(language="en")
    s_page = wiki.page(s)
    if s_page.exists():
        s_name = s_page.title
        o_page = wiki.page(o)
        if o_page.exists():
            o_name = o_page.title
        extract_info_from_pages(s_page, o_page, 'en')
        for x in languages:
            if x in s_page.langlinks:
                s_lang = s_page.langlinks[x]
                o_lang = o_page.langlinks[x]
                extract_info_from_pages(s_lang, o_lang, x)
    print(langaugesSentence)
