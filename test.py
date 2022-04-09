import os

import nltk
from bs4 import BeautifulSoup

import get_wiki_pages
import wikipediaapi
from benchmark_reader import Benchmark
from units_reader import UnitReader

metrics = {"en": 0}
# where to find the corpus
path_to_corpus = 'corpus/ru/train/'
path_to_units = "corpus/units/"
base = "wk/"
id = "KELM"


def find_in_page(pageName, s_alias, o_alias, language, engName, retry=True):
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
                            metrics[language] += 1
                            sentence.append(x)
                            break
        return set(sentence)
    else:
        print(pageName)
        if retry:
            get_wiki_pages.get_all_pages(engName)
            return find_in_page(pageName, s_alias, o_alias, language, engName, retry=False)
    return []


def process_length(text, lang):
    txt = int(float(text))
    return sum([[x.replace("{text}", y) for y in [str(txt), text]] for x in units.get_unit("meters", lang)], [])


def extract_info_from_page(page, alias, language, engName):
    s_name = page.title
    s_al = page.alias
    s_al.extend(page.label)
    s_al.append(s_name)
    sentence = find_in_page(base + language + "/" + s_name + ".html", s_al, alias, language, engName)
    langaugesSentence[language] = sentence


def extract_info_from_pages(s_lang, o_lang, language, eng_name_subj, eng_name_obj):
    o_name = o_lang.title
    s_name = s_lang.title
    s_al = s_lang.alias
    s_al.extend(s_lang.label)
    o_al = o_lang.alias
    o_al.extend(o_lang.label)
    sentence = find_in_page(base + language + "/" + s_name + ".html", s_al, o_al, language, eng_name_subj)
    for item in find_in_page(base + language + "/" + o_name + ".html", o_al, s_al, language, eng_name_obj):
        sentence.add(item)
    langaugesSentence[language] = sentence


if __name__ == '__main__':

    # initialise Units object
    units = UnitReader()
    units.read(path_to_units)

    # initialise Benchmark object
    b = Benchmark()
    for split in ['train', 'dev', 'test']:
        b.fill_benchmark([('corpus/xml', f'webnlg_release_v2.1_{split}_wkdt.xml')])

    languages = ["fr", "hi", "ru", "pt", "br", 'de']
    for x in languages:
        metrics.update({x: 0})

    wiki = wikipediaapi.Wikipedia(language="en")
    try:
        for entry in b.entries:
            # print("Properties: ", entry.relations())
            print("RDF triples: ", entry.list_triples())
            # print("Subject:", entry.modifiedtripleset.triples[0].s)
            # print("Predicate:", entry.modifiedtripleset.triples[0].p)
            # print("Object:", entry.modifiedtripleset.triples[0].o.replace("\"", ""))
            s = entry.modifiedtripleset.triples[0].s
            p = entry.modifiedtripleset.triples[0].p
            o = entry.modifiedtripleset.triples[0].o.replace("\"", "")
            langaugesSentence = dict()
            s_page = wiki.page(s)
            if not s_page.exists():
                print(s_page)
            if any(map(p.lower().__contains__, ['elevation above sea level', 'length'])):
                extract_info_from_page(s_page, process_length(o, "en"), "en", s)
                for x in languages:
                    if x in s_page.langlinks:
                        s_lang = s_page.langlinks[x]
                        extract_info_from_page(s_lang, process_length(o, x), x, s)
            else:
                o_page = wiki.page(o)
                if not o_page.exists():
                    for x in languages:
                        if x in s_page.langlinks:
                            s_lang = s_page.langlinks[x]
                            extract_info_from_page(s_lang, [o], x, s)
                else:
                    extract_info_from_pages(s_page, o_page, 'en', s, o)
                    for x in languages:
                        if x in s_page.langlinks:
                            s_lang = s_page.langlinks[x]
                            if x in o_page.langlinks:
                                o_lang = o_page.langlinks[x]
                                extract_info_from_pages(s_lang, o_lang, x, s, o)
                            else:
                                extract_info_from_page(s_lang, o_page.alias, x, s)
            print(langaugesSentence)
            c = 0
            for la in langaugesSentence:
                sent = langaugesSentence[la]
                for x in sent:
                    c += 1
                    entry.add_lex(x, id + str(c), la)
    except BaseException as e:
        print("Saving work done ! ")
        print(metrics)
        b.b2xml(".", filename="test.xml")
        raise e
