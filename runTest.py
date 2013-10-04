#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hwlib.testbench import Testbench
import os
import sys


def importFile(fn):
    mod = fn[2:-3].replace("/", ".")
    __import__(mod)

for root, dirs, files in os.walk('./hwlib/'):
    for file in files:
        if file.endswith(".py"):
            importFile(os.path.join(root, file))


showNetlist = False

if len(sys.argv) > 1:
    tests = []
    for testname in sys.argv[1:]:
        if testname[0] == "-":
            optname = testname[1:].lower()
            if optname == "shownetlist":
                showNetlist = True
        elif testname not in Testbench.RegisteredTests:
            print "Error: could not find test named \"%s\"" % testname
        else:
            tests.append(Testbench.RegisteredTests[testname])
    for Test in tests:
        print "%s running..." % str(Test)
        t = Test()
        if showNetlist:
            t.printNetlist(sys.stdout)
        t.run()
else:
    print "Available tests:"
    for testname in Testbench.RegisteredTests.keys():
        print "\t%s" % testname
