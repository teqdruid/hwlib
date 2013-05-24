#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from hwlib import *
from hwlib.basics import *

d = Design()

n1 = NMos(d)
d.connect(n1.gate, d.vss)
d.connect(n1.drain, d.vss)
d.connect(n1.source, d.vss)

# print n1.gate.__dict__

d.print_netlist(sys.stdout)
