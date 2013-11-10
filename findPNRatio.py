#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from hwlib.design import Design
from hwlib.basics import VPwl, Resistor
from hwlib.basic_circuits import Inverter
from hwlib.simulation import Simulation
import numpy as np

if len(sys.argv) < 2:
    print "Usage: %s <library name>" % sys.argv[0]
    sys.exit(-1)

library = sys.argv[1]
d = Design(None, library)


def testRatio(d, ratio):

    i = Inverter(d, "1x", ratio)
    rpu = Resistor(d, 1e9)
    rpd = Resistor(d, 1e9)
    d.pair({rpu.a: i.output,
            rpd.a: i.output,
            rpu.b: d.vdd,
            rpd.b: d.vss})

    vinput = VPwl(d, [
        (0.0, 0.0),
        (2.5e-9, d.nominal_vdd),
        (5.0e-9, 0.0)])
    d.connect(i.input, vinput.plus)
    d.connect(vinput.minus, d.vss)
    d.name({vinput.plus: "vin",
            i.output: "vout"})

    sim = Simulation(d, "5.1n", "ratioSimulation", "ratio.raw")

    times = []

    def falling(cpp):
        times.append(sim.time)
    sim.levelhalt(i.output, d.nominal_vdd / 2, False).callback = falling

    def rising(cpp):
        times.append(sim.time)
    sim.levelhalt(i.output, d.nominal_vdd / 2, True).callback = rising

    sim.run_full()

    vinputs = []
    for t in times:
        if t < 2.5e-9:
            vinput = d.nominal_vdd * (t / 2.5e-9)
        else:
            t -= 2.5e-9
            vinput = d.nominal_vdd - d.nominal_vdd * (t / 2.5e-9)
        vinputs.append(vinput)

    return np.mean(vinputs)

# goal = d.nominal_vdd

# ratio = 2.0
# amt = 1
# t = 0

# while abs(t - goal) > 0.001:
#     t = testRatio(d, ratio)
#     print ratio, t, abs(t - goal), amt
#     if t > goal:
#         ratio -= amt
#     else:
#         ratio += amt
#     amt /= 2

if len(sys.argv) > 2:
    print testRatio(d, float(sys.argv[2]))
else:
    print testRatio(d, 2.0)
