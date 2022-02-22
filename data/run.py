import os
from os import walk
import sys
import logging
logging.basicConfig(filename='example.log', level=logging.DEBUG)
from Translation import Translate
def main(path,src='/ru/',tgt='/hi/'):
    f = []
    for (dirpath, dirnames, filenames) in walk(path):
        newdirpath=dirpath.replace(src,tgt)
        if not os.path.exists(newdirpath):
            os.mkdir(newdirpath)
        for xmlfile in filenames:
            logging.info("filename:"+xmlfile+"directory:"+newdirpath )
            t = Translate()
            t.create_hindi_benchmark2xml([dirpath+'/'+xmlfile],newdirpath,xmlfile)
if __name__ == "__main__":
    main(sys.argv[1])