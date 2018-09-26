#!/usr/bin/env python3

from events import ClientSendNewQueryEvent, ClientResendQueryEvent

class Client():
    def __init__(self, queryGenerator, frontEndNode, backOff, eventsQueue, stats):
        self.queryGenerator = queryGenerator
        self.frontEndNode = frontEndNode
        self.backOff = backOff
        self.eventsQueue = eventsQueue
        self.stats = stats

    def start(self):
        self.eventsQueue.push(ClientSendNewQueryEvent(0, self))

    def sendQuery(self, query):
        if self.frontEndNode.processQuery(query):
            self.stats.queryCount += 1
            self.eventsQueue.push(ClientSendNewQueryEvent(self.stats.currentStep + 1, self))
        else:
            self.stats.retries += 1
            self.eventsQueue.push(ClientResendQueryEvent(self.stats.currentStep + self.backOff, query, self))

    def sendNewQuery(self):
        self.sendQuery(self.queryGenerator.nextQuery())

    def resendQuery(self, query):
        self.sendQuery(query)