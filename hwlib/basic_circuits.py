#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subcircuit import SubcktComponent
from basics import NMos, PMos


class Inverter(SubcktComponent):

    subckt_basename = "Inverter"
    netlist_format = "Xinv{id} {connections} {subckt}"
    connection_names = ["input", "output", "vdd", "vss"]
    suffix_components = ["width", "ratio"]

    def __init__(self, design, width="1x", ratio=2):
        self.width = design.length(width)
        self.ratio = ratio
        SubcktComponent.__init__(self, design)
        design.connect(self.vdd, design.vdd)
        design.connect(self.vss, design.vss)

    def assemble_subckt(self, design):
        n = NMos(design, self.width)
        p = PMos(design, (self.width * self.ratio))
        n.drain = "vss"
        p.drain = "vdd"
        n.gate = "input"
        p.gate = "input"
        n.source = "output"
        p.source = "output"
        n.body = "vss"
        p.body = "vdd"


class PassGate(SubcktComponent):

    subckt_basename = "PassGate"
    netlist_format = "Xpg{id} {connections} {subckt}"
    connection_names = ["a", "b", "en", "enp", "vdd", "vss"]
    suffix_components = ["width", "ratio"]

    def __init__(self, design, width="1x", ratio=2):
        self.width = design.length(width)
        self.ratio = ratio
        SubcktComponent.__init__(self, design)
        design.connect(self.vdd, design.vdd)
        design.connect(self.vss, design.vss)

    def assemble_subckt(self, design):
        n = NMos(design, self.width)
        p = PMos(design, (self.width * self.ratio))
        n.drain = "a"
        p.drain = "a"
        n.gate = "en"
        p.gate = "enp"
        n.source = "b"
        p.source = "b"
        n.body = "vss"
        p.body = "vdd"


class StackedTristateInverter(SubcktComponent):

    subckt_basename = "STriInverter"
    netlist_format = "Xstinv{id} {connections} {subckt}"
    connection_names = ["input", "output", "en", "enp", "vdd", "vss"]
    suffix_components = ["width", "ratio"]

    def __init__(self, design, width="1x", ratio=2):
        self.width = design.length(width)
        self.ratio = ratio
        SubcktComponent.__init__(self, design)
        design.connect(self.vdd, design.vdd)
        design.connect(self.vss, design.vss)

    def assemble_subckt(self, design):
        ne = NMos(design, self.width)
        pe = PMos(design, (self.width * self.ratio))

        ne.source = "output"
        pe.source = "output"
        ne.gate = "en"
        pe.gate = "enp"
        ne.body = "vss"
        pe.body = "vdd"

        ni = NMos(design, self.width)
        pi = PMos(design, (self.width * self.ratio))
        ni.gate = "input"
        pi.gate = "input"
        ni.drain = "vss"
        pi.drain = "vdd"
        ni.body = "vss"
        pi.body = "vdd"

        design.pair({ne.drain: ni.source,
                     pe.drain: pi.source})
