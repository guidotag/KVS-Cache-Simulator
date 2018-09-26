#!/usr/bin/env python3

import heapq

class EventsQueue():
    def __init__(self):
        self.queue = []

    def push(self, event):
        heapq.heappush(self.queue, event)

    def pop(self):
        answer = self.queue[0]
        heapq.heappop(self.queue)
        return answer

class Event():
    def __init__(self, step):
        self.step = step

    def __cmp__(self, other):
        return self.step > other.step

class ClientSendNewQueryEvent(Event):
    def __init__(self, step, client):
        Event.__init__(self, step)
        self.client = client

    def execute(self):
        self.client.sendNewQuery()

class ClientResendQueryEvent(Event):
    def __init__(self, step, query, client):
        Event.__init__(self, step)
        self.query = query
        self.client = client

    def execute(self):
        self.client.resendQuery(self.query)

class BackEndAnswerQueryEvent(Event):
    def __init__(self, step, key, backEndNode):
        Event.__init__(self, step)
        self.key = key
        self.backEndNode = backEndNode

    def execute(self):
        self.backEndNode.answerQuery(self.key)
        