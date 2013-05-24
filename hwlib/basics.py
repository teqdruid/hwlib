#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hwlib.component import Component


class Voltage(Component):

    netlist_format = "V{id} {connections} {voltage}V"
    connection_names = ['minus', 'plus']

    def __init__(self, design, voltage):
        Component.__init__(self, design)
        self.voltage = voltage


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
