import sys
import re
import random
import math
import copy
import time
from heapq import heappush, heappop, heapify
from functools import cmp_to_key
from bisect import bisect_left, bisect_right
from collections import defaultdict, deque, Counter
from typing import *

from main import FarmSimulator

# sys.setrecursionlimit(1000000)

# input aliases
input = sys.stdin.readline
getS = lambda: input().strip()
getN = lambda: int(input())
getList = lambda: list(map(int, input().split()))
getZList = lambda: [int(x) - 1 for x in input().split()]

"""
後々一つのファイルにまとめる必要があるけど、さすがにシミュレータをソルバ同じファイルは見づらいので分ける
"""


class BruteForceSolver(object):
    def __init__(self):
        self.simulator = FarmSimulator()
        self.max_harvester = 0
        self.operations_tmp = []

    def iteration(self):
        t_start = time.time()
        max_score = 0
        max_operations = []
        for i in range(20, 40):
            if time.time() - t_start > 1.7:
                break
            self.operations_tmp = []
            self.max_harvester = i
            self.simulator.reset()

            self.solve()

            # print("iteration: {}, score: {}".format(i, self.simulator.score))
            if self.simulator.score > max_score:
                max_score = self.simulator.score
                max_operations = self.operations_tmp

        for operation in max_operations:
            print(*operation)

        # print(max_score)

    def solve(self):
        for turn in range(self.simulator.t):
            self.step()

    def step(self):
        simulator = self.simulator
        lazy_y, lazy_x = -1, -1
        max_v = 0
        max_y, max_x = -1, -1
        for y, row in enumerate(simulator.vegetables):
            for x, cell_val in enumerate(row):
                if simulator.harvesters[y][x]:
                    if cell_val == 0:
                        lazy_y, lazy_x = y, x
                else:
                    if cell_val > max_v:
                        max_y, max_x = y, x
                        max_v = cell_val

        if max_v > 0:
            # とりあえずn個くらい買う
            able_to_buy = simulator.score >= (simulator.num_harvesters + 1) ** 3
            if self.simulator.num_harvesters < self.max_harvester and able_to_buy:
                self.op([max_y, max_x])
                return
            elif lazy_x != -1:
                self.op([lazy_y, lazy_x, max_y, max_x])
                return
            # if able_to_buy:
            #     self.op([max_y, max_x])
            #     return

        self.op([-1])
        return

    def find_lazy_harvester(self):
        simulator = self.simulator
        for y, row in enumerate(simulator.vegetables):
            for x, cell_val in enumerate(row):
                if cell_val == 0 and simulator.harvesters[y][x]:
                    return [y, x]

        return [-1, -1]

    def op(self, args):
        self.operations_tmp.append(args)
        self.simulator.step(args)
