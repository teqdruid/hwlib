#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hwlib.component import Component


class Voltage(Component):

    netlist_format = "V{id} {connections} {voltage}V"
    connection_names = ['minus', 'plus']

    def __init__(self, design, voltage):
        Component.__init__(self, design)
        self.voltage = voltage


class VPwl(Component):

    netlist_format = "V{id} {connections} pwl({v_pairs})"
    connection_names = ['minus', 'plus']

    def __init__(self, design, vpairs):
        Component.__init__(self, design)
        self.v_pairs = " ".join(map(lambda p: "%s %s" % p, vpairs))


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
