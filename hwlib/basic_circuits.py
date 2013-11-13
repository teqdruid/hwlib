#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subcircuit import SubcktComponent
from basics import NMos, PMos


class Inverter(SubcktComponent):

    subckt_basename = "Inverter"
    connection_names = ["input", "output", "vdd", "vss"]
    suffix_components = ["width", "ratio", "length"]

    def __init__(self, design, width="1x", ratio=None, length="1x"):
        self.width = design.width(width)
        self.length = design.length(length)
        self.ratio = ratio if ratio is not None else design.pn_ratio
        SubcktComponent.__init__(self, design)
        design.connect(self.vdd, design.vdd)
        design.connect(self.vss, design.vss)

    def setVdd(self, vdd):
        self.design.disconnect(self.vdd)
        self.design.connect(self.vdd, vdd)

    def assemble_subckt(self, design):
        n = NMos(design, self.width, self.length)
        p = PMos(design, (self.width * self.ratio), self.length)
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
    connection_names = ["a", "b", "en", "enp", "vdd", "vss"]
    suffix_components = ["width", "ratio"]

    def __init__(self, design, width="1x", ratio=None):
        self.width = design.width(width)
        self.ratio = ratio if ratio is not None else design.pn_ratio
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
    connection_names = ["input", "output", "en", "enp", "vdd", "vss"]
    suffix_components = ["width", "ratio"]

    def __init__(self, design, width="1x", ratio=None):
        self.width = design.width(width)
        self.ratio = ratio if ratio is not None else design.pn_ratio
        SubcktComponent.__init__(self, design)
        design.connect(self.vdd, design.vdd)
        design.connect(self.vss, design.vss)

    def setVdd(self, vdd):
        self.design.disconnect(self.vdd)
        self.design.connect(self.vdd, vdd)

    def assemble_subckt(self, design):
        ne = NMos(design, self.width)
        pe = PMos(design, (self.width * self.ratio))

        ne.source = "output"
        pe.source = "output"
        ne.gate = "en"
        pe.gate = "enp"
        ne.body = "vss"
        pe.body = "vdd"
        design.connect(self.vdd, design.vdd)
        design.connect(self.vss, design.vss)
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


class Latch(SubcktComponent):

    subckt_basename = "Latch"
    connection_names = ["d", "q", "qp", "en", "enp", "vdd", "vss"]
    suffix_components = []

    def __init__(self, design):
        SubcktComponent.__init__(self, design)
        design.connect(self.vdd, design.vdd)
        design.connect(self.vss, design.vss)

    def assemble_subckt(self, design):
        self.i1 = Inverter(design)
        self.i1.output = "qp"

        self.i2 = Inverter(design)
        self.i2.output = "q"
        self.i2.input = "qp"

        self.fbpg = PassGate(design)
        self.fbpg.en = "enp"
        self.fbpg.enp = "en"
        self.fbpg.a = "q"
        design.connect(self.fbpg.b, self.i1.input)

        self.inputPG = PassGate(design)
        self.inputPG.en = "en"
        self.inputPG.enp = "enp"
        self.inputPG.a = "d"
        design.connect(self.inputPG.b, self.fbpg.b)

        self.i1.vdd = "vdd"
        self.i2.vdd = "vdd"
        self.fbpg.vdd = "vdd"
        self.inputPG.vdd = "vdd"

        self.i1.vss = "vss"
        self.i2.vss = "vss"
        self.fbpg.vss = "vss"
        self.inputPG.vss = "vss"
