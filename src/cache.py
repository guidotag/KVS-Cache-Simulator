#!/usr/bin/env python3

import random

class PerfectCacheSystem():
    def __init__(self, cacheSize, queryRange):
        self.cache = PerfectCache(cacheSize)
        self.queryGenerator = CyclicQueryGenerator(queryRange)

class PerfectCache():
    def __init__(self, size):
        self.size = size

    def lookup(self, key):
        if key < self.size:
            return True
        return False

    def onAnswer(self, key):
        pass # We do not insert the queried key because the most popular keys are already cached

class RandomQueryGenerator():
    def __init__(self, queryRange, seed = 1234567):
        self.queryRange = queryRange
        random.seed(seed)

    def nextQuery(self):
        return random.randint(0, self.queryRange - 1)

# Queries some a key from 0, ..., queryRange - 1, in a cyclic fashion
class CyclicQueryGenerator():
    def __init__(self, queryRange):
        self.queryRange = queryRange
        self.nextKey = 0
    
    def nextQuery(self):
        key = self.nextKey
        self.nextKey = (self.nextKey + 1) % self.queryRange
        return key

class LRUCacheSystem():
    def __init__(self, cacheSize, queryRange):
        self.cache = LRUCache(cacheSize)
        self.queryGenerator = CyclicQueryGenerator(queryRange)

class LRUCache():
    def __init__(self, size):
        self.size = size
        self.table = []

    def lookup(self, key):
        if self.table.count(key) > 0:
            self.table.remove(key)
            self.table.append(key)
            return True
        return False

    def insert(self, key):
        if len(self.table) < self.size:
            self.table.append(key)
        else:
            self.table.pop(0)
            self.table.append(key)

    def onAnswer(self, key):
        if not self.lookup(key):
            self.insert(key)