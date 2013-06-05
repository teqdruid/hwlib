#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from hwlib import *
from hwlib.basics import *
from hwlib.basic_circuits import *

d = Design()

pwl = Voltage(d, 1)

i1 = Inverter(d)
c1 = Capacitor(d, 2e-15)

d.pair({i1.input: pwl.plus,
        pwl.minus: d.vss,
        c1.pos: i1.output,
        c1.neg: d.vss
        })

d.print_netlist(sys.stdout)

inp = True


def toggle(cpp):
    global inp
    if inp:
        inp = False
        pwl.alter("0v")
        outlevel.highgoing()
    else:
        inp = True
        pwl.alter("1v")
        outlevel.lowgoing()

s = Simulation(d, "10n", "test simulation", "test.raw")
s.add_start_callback(toggle)
pmon = s.power(d.vpwr)
outlevel = s.levelhalt(i1.output, 0.05, False)
outlevel.callback = toggle

s.run_full()


print "Simulation end with ", s.sim.status

print "VPwr:"
print "  Avg: %e" % pmon.avg()
