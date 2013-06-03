#!/usr/bin/env python
# -*- coding: utf-8 -*-

import util
import hwcpplib
import StringIO


class Simulation:

    def __init__(self, time, name="simulation", outfn="", ts="10p"):
        self.time = util.parse_suffix(time)
        self.name = name
        self.outfn = outfn
        self.timestep = util.parse_suffix(ts)
        self.monitors = []

    def print_netlist(self, stream):
        write = ""
        if self.outfn != "":
            write = "write %s" % self.outfn
        stream.write("""
.control
tran {ts} {time}
{write}
.endc
.end
""".format(time=self.time, write=write, ts=self.timestep))

    def run(self, design):
        netlist = StringIO.StringIO()
        design.print_netlist(netlist)
        self.sim = hwcpplib.spicesimulation(self.name, netlist.getvalue())
        netlist.close()

        for m in self.monitors:
            cppmon = m.create()
            self.sim.add_monitor(cppmon)
        self.sim.run_trans(self.timestep, self.time)

    def power(self, device, terminal=None, branch="branch"):
        pm = PowerMonitor(device, terminal, branch)
        self.monitors.append(pm)
        return pm


class PowerMonitor:

    def __init__(self, device, terminal, branch):
        if terminal is None:
            terminal = device.__dict__[device.connection_names[0]]
        self.device = device
        self.terminal = terminal
        self.branch = branch
        self.cppmon = None

    def create(self):
        termnet = self.terminal
        if not isinstance(termnet, str):
            termnet = self.terminal.net.get_name()
        branchname = self.device.get_spice_id() + "#" + self.branch
        self.cppmon = hwcpplib.powermonitor(branchname,
                                            termnet)
        return self.cppmon

    def __getattr__(self, key):
        return getattr(self.cppmon, key)
