#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hwlib.basic_circuits import Inverter
from hwlib.component import Component
import math
import random


class ClockTree:

    def __init__(self, design, fanout=4, vsrc=None,
                 invSize="1x", allowOdd=False):
        self.design = design
        self.vsrc = vsrc
        self.invSize = invSize
        self.fanout = fanout
        self.allowOdd = allowOdd
        self.input = Component.Terminal(self)

    def driveNet(self, net):
        if isinstance(net, Component.Terminal):
            net = net.net
        terminals = list(net.terminals)
        random.shuffle(terminals)
        numTerms = len(terminals)
        levelsFrac = math.log(numTerms) / math.log(self.fanout)
        print "Expecting to create %f levels" % (levelsFrac)

        for term in terminals:
            self.design.disconnect(term)

        levels = 0
        while len(terminals) > 1:
            levels += 1
            numGroups = int(math.ceil(float(len(terminals)) / self.fanout))
            drivers = [Inverter(self.design, self.invSize)
                       for i in range(numGroups)]
            for gn in range(numGroups):
                driver = drivers[gn]
                driver.setVdd(self.vsrc)
                for tn in range(self.fanout):
                    idx = tn + gn * self.fanout
                    if idx < len(terminals):
                        t = terminals[idx]
                        self.design.connect(t, driver.output)

            terminals = [driver.input for driver in drivers]

        lastTerminal = terminals[0]

        # Are we inverting the output?
        if levels % 2 == 1:
            self.isOdd = True
            if not self.allowOdd:
                # Cannot have an odd number of levels
                i = Inverter(self.design, self.invSize)
                i.setVdd(self.vsrc)
                self.design.connect(lastTerminal, i.output)
                lastTerminal = i.input
        else:
            self.isOdd = False
        self.design.connect(self.input, lastTerminal)
