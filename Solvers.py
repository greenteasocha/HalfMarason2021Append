import sys
import re
import random
import math
import copy
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
            if lazy_x != -1:
                self.op([lazy_y, lazy_x, max_y, max_x])
                return
            if simulator.score >= (simulator.num_harvesters + 1) ** 3:
                self.op([max_y, max_x])
                return
                # if cell_val != 0 and not simulator.harvesters[y][x]:
                #     if simulator.score >= (simulator.num_harvesters + 1) ** 3:
                #         py, px = self.find_lazy_harvester()
                #         if py == -1:
                #             self.op([y, x])
                #         else:
                #             self.op([py, px, y, x])
                #         return

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
        print(*args)
        self.simulator.step(args)
