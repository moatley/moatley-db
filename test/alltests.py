#!/usr/bin/python

from unittest import main

from seecrdeps import includeParentAndDeps         #DO_NOT_DISTRIBUTE 
includeParentAndDeps(__file__, scanForDeps=True)   #DO_NOT_DISTRIBUTE

from mysqltest import MysqlTest

if __name__ == '__main__':
    main()

