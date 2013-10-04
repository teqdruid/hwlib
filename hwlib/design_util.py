#!/usr/bin/env python
# -*- coding: utf-8 -*-

from basics import NMos, PMos


class EasyCMOS:

    def __init__(self, design, vdd, vss):
        self.design = design
        self.vdd_name = vdd
        self.vss_name = vss

    def p(self, gate, w="1x"):
        p = PMos(self.design, w)
        p.body = self.vdd_name
        p.gate = gate
        return (p.drain, p.source)

    def n(self, gate, w="1x"):
        n = NMos(self.design, w)
        n.body = self.vss_name
        n.gate = gate
        return (n.drain, n.source)

    def par(self, devs):
        assert len(devs) > 0
        (drain, source) = devs[0]
        for d in devs[1:]:
            self.design.connect(drain, d[0])
            self.design.connect(source, d[1])
        return (drain, source)

    def ser(self, devs):
        assert len(devs) > 0
        (drain, source) = devs[0]
        for d in devs[1:]:
            self.design.connect(source, d[0])
            source = d[1]
        return (drain, source)
