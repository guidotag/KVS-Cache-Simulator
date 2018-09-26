#!/usr/bin/env python3

import time
from math import sqrt, log
from cache import PerfectCacheSystem, LRUCacheSystem
from nodes import BackEndNode, FrontEndNode
from client import Client
from events import EventsQueue, ClientSendNewQueryEvent, ClientResendQueryEvent, BackEndAnswerQueryEvent
from stats import Stats
from plot import Plotter

class Simulator():
    def __init__(self,
        backEndNodesCount,      # Number of back-end nodes
        backEndNodesQueueSize,
        responseRate,           # QPS answered by back-end nodes
        queryRateFactor,        # queryRate = queryRateFactor * responseRate
        cacheSystem,
        simulationLength):      # Number of seconds simulated

        assert (simulationLength >= 1), "Simulation should last at least 1 second"

        self.responseRate = responseRate
        self.queryRateFactor = queryRateFactor
        self.simulationLength = simulationLength
        self.stepsPerSecond = queryRateFactor * responseRate
        self.stepsPerResponse = queryRateFactor
        self.cacheSystem = cacheSystem

        self.stats = Stats()

        self.eventsQueue = EventsQueue()

        backEndNodes = []
        for i in range(0, backEndNodesCount):
            backEndNodes.append(BackEndNode(backEndNodesQueueSize, self.stepsPerResponse, self.eventsQueue, self.stats))

        self.frontEndNode = FrontEndNode(cacheSystem.cache, backEndNodes, self.stats)

        backOff = self.stepsPerResponse * backEndNodesQueueSize
        self.client = Client(cacheSystem.queryGenerator, self.frontEndNode, backOff, self.eventsQueue, self.stats)

    def run(self):
        self.client.start()

        while True:
            nextEvent = self.eventsQueue.pop()

            self.stats.currentStep = nextEvent.step
            nextSecond = self.stats.currentStep / self.stepsPerSecond
            if self.stats.currentSecond < nextSecond:
                self.stats.currentSecond = nextSecond

            if self.stats.currentSecond == self.simulationLength:
                break

            nextEvent.execute()

        return self.stats

def neat(headers, values):
    n = len(headers)
    assert (n == len(values))
    fmt = ''
    for i in range(0, n):
        fmt += '{{{}:{{{}}}}}   '.format(i, n + i)

    return fmt.format(*(values + map(lambda x: len(x), headers)))

# Simulations for Figure 9
def throughputVsWorkingSetNoCache(outputFile, verbose):
    backEndNodesCount = 85
    cacheSize = 0
    backEndNodesQueueSize = 1000
    responseRate = 10000
    queryRateFactor = backEndNodesCount
    simulationLength = 1

    headers = ['     set', 'throughput (KQPS)']
    if verbose:
        print('Size of working set vs. Throughput - No cache (Fig. 9)')
        print(neat(headers, headers))

    mid = sqrt(10)
    for queryRange in [1, int(mid), 10, int(10 * mid), 100, int(100 * mid), 1000, int(1000 * mid),
                        10000, int(10000 * mid), 100000, int(100000 * mid), 1000000]:
        cacheSystem = PerfectCacheSystem(cacheSize, queryRange)
        sim = Simulator(
            backEndNodesCount,
            backEndNodesQueueSize,
            responseRate,
            queryRateFactor,
            cacheSystem,
            simulationLength)
        stats = sim.run()

        th = stats.totalThroughput() / 1000.0
        outputFile.write('{} {}\n'.format(queryRange, th))
        if verbose:
            print(neat(headers, [queryRange, th]))

# Simulations for Figure 10
def throughputVsWorkingSet(outputFile, verbose):
    backEndNodesCount = 85
    cacheSize = 3000 #8 * backEndNodesCount * log(backEndNodesCount, 10)
    backEndNodesQueueSize = 1000
    responseRate = 10000
    queryRateFactor = 2 * backEndNodesCount # Twice as the aggregate throughput, to stress the cache
    simulationLength = 1

    headers = ['     set', 'total throughput (KQPS)', 'backend throughput (KQPS)']
    if verbose:
        print('Size of working set vs. Throughput (Fig. 10)')
        print(neat(headers, headers))

    mid = sqrt(10)
    for queryRange in [3000, 4000, 5000, 6000,
                        10000, 20000, 30000, 70000,
                        100000, int(100000 * mid), 1000000]:
        cacheSystem = PerfectCacheSystem(cacheSize, queryRange)
        sim = Simulator(
            backEndNodesCount,
            backEndNodesQueueSize,
            responseRate,
            queryRateFactor,
            cacheSystem,
            simulationLength)
        stats = sim.run()

        th = stats.totalThroughput() / 1000.0
        bth = stats.backEndThroughput() / 1000.0
        outputFile.write('{} {} {}\n'.format(queryRange, th, bth))
        if verbose:
            print(neat(headers, [queryRange, th, bth]))

# Simulations for Figure 11
def throughputVsCacheSize(dataOutputFile, verbose):
    backEndNodesCount = 85
    backEndNodesQueueSize = 1000
    responseRate = 10000
    queryRateFactor = backEndNodesCount
    simulationLength = 1

    headers = ['      c', 'throughput (KQPS)']
    if verbose:
        print('Size of cache vs. Throughput (Fig. 11)')
        print(neat(headers, headers))

    mid = sqrt(10)

    for cacheSize in [10, int(10 * mid), 100, int(100 * mid),
                        1000, int(1000 * mid), 10000, int(10000 * mid), 100000]:
        minThroughput = queryRateFactor * responseRate
        for queryRange in [5, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]:
            cacheSystem = PerfectCacheSystem(cacheSize, queryRange)
            sim = Simulator(
                backEndNodesCount,
                backEndNodesQueueSize,
                responseRate,
                queryRateFactor,
                cacheSystem,
                simulationLength)
            stats = sim.run()
            minThroughput = min(minThroughput, stats.totalThroughput())

        th = minThroughput / 1000.0
        dataOutputFile.write('{} {}\n'.format(cacheSize, th))
        if verbose:
            print(neat(headers, [cacheSize, th]))

def throughputVsCacheSizeLRUCache(dataOutputFile, verbose):
    backEndNodesCount = 85
    backEndNodesQueueSize = 1000
    responseRate = 10000
    queryRateFactor = backEndNodesCount
    simulationLength = 1

    headers = ['      c', 'throughput (KQPS)']
    if verbose:
        print('Size of LRU cache vs. Throughput')
        print(neat(headers, headers))

    mid = sqrt(10)

    for cacheSize in [10, int(10 * mid), 100, int(100 * mid),
                        1000, int(1000 * mid), 10000, int(10000 * mid), 100000]:
        minThroughput = queryRateFactor * responseRate
        for queryRange in [5, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]:
            cacheSystem = LRUCacheSystem(cacheSize, queryRange)
            sim = Simulator(
                backEndNodesCount,
                backEndNodesQueueSize,
                responseRate,
                queryRateFactor,
                cacheSystem,
                simulationLength)
            stats = sim.run()
            minThroughput = min(minThroughput, stats.totalThroughput())

        th = minThroughput / 1000.0
        dataOutputFile.write('{} {}\n'.format(cacheSize, th))
        if verbose:
            print(neat(headers, [cacheSize, th]))

# Computes the maximum theoretical query rate (and thus, aggregate throughput) given
# the number of back end nodes and the response rate
def queryRateTheoryBound(dataOutputFile, verbose):
    backEndNodesCount = 85
    responseRate = 10000
    alpha = 2
    n = backEndNodesCount   # Just to simplify the formula below
    r = responseRate

    headers = ['      c', 'query rate (KQPS)']
    if verbose:
        print('Size of cache vs. Maximum query rate')
        print(neat(headers, headers))

    for cacheSize in range(10, 100001, 10):
        c = cacheSize
        rate = (2 * n * r) / (1 + sqrt(1 + (2 * (alpha ** 2) * n * log(n, 10)) / float(c - 1)))
        rate /= 1000
        dataOutputFile.write('{} {}\n'.format(cacheSize, rate))
        if verbose:
            print(neat(headers, [cacheSize, rate]))

def runExperiment(experimentFunction, dataFilePath, verbose):
    with open(dataFilePath + '.dat', 'w') as data:
        experimentFunction(data, verbose)

def plotExperiment(plotFunction, dataFilePath):
    with open(dataFilePath + '.dat', 'r') as data:
        plotFunction(data, dataFilePath + '.pdf')

if __name__ == '__main__':
    verbose = True
    simulate = True
    plot = True
    runThroughputVsWorkingSetNoCache = True and simulate
    runThroughputVsWorkingSet = True and simulate
    runThroughputVsCacheSize = True and simulate
    runQueryRateTheoryBound = True and simulate
    runThroughputVsCacheSizeLRUCache = True and simulate

    throughputVsWorkingSetNoCachePath = 'output/throughput_vs_working_set_no_cache'
    throughputVsWorkingSetPath = 'output/throughput_vs_working_set'
    throughputVsCacheSizePath = 'output/throughput_vs_cache_size'
    queryRateTheoryBoundPath = 'output/query_rate_theory_bound'
    throughputVsCacheSizeLRUCachePath = 'output/throughput_vs_cache_size_lru'

    if runThroughputVsWorkingSetNoCache:
        runExperiment(throughputVsWorkingSetNoCache,
            throughputVsWorkingSetNoCachePath,
            verbose)

    if runThroughputVsWorkingSet:
        runExperiment(throughputVsWorkingSet,
            throughputVsWorkingSetPath,
            verbose)

    if runThroughputVsCacheSize:
        runExperiment(throughputVsCacheSize,
            throughputVsCacheSizePath,
            verbose)

    if runQueryRateTheoryBound:
        runExperiment(queryRateTheoryBound,
            queryRateTheoryBoundPath,
            False)

    if runThroughputVsCacheSizeLRUCache:
        runExperiment(throughputVsCacheSizeLRUCache,
            throughputVsCacheSizeLRUCachePath,
            verbose)

    if plot:
        plt = Plotter()

        plotExperiment(plt.plotThroughputVsWorkingSetNoCache,
            throughputVsWorkingSetNoCachePath)

        plotExperiment(plt.plotThroughputVsWorkingSet,
            throughputVsWorkingSetPath)

        with open(throughputVsCacheSizePath + '.dat', 'r') as data1:
            with open(queryRateTheoryBoundPath + '.dat', 'r') as data2:
                plt.plotThroughputVsCacheSize(data1, data2, throughputVsCacheSizePath + '.pdf')

        with open(throughputVsCacheSizeLRUCachePath + '.dat', 'r') as data1:
            with open(throughputVsCacheSizePath + '.dat', 'r') as data2:
                plt.plotThroughputVsCacheSizeLRUCache(data1, data2, throughputVsCacheSizeLRUCachePath + '.pdf')