from itertools import product
from typing import List, Tuple
from collections import deque

import random
from sudoku_core import Sudoku


class MinConflict(Sudoku):
    def __init__(self, board: List[List]) -> None:
        # CSP として初期化する
        self.initialize_as_csp(board)
        # 既に数字が埋まっている cell の集合を集めておく
        self.already_assigned_cells = {cell for cell in product(range(0, 9), range(0, 9)) if self.board[cell] != 0}
        # max iteration step num
        self.max_steps = 5000
        # 各 cell の conflict の数を格納する場所
        self.conflicts = {(row, col): -1 for row, col in product(range(0, 9), range(0, 9))}
        # cell の値を変えたときに影響のある cell の集合
        self.current_effected_cells = set()
        # debug
        self.debug_min_conflict_count = 0

    def solve(self) -> None:
        """min_conflict で解く
        """
        is_solved: bool = self.min_conflict()
        self.print()
        assert is_solved, 'not solved'
        assert self.is_solution(), 'not solution'

    def min_conflict(self) -> bool:
        """min_conflict の実装
        """
        # まず、初期解を作る。
        self.initialize_board()

        # max_steps の間だけ繰り返す
        for step in range(self.max_steps):
            self.debug_min_conflict_count += 1

            # もしここで解であるならば True
            if self.is_solution():
                return True
            # conflict を起こしている cell をランダムに選ぶ
            cell = self.choose_conflict_cell()
            # その cell の値として最も conflict が小さくなる value を選択する
            value = self.choose_min_conflict_value(cell)
            # その cell に value を set する
            self.set(cell, value)

        # max_step の中で処理が終わらなければ失敗
        return False

    def evaluate(self, cell: Tuple[int, int], value: int) -> float:
        """評価。 0 に近いほど良い評価。
        今回は、 conflict を起こした数を数える。
        """
        return len(self._get_conflict_cells(cell, value))

    def initialize_board(self) -> None:
        """初期解を作る
        """
        # 81 個の cell になるべく conflict が起きないように数字を入れていく
        for row in range(0, 9):

            # 一行に入る数は 1 から 9 の間の数。なので、行ごとに見て数字を入れていく
            # ただし、既に数字が入っているならそれは予め取り除く
            _already_assigned_values = {self.board[(row, i)] for i in range(0, 9)} - {0}
            _nums = list({i for i in range(1, 10)} - _already_assigned_values)
            random.shuffle(_nums)
            domain = deque(_nums)

            for col in range(0, 9):
                cell = (row, col)

                # 既に埋まっているならスキップ
                if cell in self.already_assigned_cells:
                    continue

                # cell 毎になるべく conflict が小さい value を選択する。
                # そのために、 conflict が 0 で無い限り値を一巡して調べるが、調べた値を以下の deque に入れる。後で元に戻す。
                _rest_domain = deque()
                min_conflict_value_eval = (-1, float('inf'))
                while len(domain) != 0:

                    # 評価をする。
                    value = domain.popleft()
                    eval = self.evaluate(cell, value)
                    if eval == 0:
                        # conflict が無いならそこに入れる。一番小さいやつだけ残す
                        self.board[cell] = value
                        break
                    else:
                        # conflict があるなら、これまで調べた中と比較して一番小さいやつだけ残しておく
                        min_conflict_value_eval = (value, eval) \
                            if min_conflict_value_eval[1] > eval else min_conflict_value_eval
                        _rest_domain.append(value)

                # 入れられなかったら、仕方が無いので、一番 conflict が小さかったところにいれる
                if self.board[cell] == 0:
                    v, e = min_conflict_value_eval
                    self.board[cell] = v
                    _rest_domain.remove(v)

                # domain を補充する
                domain += _rest_domain

    def choose_conflict_cell(self) -> Tuple[int, int]:
        """conflict を起こしている cell を一つ選ぶ
        """
        # もしも最近影響を及ぼした cell があるならそこから random に一つ選ぶ.
        # しかしながら、定めた確率で breaking tiesする
        self.current_effected_cells -= self.already_assigned_cells
        # if len(self.current_effected_cells) != 0 and random.randrange(0, 10000) != 0:
        if len(self.current_effected_cells) != 0:
            return random.choice(list(self.current_effected_cells))
        # conflict が起きている cell からランダムに一つ返す
        conflict_list = {c for c in product(range(0, 9), range(0, 9))
                         if self.evaluate(c, self.board[c]) != 0} - self.already_assigned_cells
        if len(conflict_list) != 0:
            return random.choice(list(conflict_list))
        # そうでなければ本当に random に cell を返す
        return random.choice(list({cell for cell in product(range(0, 9), range(0, 9))} - self.already_assigned_cells))

    def choose_min_conflict_value(self, cell: Tuple[int, int]) -> int:
        """cell に対して最も conflict が起きない value を返す
        """
        min_value_conflictnum = (-1, float('inf'))
        for num in range(1, 10):
            # 既に入っている数字ならば意味ないのでスキップ
            if num == self.board[cell] and random.randrange(0, 10000) != 0:
                continue
            # 評価が一番良い(= conflict が一番小さい) value を探す
            eval = self.evaluate(cell, num)
            min_value_conflictnum = (num, eval) \
                if min_value_conflictnum[1] > eval else min_value_conflictnum
        return min_value_conflictnum[0]

    def set(self, cell: Tuple[int, int], value: int) -> None:
        """cell に value をセットする
        """
        # このとき、影響のある cell たちを保存しておく
        self.current_effected_cells = self._get_conflict_cells(cell, value) - {cell}
        self.board[cell] = value


if __name__ == '__main__':
    board_0 = [
        [9, 8, 4, 0, 3, 1, 0, 7, 2],
        [6, 1, 0, 0, 0, 7, 0, 0, 0],
        [2, 5, 7, 0, 0, 9, 8, 0, 0],
        [3, 0, 0, 0, 6, 0, 0, 1, 0],
        [0, 0, 0, 3, 7, 0, 9, 2, 0],
        [0, 0, 9, 0, 0, 5, 0, 0, 0],
        [0, 3, 0, 0, 0, 6, 0, 0, 0],
        [0, 4, 5, 0, 1, 8, 0, 9, 6],
        [1, 9, 6, 7, 0, 0, 2, 8, 0]
    ]

    board_0 = [
        [8, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 6, 0, 0, 0, 0, 0],
        [0, 7, 0, 0, 9, 0, 2, 0, 0],
        [0, 5, 0, 0, 0, 7, 0, 0, 0],
        [0, 0, 0, 0, 4, 5, 7, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 3, 0],
        [0, 0, 1, 0, 0, 0, 0, 6, 8],
        [0, 0, 8, 5, 0, 0, 0, 1, 0],
        [0, 9, 0, 0, 0, 0, 4, 0, 0]
    ]

    board_0 = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    # board_0 = [
    #     [7, 4, 1, 9, 3, 5, 2, 6, 0],
    #     [5, 9, 8, 6, 7, 2, 3, 1, 4],
    #     [6, 3, 2, 1, 8, 4, 9, 0, 7],
    #     [8, 7, 4, 2, 6, 9, 5, 3, 1],
    #     [2, 1, 9, 4, 5, 3, 8, 7, 6],
    #     [3, 6, 5, 8, 1, 7, 4, 9, 2],
    #     [1, 8, 3, 5, 2, 6, 7, 4, 9],
    #     [9, 5, 6, 7, 4, 8, 1, 2, 3],
    #     [4, 2, 7, 3, 9, 1, 6, 0, 0],
    # ]

    solver = MinConflict(board_0)
    solver.print()
    solver.solve()
    # solver.print()
    print(f'debug_min_conflict_count: {solver.debug_min_conflict_count}')
