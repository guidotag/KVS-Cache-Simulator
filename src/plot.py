#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

class Plotter():
    def __init__(self):
        params = {'backend': 'ps',
              'text.latex.preamble': ['\usepackage{gensymb}'],
              'axes.labelsize': 10,
              'axes.titlesize': 10,
              'font.size': 10,
              'legend.fontsize': 10,
              'xtick.labelsize': 10,
              'ytick.labelsize': 10,
              'text.usetex': True,
              # 'figure.figsize': [4, 4],
              'font.family': 'serif'
        }
        matplotlib.rcParams.update(params)

    def plotThroughputVsWorkingSetNoCache(self, dataFile, plotFilePath):
        plt.figure(figsize = (4, 3))
        plt.grid(b = True, axis = 'y', linestyle = 'dashed')
        plt.xlabel('Size of working set')
        plt.xscale('log')
        plt.ylabel('Overall throughput (kQPS)')
        plt.xlim(1, 1000000)
        plt.xticks(np.logspace(0, 6, 7, endpoint = True))
        plt.ylim(0, 1000)
        plt.yticks(np.linspace(0, 1000, 6, endpoint = True))

        X, Y = [], []
        for line in dataFile:
            (x, th) = line.split()
            X.append(int(x))
            Y.append(float(th))

        plt.plot(np.array(X), np.array(Y), color = "red", linewidth = 1.0, linestyle = "-", marker = '+')
        plt.tight_layout()
        plt.savefig(plotFilePath)
        # plt.show()

    def plotThroughputVsWorkingSet(self, dataFile, plotFilePath):
        plt.figure(figsize = (4, 3))
        plt.grid(b = True, axis = 'y', linestyle = 'dashed')
        plt.xlabel('Size of working set')
        plt.xscale('log')
        plt.ylabel('Overall throughput (kQPS)')
        plt.xlim(1000, 1000000)
        plt.xticks(np.logspace(3, 6, 4, endpoint = True))
        plt.ylim(0, 1000)
        plt.yticks(np.linspace(0, 1400, 8, endpoint = True))

        X, Y1, Y2 = [], [], []
        for line in dataFile:
            (x, th, bth) = line.split()
            X.append(int(x))
            Y1.append(float(th))
            Y2.append(float(bth))

        plt.plot(np.array(X), np.array(Y1), label = "Total", color = "red", linewidth = 1.0, linestyle = "-", marker = '+')
        plt.plot(np.array(X), np.array(Y2), label = "Back-end", color = "blue", linewidth = 1.0, linestyle = "--", marker = 'x')
        plt.legend(frameon = True)
        plt.tight_layout()
        plt.savefig(plotFilePath)

    def plotThroughputVsCacheSize(self, dataFile, boundFile, plotFilePath):
        plt.figure(figsize = (4, 3))
        plt.grid(b = True, axis = 'y', linestyle = 'dashed')
        plt.xlabel('Size of cache')
        plt.xscale('log')
        plt.ylabel('Overall throughput (kQPS)')
        plt.xlim(10, 100000)
        plt.xticks(np.logspace(1, 5, 5, endpoint = True))
        plt.ylim(0, 900)
        plt.yticks(np.linspace(0, 900, 10, endpoint = True))

        X, Y = [], []
        for line in dataFile:
            (x, th) = line.split()
            X.append(int(x))
            Y.append(float(th))
        plt.plot(np.array(X), np.array(Y), label = "Worst case", color = "red", linewidth = 1.0, linestyle = "-", marker = '+')

        X, Y = [], []
        for line in boundFile:
            (x, y) = line.split()
            X.append(int(x))
            Y.append(float(y))
        plt.plot(np.array(X), np.array(Y), label = "Theory bound", color = "blue", linewidth = 1.0, linestyle = "--")

        plt.legend(frameon = True)
        plt.tight_layout()
        plt.savefig(plotFilePath)

    def plotThroughputVsCacheSizeLRUCache(self, dataFile1, dataFile2, plotFilePath):
        plt.figure(figsize = (4, 3))
        plt.grid(b = True, axis = 'y', linestyle = 'dashed')
        plt.xlabel('Size of cache')
        plt.xscale('log')
        plt.ylabel('Overall throughput (kQPS)')
        plt.xlim(10, 100000)
        plt.xticks(np.logspace(1, 5, 5, endpoint = True))
        plt.ylim(0, 900)
        plt.yticks(np.linspace(0, 900, 10, endpoint = True))

        X, Y = [], []
        for line in dataFile1:
            (x, th) = line.split()
            X.append(int(x))
            Y.append(float(th))
        plt.plot(np.array(X), np.array(Y), label = "Perfect cache", color = "red", linewidth = 1.0, linestyle = "-", marker = "+")

        X, Y = [], []
        for line in dataFile2:
            (x, th) = line.split()
            X.append(int(x))
            Y.append(float(th))
        plt.plot(np.array(X), np.array(Y), label = "LRU cache", color = "blue", linewidth = 1.0, linestyle = "--", marker = "v")

        plt.legend(frameon = True)
        plt.tight_layout()
        plt.savefig(plotFilePath)