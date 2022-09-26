from collections import deque
from itertools import product
from backtracking_simple import BacktrackingSimple
from typing import Tuple, Iterator, Dict
import random


class BacktrackingIDP(BacktrackingSimple):
    def initialize_with_strategy(self) -> None:
        """imcomplete dynamic backtracking としての初期化
        """
        # 最大の試行回数
        self.max_steps = 5000
        # 現在の step 数
        self.current_step = 0
        # ここで変数の順番も決める。 static.
        self.ordered_cells = deque([(row, col) for row, col in product(range(0, 9), range(0, 9))])
        # 既に数字が埋まっている cell の集合を集めておく
        self.already_assigned_cells = {cell for cell in product(range(0, 9), range(0, 9)) if self.board[cell] != 0}
        # 初期の cell と value の組み合わせ
        self.cell_value_map = self.initialize_as_min_conflict()
        # cell の値を変えたときに影響のある cell の集合
        self.current_effected_cells = set()

    def initialize_as_min_conflict(self) -> Dict:
        """min_conflict 的な、 cell 毎に何の value を初期に割り当てるかを定める
        return は dict で、 {cell: value} というかんじ。
        """
        result_dict = {c: 0 for c in self.ordered_cells}
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
                        result_dict[cell] = value
                        break
                    else:
                        # conflict があるなら、これまで調べた中と比較して一番小さいやつだけ残しておく
                        min_conflict_value_eval = (value, eval) \
                            if min_conflict_value_eval[1] > eval else min_conflict_value_eval
                        _rest_domain.append(value)

                # 入れられなかったら、仕方が無いので、一番 conflict が小さかったところにいれる
                if result_dict[cell] == 0:
                    v, e = min_conflict_value_eval
                    result_dict[cell] = v
                    _rest_domain.remove(v)

                # domain を補充する
                domain += _rest_domain

        return result_dict

    def order_domain_values(self, cell: Tuple[int, int]) -> Iterator:
        """次に試す value を返す
        先頭に試す cell においては、 max_steps が許す限り繰り返す
        """
        if cell == (0, 0):
            for step in range(self.max_steps):
                self.current_step = step
                yield self.cell_value_map[cell]
        yield self.cell_value_map[cell]

    def is_consistent(self, cell: Tuple[int, int], value: int) -> bool:
        """consistency をみるが、今回に限ってはこれをあえて機能させない
        """
        return True

    def inference(self, cell: Tuple[int, int], value: int) -> bool:
        """look ahead をする
        ただし、 consistency を保つことはしない。
        """
        # leaf まで割り付けていないならそのままスルー
        if len(self.ordered_cells) != 0:
            return True

        # ここで max_step に至っているならば、処理終わり
        if self.current_step == self.max_steps - 1:
            return True

        # 変数を補充
        # self.ordered_cells = deque([(row, col) for row, col in product(range(0, 9), range(0, 9))])
        # ここで解であるならば 処理 おしまい
        if self.is_solution():
            return True

        # ここから、 min-conflict をやるpp
        # conflict を起こしている cell をランダムに選ぶ
        cell = self.choose_conflict_cell()
        # その cell の値として最も conflict が小さくなる value を選択する
        value = self.choose_min_conflict_value(cell)
        # 次、それを割り付ける
        self.set(cell, value)

        return False

    def choose_conflict_cell(self) -> Tuple[int, int]:
        """conflict を起こしている cell を一つ選ぶ
        """
        # もしも最近影響を及ぼした cell があるならそこから random に一つ選ぶ.
        self.current_effected_cells -= self.already_assigned_cells
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
        self.cell_value_map[cell] = value

    def evaluate(self, cell: Tuple[int, int], value: int) -> float:
        """評価
        """
        return len(self._get_conflict_cells(cell, value))


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

    solver = BacktrackingIDP(board_0)
    solver.print()
    solver.solve()
    solver.print()
    print(f'current_step: {solver.current_step}')
    print(f'debug_backtrack_count: {solver.debug_backtrack_count}')
