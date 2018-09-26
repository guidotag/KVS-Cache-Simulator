#!/usr/bin/env python3

import random
from events import BackEndAnswerQueryEvent

class BackEndNode():
    def __init__(self, queueSize, stepsPerResponse, eventsQueue, stats):
        self.queueSize = queueSize
        self.stepsPerResponse = stepsPerResponse
        self.eventsQueue = eventsQueue
        self.stats = stats
        self.queue = []
        self.busy = False

    def setFrontEndNode(self, node):
        self.frontEndNode = node

    def lookup(self, key):
        self.eventsQueue.push(BackEndAnswerQueryEvent(self.stats.currentStep + self.stepsPerResponse, key, self))

    def processQuery(self, key):
        if len(self.queue) == self.queueSize:
            return False

        if not self.busy:
            self.lookup(key)
            self.busy = True
        else:
            self.queue.append(key)

        return True

    def answerQuery(self, key):
        self.frontEndNode.receiveAnswer(key)
        self.stats.backEndAnswers += 1
        if len(self.queue) == 0:
            self.busy = False
        else:
            nextKey = self.queue[0]
            self.queue.pop(0)
            self.lookup(nextKey)

class FrontEndNode():
    def __init__(self, cache, backEndNodes, stats):
        self.cache = cache
        self.backEndNodes = backEndNodes
        self.stats = stats
        for node in self.backEndNodes:
            node.setFrontEndNode(self)

    @staticmethod
    def hash(x):
        # From https://stackoverflow.com/a/12996028
        x = ((x >> 16) ^ x) * 0x45d9f3b
        x = ((x >> 16) ^ x) * 0x45d9f3b
        x = (x >> 16) ^ x
        return x

    def processQuery(self, key):
        if self.cache.lookup(key):
            # Key is cached, result would be sent to client
            self.stats.frontEndAnswers += 1
            return True
        else:
            index = FrontEndNode.hash(key) % len(self.backEndNodes)
            return self.backEndNodes[index].processQuery(key)

    def receiveAnswer(self, key):
        self.cache.onAnswer(key)