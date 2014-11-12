#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hwlib.component import Component, NetlistFormatter

class Wire(Component):

                # Including inductance causes SPICE to not converge
                # "L{id}_seg{sn} {sb}_ri {sb} {inductance}\n" + \

    seg_format = "R{id}_seg{sn} {sa} {sb} {resistance}\n" + \
                 "Cg{id}_seg{sn} 0 {sb} {groundcap}\n"

    cpl_format = "Cc{id}_seg{sn} {ca} {cb} {cplcap}\n"
    connection_names = ['a', 'b']

    def __init__(self, design, length, layer="M1", segments=2):
        Component.__init__(self, design)
        self.length = length
        self.layer = layer
        self.segments = segments
        self.coupled = []
        self.resistance = design.__dict__[self.layer + "ResPerM"] * length / segments
        self.inductance = design.__dict__[self.layer + "IndPerM"] * length / segments
        self.groundcap = design.__dict__[self.layer + "GndCapPerM"] * length / segments
        self.couplecap = design.__dict__[self.layer + "CoupCapPerM"] * length / segments

    # Couple this wire with an adjacent one at minimum spacing
    def couple(self, wire):
        assert wire.segments == self.segments
        assert wire.layer == self.layer
        assert wire.length == self.length
        self.coupled.append(wire)

    def intermediate(self, f, i):
        return f.vformat("r{id}_seg{sn}", [], {"id": self.id, "sn": i})

    def get_spice_line(self):
        f = NetlistFormatter()
        ret = ""
        for i in range(self.segments):
            d = dict(self.__class__.__dict__)
            d.update(self.__dict__)
            d.update({
                "sn": i,
                "sa": self.intermediate(f, i-1) if i > 0 else self.get_connection_str("a"),
                "sb": self.intermediate(f, i) if i < (self.segments - 1) else self.get_connection_str("b")
            })
            ret += f.vformat(self.seg_format, [] , d)

            for cw in self.coupled:
                d.update({
                    "ca": self.intermediate(f, i) if i < (self.segments - 1) else self.get_connection_str("b"),
                    "cb": cw.intermediate(f, i) if i < (cw.segments - 1) else cw.get_connection_str("b"),
                    "cplcap": self.couplecap,
                })
                ret += f.vformat(self.cpl_format, [] , d)

        return ret

