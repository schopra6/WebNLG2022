from benchmark_reader import Benchmark
from benchmark_reader import select_files

# where to find the corpus
path_to_corpus = 'corpus/ru/train/'

# initialise Benchmark object
b = Benchmark()

# collect xml files
files = select_files(path_to_corpus)

# load files to Benchmark
b.fill_benchmark(files)

for entry in b.entries:
    if entry.dbpedialinks:
        for x in entry.dbpedialinks:
            print(x.flat_triple())