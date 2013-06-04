#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import sys
from hwlib import *
from hwlib.basics import *
from hwlib.basic_circuits import *

d = Design()

pwl = VPwl(d, [(0, 0),
               ("5n", 1.0),
               ("10n", 0)])
i1 = Inverter(d)
# r1 = Resistor(d, 10000)
c1 = Capacitor(d, 2e-15)

d.pair({i1.input: pwl.plus,
        pwl.minus: d.vss,
        # i1.output: r1.a,
        # r1.b: d.vss,
        c1.pos: i1.output,
        c1.neg: d.vss
        })

# print n1.gate.__dict__

# d.print_netlist(sys.stdout)

s = Simulation(d, "10n", "test simulation", "test.raw")
# s.print_netlist(sys.stdout)
pmon = s.power(d.vpwr)
outlevel = s.levelhalt(i1.output, 0.05, False)
s.run()

while s.sim.status == s.sim.status.halted:
    print "Halt!"
    s.resume()

print "Simulation end with ", s.sim.status

print "VPwr:"
print "  Avg: %e" % pmon.avg()
