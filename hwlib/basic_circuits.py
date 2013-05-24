#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subcircuit import SubcktComponent
from basics import NMos, PMos


class Inverter(SubcktComponent):

    subckt_basename = "Inverter"
    netlist_format = "Xinv{id} {connections} Inverter"
    connection_names = ["input", "output", "vdd", "vss"]

    def __init__(self, design):
        SubcktComponent.__init__(self, design)
        design.connect(self.vdd, design.vdd)
        design.connect(self.vss, design.vss)

    def assemble_subckt(self, design):
        n = NMos(design)
        p = PMos(design)
        n.drain = "vss"
        p.drain = "vdd"
        n.gate = "input"
        p.gate = "input"
        n.source = "output"
        p.source = "output"
        n.body = "vss"
        p.body = "vdd"
