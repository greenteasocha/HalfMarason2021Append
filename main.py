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

# sys.setrecursionlimit(1000000)

# input aliases
input = sys.stdin.readline
getS = lambda: input().strip()
getN = lambda: int(input())
getList = lambda: list(map(int, input().split()))
getZList = lambda: [int(x) - 1 for x in input().split()]


"""
※※注意点, 方針など※※ 
- 入力がy, x なので、盤面を表す二次元配列もarr[y][x]の形でアクセスすることにする
"""


# ================================== DATACLASSES ==================================
class VegetableStateChange(object):
    def __init__(self, val):
        assert len(val) == 4 and type(val[3]) == bool, "Invalid value for State change instance"
        self.__y, self.__x, self.__value, self.__is_growth = val

    def __repr__(self):
        return "[{}, {}, {}, {}]".format(self.__y, self.__x, self.__value, self.__is_growth)

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def value(self):
        return self.__value

    @property
    def is_growth(self):
        # notice: True: Growth, False:Wither
        return self.__is_growth


class VegetableSingleLineInput(object):
    def __init__(self, val):
        self.val = val

    @property
    def val(self):
        return self.__val

    @val.setter
    def val(self, input_val):
        assert len(input_val) == 5, "Invalid Input for a vegetable: {}".format(input_val)
        self.__val = input_val


class VegetablesDataInputs(object):
    def __init__(self, num_vegetables):
        self.__vegetables: List[VegetableSingleLineInput] = []
        for i in range(num_vegetables):
            v = VegetableSingleLineInput(getList())
            self.__vegetables.append(v)

    @property
    def vegetables(self):
        # TODO? setter消してもgetされたらappendとかの操作はされてしまうのどうにかならないかな？
        return self.__vegetables


# ================================== HELPER ==================================
def calculate_connection_cells(harvester: List[List[int]], y: int, x: int)-> int:
    """
    指定された(y,x)を含むような、連結した収穫期の数をカウントする
    小さいヘルパーメソッドなので帰り値以外の型とかは適当に
    TODO: 多分UnionFindとかで高速に計算できるが、削除やサイズ管理が面倒なので見送り
    """
    if harvester[y][x] == 0:
        return 0

    n = len(harvester)  # 正方形と仮定

    count: int = 1
    moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    visited = [[0 for i in range(n)] for j in range(n)]  # np.zeros_likeほしい pypyにも
    visited[y][x] = 1

    q = deque()
    q.append((y, x))
    while q:
        cy, cx = q.pop()
        for dy, dx in moves:
            ny, nx = cy + dy, cx + dx
            if ny < 0 or nx < 0 or ny >= n or nx >= n:
                continue
            if harvester[ny][nx] and not visited[ny][nx]:
                count += 1
                q.append((ny, nx))
                visited[ny][nx] = 1
    return count


class ValidationHelper(object):
    # TODO? validatorが複数必要になったら、parseargsとrulesを継承して作れるような感じにしたいな
    def __init__(self, *args):
        self.__args = args
        self.__parse_args()

    def __parse_args(self):
        # 初期化時の引数を分かりやすく分解し解きたい時はここに記述する
        self.__n = self.__args[0]
        self.__harvesters = self.__args[1]

    def validate(self, op):
        assert self.__rules(op), "Invalid Operation: {}".format(op)

    def __rules(self, op):
        if len(op) == 1:
            # 1手パス(-1) 以外
            if op[0] != -1:
                return False
        elif len(op) == 2:
            # 収獲機がすでにある場合
            y, x = op
            if self.__harvesters[y][x]:
                return False
        elif len(op) == 4:
            # 収獲機が移動元にない or 移動先にすでにある場合
            # AtCoderの問題原文では同じ場所への移動を許可しているが、パスで代用できるため想定しない
            cy, cx, ny, nx = op
            if self.__harvesters[ny][nx] or not self.__harvesters[cy][cx]:
                return False
        else:
            # フォーマットの時点で無無効
            return False

        return True


# ================================== SIMULATOR ==================================
class FarmSimulator(object):
    """
    農場のシミュレーションをするクラス
    操作一覧
    - construct(__init__): シミュレータのセットアップを行う。ここで入力ファイルの読み込みはすべて完了
    - step               : 操作列を引数として渡し、ターンを進める
    - reset              : 盤面とターン数を初期値に戻す
    - properties         : 現在の状況を把握するためのプロパティは取得できる
    """
    def __init__(self):
        # properties(constants and values)
        # self.n = 16            # size of farm (N * N cells)
        # self.m = 5000          # number of vegetables
        # self.t = 1000          # total turns
        self.n = 9  # size of farm (N * N cells)
        self.m = 4  # number of vegetables
        self.t = 10  # total turns
        self.__t_current = 0       # current turn
        self.__score = 1           # current score
        self.__num_harvesters = 0  # current harvesters

        # properties(states)
        self.__vegetables_changes_by_time: List[List[VegetableStateChange]] = [[] for i in range(self.t + 1)]
        self.__vegetables: List[List[int]] = [[0 for i in range(self.n)] for j in range(self.n)]
        self.__harvesters: List[List[int]] = [[0 for i in range(self.n)] for j in range(self.n)]

        # properties(helpers)
        self.__validator = ValidationHelper(self.n, self.__harvesters)

        # read inputs
        # assert \
        #     getList() == [self.n, self.m, self.t],\
        #     "Invalid Input: [N, M, T] should be [{}, {}, {}]".format(self.n, self.m, self.t)
        getList()
        self.setup()

    def setup(self):
        # 野菜の生え/枯れは入力に対して固定なので、変なところで更新されないようにする
        # TODO: static的な枠組みを使ったほうが上手くやれるかも
        assert \
            self.__vegetables_changes_by_time == [[] for i in range(self.t + 1)], \
            "State changes can't be re-initialized."

        vegetables_input = VegetablesDataInputs(self.m)
        for vegetable in vegetables_input.vegetables:
            r, c, s, e, v = vegetable.val
            growth = VegetableStateChange([r, c, v, True])
            wither = VegetableStateChange([r, c, 0, False])
            self.__vegetables_changes_by_time[s].append(growth)
            self.__vegetables_changes_by_time[e+1].append(wither)  # 該当ターン(e)の最後 = 次のターン(e+1)の最初に消える

    def reset(self):
        # 盤面とターンをリセットする
        self.__t_current = 0
        self.__vegetables = [[0 for i in range(self.n)] for j in range(self.n)]
        self.__harvesters = [[0 for i in range(self.n)] for j in range(self.n)]

    def step(self, op: List):
        # TODO: そのターンでの行動を受け付け、1ターン勧める
        self.__validator.validate(op)

        self.__step_vegetable()
        self.__step_operation(op)
        self.__step_calculate_score()
        self.__t_current += 1
        return

    def __step_vegetable(self):
        # 野菜を生やしたり枯らしたりする
        changes: List[VegetableStateChange] = self.__vegetables_changes_by_time[self.__t_current]
        for change in changes:
            if change.is_growth:
                self.__vegetables[change.y][change.x] = change.value
            else:
                self.__vegetables[change.y][change.x] = 0

        return

    def __step_operation(self, op: List):
        # 受け付けた操作に応じて状態を変化させる
        if op == [-1]:
            return
        elif len(op) == 2:
            y, x = op
            self.__num_harvesters += 1
            self.__score -= self.__num_harvesters ** 3
            self.__harvesters[y][x] = 1
            return
        elif len(op) == 4:
            cy, cx, ny, nx = op
            self.__harvesters[ny][nx] = 1
            self.__harvesters[cy][cx] = 0
            return

    def __step_calculate_score(self):
        # スコア計算をする
        for y, row in enumerate(self.__vegetables):
            for x, cell_val in enumerate(row):
                if cell_val != 0 and self.__harvesters[y][x]:
                    self.__vegetables[y][x] = 0 # 収獲
                    self.__score += cell_val * calculate_connection_cells(self.__harvesters, y, x) # スコア加算


    @property
    def t_current(self):
        return self.__t_current

    @property
    def score(self):
        return self.__score

    @property
    def vegetables_changes_by_time(self):
        return self.__vegetables_changes_by_time

    @property
    def vegetables(self):
        return self.__vegetables

    @property
    def harvesters(self):
        return self.__harvesters

    @property
    def num_harvesters(self):
        return self.__num_harvesters


S = FarmSimulator()
a = 1

for i in range(10):
    S.step(getList())

    print(S.score)
