#!/usr/bin/env python3

class Stats():
    def __init__(self):
        self.currentStep = 0
        self.currentSecond = 0
        self.queryCount = 0
        self.retries = 0
        self.frontEndAnswers = 0
        self.backEndAnswers = 0

    def queryRate(self):
        return self.queryCount / self.currentSecond

    def frontEndThroughput(self):
        return self.frontEndAnswers / self.currentSecond
        
    def backEndThroughput(self):
        return self.backEndAnswers / self.currentSecond

    def totalThroughput(self):
        return self.frontEndThroughput() + self.backEndThroughput()

    def retryCount(self):
        return self.retries / self.currentSecond

    def __str__(self):
        return 't = {}\nQuery rate: {}\nRetries: {}\nFE throughput: {}\nBE throughput: {}\nTotal througput: {}'  \
            .format(self.currentSecond,
                self.queryRate(),
                self.retryCount(),
                self.frontEndThroughput(),
                self.backEndThroughput(),
                self.totalThroughput())