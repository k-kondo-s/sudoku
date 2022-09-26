'''プロトタイプ
テキトー実装の思い出として残す
'''
# %%
from copy import deepcopy
from time import time
from typing import List
from collections import deque
from itertools import product

FOOLISH = 'FOOLISH'
SORT_BEFOREHAND = 'SORT_BEFOREHAND'
DYNAMIC = 'DYNAMIC'


class SudokuSolver():
    def __init__(self) -> None:
        self.backtrack_count = 0
        self.strategy = FOOLISH  # FOOLISH, SORT_BEFOREHAND, DYNAMIC
        self.cells_to_be_checked: deque = None
        self.debug_print = False

    def _remove_candidates_per_row(self, candidate_nums, board):
        """行を見て既にある数字を候補から削除する
        """
        for row in range(0, 9):
            filled_num_wo_zero = set(board[row]) - {0}
            for col in range(0, 9):
                candidate_nums[(row, col)] -= filled_num_wo_zero
        return candidate_nums

    def _remove_candidates_per_colmun(self, candidate_nums, board):
        """列を見て、すでにある数字を候補から削除する
        """
        for col in range(0, 9):
            filled_num_wo_zero = set([board[_row][col] for _row in range(0, 9)]) - {0}
            for row in range(0, 9):
                candidate_nums[(row, col)] -= filled_num_wo_zero
        return candidate_nums

    def _remove_candidates_per_block(self, candidate_nums, board):
        """ブロックを見て、すでにある数字を候補から削除する
        """
        # ブロックごとにに対応する cell のリストを準備する
        _cells_per_block = {(_block_row, _block_col): set()
                            for (_block_row, _block_col) in product(range(0, 3), range(0, 3))}
        for row, col in product(range(0, 9), range(0, 9)):
            _block_index = (row // 3, col // 3)
            _cells_per_block[_block_index] = _cells_per_block[_block_index] | {board[row][col]} - {0}
        for row, col in product(range(0, 9), range(0, 9)):
            candidate_nums[(row, col)] -= _cells_per_block[(row // 3, col // 3)]

        return candidate_nums

    def generate_candidate_nums(self, board):
        """候補となる数字の集合を作る
        """
        # あらかじめすべての cell の候補は 1,2,3,...,9 であるとしておく
        candidate_nums = {(row, col): set([i for i in range(1, 10)])
                          for (row, col) in product(range(0, 9), range(0, 9))}

        # board の数字から、予め候補にならない数字を取り除く
        candidate_nums = self._remove_candidates_per_row(candidate_nums, board)
        candidate_nums = self._remove_candidates_per_colmun(candidate_nums, board)
        candidate_nums = self._remove_candidates_per_block(candidate_nums, board)

        return candidate_nums

    def initialize_cells_to_be_checked(self, candidate_nums):
        """候補の数の集合に基づいて、確認していく cell の順番を決める
        """
        # 候補が少ないところから.
        if self.strategy in [SORT_BEFOREHAND, DYNAMIC]:
            self.cells_to_be_checked = deque([k[0] for k in sorted(candidate_nums.items(), key=lambda t: len(t[1]))])
        # 一番バカな方法から。
        else:  # FOOLISH
            self.cells_to_be_checked = deque(candidate_nums.keys())
        return self.cells_to_be_checked

    def is_valid(self, board, candidate_nums, cell):
        """矛盾がないかをしらべる
        """
        # 矛盾がないの定義: ボードは埋まっていないのに、候補となる数が存在しないこと
        row, col = cell
        return not (board[row][col] == 0 and not candidate_nums[cell])

    def update(self, board, candidate_nums, cell, num):
        updated_cells = set()
        row, col = cell
        assert board[row][col] == 0, f'not empty, {(row, col, board[row][col])}'

        # board を更新
        board[row][col] = num

        # これで影響のある candidate を取り除く。まずは行から
        for c in range(0, 9):
            if num not in candidate_nums[(row, c)]:
                continue
            candidate_nums[(row, c)] -= {num}
            updated_cells.add((row, c))
        # 次に列。
        for r in range(0, 9):
            if num not in candidate_nums[(r, col)]:
                continue
            candidate_nums[(r, col)] -= {num}
            updated_cells.add((r, col))
        # 最後にブロック
        for r, c in product(range(0, 9), range(0, 9)):
            if (r // 3, c // 3) != (row // 3, col // 3):
                continue
            if num not in candidate_nums[(r, c)]:
                continue
            candidate_nums[(r, c)] -= {num}
            updated_cells.add((r, c))

        return candidate_nums, board, updated_cells

    def revert(self, board, candidate_nums, cell, num, updated_cells):
        row, col = cell

        # board を戻す
        board[row][col] = 0

        # update した cell だけもとに戻す
        for ucell in updated_cells:
            candidate_nums[ucell].add(num)

        return candidate_nums, board

    def popleft(self, candidate_nums):
        """strategy に応じて次に探索する cell を取得する
        """
        # 動的であれば、現在の状態の中でも一番候補が少ないところを選ぶ
        if self.strategy == DYNAMIC:
            rest_checked_cells = {cell: candidates for cell,
                                  candidates in candidate_nums.items() if cell in self.cells_to_be_checked}
            self.cells_to_be_checked = deque([k[0] for k in sorted(
                rest_checked_cells.items(), key=lambda t: len(t[1]))])

        return self.cells_to_be_checked.popleft()

    def appendleft(self, cell):
        """cell を元に戻す
        """
        return self.cells_to_be_checked.appendleft(cell)

    def backtrack(self, board, candidate_nums, history: List):
        self.backtrack_count += 1
        if self.debug_print is True and self.backtrack_count % 100 == 0:
            print('count', self.backtrack_count)

        # 次がないならそれで終わり
        if not self.cells_to_be_checked:
            return True, board

        # 次に探索する cell を取り出す。
        cell = self.popleft(candidate_nums)
        row, col = cell

        # 矛盾していたら False を返す
        if not self.is_valid(board, candidate_nums, cell):
            self.appendleft(cell)
            return False, board

        # もし既に数字が埋まっているなら次へ
        if board[row][col] != 0:
            return self.backtrack(board, candidate_nums, history)

        # 以下は数字が埋まっていない場合、埋めてみる。
        to_be_checked = deepcopy(candidate_nums[cell])
        for num in to_be_checked:
            # この数字を入れて、全ての candidate を更新する
            candidate_nums, board, updated_cells = self.update(board, candidate_nums, cell, num)

            # debug
            if self.debug_print is True and self.backtrack_count % 100 == 0:
                self.show(board)
                print()

            # その前提で次を試す
            result_bool, board = self.backtrack(board, candidate_nums, history)
            # もしもここで True が返ってくるならば、それはすべて成功した、ということだから、もう何もせず上に返す
            if result_bool:
                return True, board
            # だめだったら、 revert する
            candidate_nums, board = self.revert(board, candidate_nums, cell, num, updated_cells)

            # debug
            if self.debug_print is True and self.backtrack_count % 100 == 0:
                self.show(board)
                print()

        # ここまで来るとその前がだめだった、ということだから、だめだと返す
        self.appendleft(cell)
        return False, board

    def solve(self, board) -> List[List]:
        # それぞれの cell の候補となる数字を格納する dict を作る。
        # これはずっと更新されていく。終了判定も必要になるであろう。そういう使われ方も OK
        # TODO: board は cell を index とした dict にしたほうがよさそうだな。 I/F が若干複雑。
        # TODO: popleft しているところは全部 next という関数にしよう。ということは内部に deque を持つことになるから
        #       class にする必要があるであろう。
        candidate_nums = self.generate_candidate_nums(board)

        # 調べる順番を定義する
        self.initialize_cells_to_be_checked(candidate_nums)

        # backtrack で埋めていく
        history = []
        _, result_board = self.backtrack(board, candidate_nums, history)

        return result_board

    def show(self, board):
        """ボードを見やすいように表示する

        53 | 7 |
        6  |195|
         98|   | 6
        ---+---+---
        8  | 6 |  3
        4  |8 3|  1
        7  | 2 |  6
        ---+---+---
         6 |   |28
           |419|  5
           | 8 | 79

        Args:
            board (List[List]): ボード
        """
        for row_index, row in enumerate(board):
            # print する 1 行の文字列
            print_row = ''
            for cell_index, cell in enumerate(row):
                # 0 の値は空白にする
                value = str(cell) if cell != 0 else ' '
                # 3 マスで区切りが入る
                value = value + '|' if cell_index in [2, 5] else value + ''
                print_row += value
            print(print_row)
            if row_index in [2, 5]:
                # 3 行目、また 6 行目であれば区切り線をいれる
                sep_list = ['-' for i in range(11)]
                sep_list[3], sep_list[7] = '+', '+'
                print(''.join(sep_list))


# %%
# 手で解いたらだいたい 10 分のやつ
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

# Wikipedia の例題: https://en.wikipedia.org/wiki/Backtracking
board_1 = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

# 世界一難しい: https://abcnews.go.com/blogs/headlines/2012/06/can-you-solve-the-hardest-ever-sudoku
board_2 = [
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

for board in [board_0, board_1, board_2]:
    original_board = deepcopy(board)
    for strategy in [FOOLISH, SORT_BEFOREHAND, DYNAMIC]:
        board = deepcopy(original_board)
        print('# strategy', strategy)
        solver = SudokuSolver()
        print('# before')
        solver.show(board)
        print()
        solver.strategy = strategy
        _start = time()
        print('# after')
        result_board = solver.solve(board)
        _end = time()
        solver.show(result_board)
        print('# summary')
        print('result_count', solver.backtrack_count, 'duration', _end - _start)
        print()

# %%
board_4 = [
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

strategy = FOOLISH
print('# strategy', strategy)
solver = SudokuSolver()
print('# before')
solver.show(board_4)
print()
solver.strategy = strategy
_start = time()
print('# after')
result_board = solver.solve(board_4)
_end = time()
solver.show(result_board)
print('# summary')
print('result_count', solver.backtrack_count, 'duration', _end - _start)
print()

# %%
