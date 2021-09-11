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
        for y, row in enumerate(simulator.vegetables):
            for x, cell_val in enumerate(row):
                if cell_val != 0 and not simulator.harvesters[y][x]:
                    if simulator.score >= (simulator.num_harvesters + 1) ** 3:
                        self.op([y, x])
                        return

        self.op([-1])
        return

    def op(self, args):
        print(*args)
        self.simulator.step(args)
