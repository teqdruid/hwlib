#!/usr/bin/env python
# -*- coding: utf-8 -*-

import util
import hwcpplib
import StringIO

from component import Component
from hwlib.basics import VPwl, Resistor


class Simulation:

    def __init__(self, design, time, name="simulation", outfn="", ts="10p"):
        self.time = util.parse_suffix(time)
        self.design = design
        self.name = name
        self.outfn = outfn
        self.timestep = util.parse_suffix(ts)
        self.monitors = []
        self.halts = []

        self.add_dummy(design)
        self.design.set_simulation(self)

    def add_dummy(self, d):
        pwldummy = VPwl(d, [(0, 0),
                       ("100p", 1.0)])
        r1 = Resistor(d, 100000000)
        d.pair({r1.a: pwldummy.plus,
                r1.b: d.vss,
                pwldummy.minus: d.vss})
        self.levelhalt(pwldummy.plus, 1.0, True)

    def print_netlist(self, stream):
        write = ""
        if self.outfn != "" and self.outfn is not None:
            write = "write %s" % self.outfn
        stream.write("""
.control
tran {ts} {time}
{write}
.endc
.end
""".format(time=self.time, write=write, ts=self.timestep))

    def run(self):
        netlist = StringIO.StringIO()
        self.design.print_netlist(netlist)
        self.sim = hwcpplib.spicesimulation(self.name, netlist.getvalue())
        netlist.close()

        for m in self.monitors:
            cppmon = m.create(self)
            self.sim.add_monitor(cppmon)
        for hc in self.halts:
            hc.create(self)
        if self.outfn != "" and self.outfn is not None:
            self.sim.set_output_file(self.outfn)
        self.sim.run_trans(self.timestep, self.time)

    def resume(self):
        self.sim.resume()

    def run_full(self):
        self.run()
        while self.status == self.status.halted:
            self.resume()

    def power(self, device, terminal=None, branch="branch"):
        pm = PowerMonitor(device, terminal, branch)
        self.monitors.append(pm)
        return pm

    def levelhalt(self, net, level, rising):
        lh = LevelHalt(net, level, rising)
        self.halts.append(lh)
        return lh

    def __getattr__(self, key):
        return getattr(self.sim, key)


class PowerMonitor:

    def __init__(self, device, terminal, branch):
        if terminal is None:
            terminal = device.__dict__[device.connection_names[0]]
        self.device = device
        self.terminal = terminal
        self.branch = branch
        self.cppmon = None

    def create(self, sim):
        termnet = self.terminal
        if not isinstance(termnet, str):
            termnet = self.terminal.net.get_name()
        branchname = self.device.get_spice_id() + "#" + self.branch
        self.cppmon = hwcpplib.powermonitor(branchname,
                                            termnet)
        return self.cppmon

    def __getattr__(self, key):
        return getattr(self.cppmon, key)


class LevelHalt:

    def __init__(self, net, level, rising):
        self.net = net
        self.level = level
        self.rising = rising

    def create(self, sim):
        net = self.net
        if not isinstance(net, str):
            if isinstance(net, Component.Terminal):
                net = net.net
            net = net.get_name()
        self.cppmon = hwcpplib.levelhalt(sim.sim, net, self.level, self.rising)
        return self.cppmon

    def highgoing(self):
        self.level = 0.99
        self.rising = True
        self.cppmon.level = self.level
        self.cppmon.rising = self.rising

    def lowgoing(self):
        self.level = 0.01
        self.rising = False
        self.cppmon.level = self.level
        self.cppmon.rising = self.rising
