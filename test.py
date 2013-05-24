#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from hwlib import *
from hwlib.basics import *

d = Design()

n1 = NMos(d)

d.print_netlist(sys.stdout)
