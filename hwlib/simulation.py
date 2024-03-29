#!/usr/bin/env python
# -*- coding: utf-8 -*-

import util
import hwcpplib
import StringIO

from component import Component
from hwlib.basics import VPulse, Resistor


class Simulation:

    def __init__(self, design, time, name="simulation", outfn="", ts="1p"):
        self.time = util.parse_suffix(time)
        self.design = design
        self.name = name
        self.outfn = outfn
        self.timestep = util.parse_suffix(ts)
        self.monitors = []
        self.halts = []
        self.start_callbacks = []
        self.periodic_callbacks = []
        self.init_conds = []
        self.quiet = False
        self.debug = False

        self.add_dummy(design)
        self.design.set_simulation(self)

    def add_dummy(self, d):
        pulse = VPulse(d, None, 0.5e-9)
        r1 = Resistor(d, 100000000)
        d.pair({r1.a: pulse.plus,
                r1.b: d.vss,
                pulse.minus: d.vss})
        d.name({pulse.plus: "clk"})
        dummy_lh = self.levelhalt(pulse.plus, pulse.v2, True)
        dummy_lh.callback = self.callback
        self.callback_count = 0

    def callback(self, cpp):
        self.callback_count += 1
        if self.callback_count == 1:
            for cb in self.start_callbacks:
                cb(cpp)
        for cb in self.periodic_callbacks:
            cb(cpp)

    def add_start_callback(self, cb):
        self.start_callbacks.append(cb)

    def add_periodic_callback(self, cb):
        self.periodic_callbacks.append(cb)

    def set_ic(self, node, v):
        self.init_conds.append((node, v))

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
        for (node, v) in self.init_conds + self.design.init_conds:
            netlist.write(".IC V(%s) = %s\n" % (resolve_net(node), v))
        self.sim = hwcpplib.spicesimulation(self.name, netlist.getvalue())
        self.sim.quiet = self.quiet
        self.sim.debug = self.debug
        netlist.close()

        for m in self.monitors:
            cppmon = m.create(self)
            self.sim.add_monitor(cppmon)

        self.haltmap = dict()
        for hc in self.halts:
            cppmon = hc.create(self)
            cppid = cppmon.getid()
            assert cppid not in self.haltmap
            self.haltmap[cppid] = hc
        if self.outfn != "" and self.outfn is not None:
            self.sim.set_output_file(self.outfn)

        self.sim.run_trans(self.timestep, self.time)
        self.halt_callbacks()

    def resume(self):
        self.sim.resume()
        self.halt_callbacks()

    def halt_callbacks(self):
        halts = self.sim.halts_requested
        self.time = self.sim.time
        for cppmon in halts:
            id = cppmon.getid()
            hc = self.haltmap[id]
            if hasattr(hc, "callback"):
                hc.callback(cppmon)

    def run_full(self):
        self.run()
        while self.status == self.status.halted:
            self.resume()

    def power(self, device, terminal=None, branch="branch"):
        pm = PowerMonitor(device, terminal, branch)
        self.monitors.append(pm)
        return pm

    def levelhalt(self, net, level, rising, base_net=None):
        if base_net is None:
            base_net = self.design.vss
        lh = LevelHalt(net, base_net, level, rising)
        self.halts.append(lh)
        return lh

    def __getattr__(self, key):
        return getattr(self.sim, key)


def resolve_net(net):
    if not isinstance(net, str):
        if isinstance(net, Component.Terminal):
            net = net.net
        net = net.get_name()
    return net


class PowerMonitor:

    def __init__(self, device, terminal, branch):
        if terminal is None:
            terminal = device.__dict__[device.connection_names[0]]
        self.device = device
        self.terminal = terminal
        self.branch = branch
        self.cppmon = None

    def create(self, sim):
        termnet = resolve_net(self.terminal)
        branchname = self.device.get_spice_id() + "#" + self.branch
        self.cppmon = hwcpplib.powermonitor(branchname,
                                            termnet)
        return self.cppmon

    def __getattr__(self, key):
        return getattr(self.cppmon, key)


class LevelHalt:

    def __init__(self, net, base_net, level, rising):
        self.net = net
        self.base_net = base_net
        self.level = level
        self.rising = rising

    def create(self, sim):
        net = resolve_net(self.net)
        base_net = resolve_net(self.base_net)
        self.cppmon = hwcpplib.levelhalt(net, base_net,
                                         self.level, self.rising)
        self.cppmon.setup(sim.sim)
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
