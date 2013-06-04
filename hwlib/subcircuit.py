#!/usr/bin/env python
# -*- coding: utf-8 -*-

from design import Circuit
from component import Component


class Subcircuit(Circuit):

    def __init__(self, parent, id, ports):
        Circuit.__init__(self, parent)
        self.id = id
        self.ports = ports

    def print_netlist(self, stream):
        stream.write(".SUBCKT {name} {ports}\n".format(
                     name=self.id, ports=" ".join(self.ports)))
        self.print_components(stream)
        stream.write(".ENDS\n")


class SubcktComponent(Component):

    subckt_basename = ""
    netlist_format = "Xinv{id} {connections} {subckt}"
    suffix_components = []

    def __init__(self, design):
        Component.__init__(self, design)

        if self.has_suffix():
            self.subckt = self.subckt_basename + "_" + self.suffix()
        else:
            self.subckt = self.subckt_basename

        if not design.hassubckt(self.subckt):
            self.build_subckt(design)

    def has_suffix(self):
        return len(self.suffix_components) > 0

    def suffix(self):
        return "_".join(map(lambda c: "%s%s" % (c[0], getattr(self, c)),
                            self.suffix_components))

    def build_subckt(self, design):
        circuit = Subcircuit(design, self.subckt, self.connection_names)
        self.assemble_subckt(circuit)
        design.add_subckt(circuit)
