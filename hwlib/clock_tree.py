#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hwlib.basic_circuits import Inverter
from hwlib.component import Component
import math
import random


class ClockTree:

    def __init__(self, design, fanout=4, vsrc=None, invSize="1x"):
        self.design = design
        self.vsrc = vsrc
        self.invSize = invSize
        self.fanout = fanout
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
            newTerminals = []
            groupDriver = Inverter(self.design, self.invSize)
            groupDriver.setVdd(self.vsrc)
            groupSize = 0
            for t in terminals:
                if groupSize >= self.fanout:
                    newTerminals.append(groupDriver.input)
                    groupDriver = Inverter(self.design, self.invSize)
                    groupDriver.setVdd(self.vsrc)
                    groupSize = 0
                self.design.connect(t, groupDriver.output)
                groupSize += 1
            newTerminals.append(groupDriver.input)
            terminals = newTerminals

        lastTerminal = terminals[0]
        # Cannot have an odd number of levels
        if levels % 2 == 1:
            i = Inverter(self.design, self.invSize)
            i.setVdd(self.vsrc)
            self.design.connect(lastTerminal, i.output)
            lastTerminal = i.input
        self.design.connect(self.input, lastTerminal)
