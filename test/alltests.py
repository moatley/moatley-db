#!/usr/bin/python

from unittest import main

from seecrdeps import includeParentAndDeps         #DO_NOT_DISTRIBUTE 
includeParentAndDeps(__file__, scanForDeps=True)   #DO_NOT_DISTRIBUTE

from ast import parse, ClassDef
from imp import load_module, get_suffixes
from os import walk
from os.path import abspath, dirname, splitext, join

def loadTestFromPath(testRoot):
    pySuffix = [(suffix, mode, suffixType) for (suffix, mode, suffixType) in get_suffixes() if suffix == ".py"][0]
    for path, dirs, files in walk(testRoot):
        for filename in [join(path, filename) for filename in files if splitext(filename)[-1] == '.py']:
            tree = parse(open(filename).read())

            for each in tree.body:
                if type(each) is ClassDef and each.bases[0].id == 'SeecrTestCase':
                    fullFilename = join(path, filename)
                    with open(fullFilename) as fp:
                        mod = load_module(each.name, fp, fullFilename, pySuffix)
                        globals()[each.name] = getattr(mod, each.name)


if __name__ == '__main__':
    loadTestFromPath(dirname(abspath(__file__)))
    main()
