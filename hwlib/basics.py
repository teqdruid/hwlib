#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hwlib.component import Component


class Voltage(Component):

    netlist_format = "V{id} {connections} {voltage}V"
    connection_names = ['plus', 'minus']

    def __init__(self, design, voltage):
        Component.__init__(self, design)
        self.voltage = voltage


class VPwl(Component):

    netlist_format = "V{id} {connections} pwl({v_pairs})"
    connection_names = ['plus', 'minus']

    def __init__(self, design, vpairs):
        Component.__init__(self, design)
        self.v_pairs = " ".join(map(lambda p: "%s %s" % p, vpairs))


class VPulse(Component):

    netlist_format = \
        "V{id} {connections} pulse({v1} {v2} {td} {tr} {tf} {pw} {period})"
    connection_names = ['plus', 'minus']

    def __init__(self, design, v2, period, duty_cycle=0.5,
                 td=0, tr=0, tf=0, v1=0):
        Component.__init__(self, design)
        self.v2 = v2
        self.period = period
        self.pw = period * duty_cycle
        self.td = td
        self.tr = tr
        self.tf = tf
        self.v1 = v1


class NMos(Component):

    netlist_format = "Mn{id} {connections} nmos l={length:len} w={width:len}"
    connection_names = ['drain', 'gate', 'source', 'body']

    def __init__(self, design, width='1x', length='1x'):
        Component.__init__(self, design)
        self.length = design.length(length)
        self.width = design.length(width)
        design.connect(self.body, design.vss)


class PMos(Component):

    netlist_format = "Mp{id} {connections} pmos l={length:len} w={width:len}"
    connection_names = ['drain', 'gate', 'source', 'body']

    def __init__(self, design, width='2x', length='1x'):
        Component.__init__(self, design)
        self.length = design.length(length)
        self.width = design.length(width)
        design.connect(self.body, design.vdd)


class Resistor(Component):

    netlist_format = "R{id} {connections} {resistance}"
    connection_names = ['a', 'b']

    def __init__(self, design, resistance):
        Component.__init__(self, design)
        self.resistance = resistance


class Capacitor(Component):

    netlist_format = "C{id} {connections} {capacitance}"
    connection_names = ['pos', 'neg']

    def __init__(self, design, capacitance):
        Component.__init__(self, design)
        self.capacitance = capacitance
