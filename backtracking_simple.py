from collections import deque
from copy import deepcopy
from itertools import product
from typing import Iterator, List, Tuple, Union

from sudoku_core import Sudoku


class BacktrackingSimple(Sudoku):
    def __init__(self, board: List[List]) -> None:
        """initialize. board をセットする
        """
        super().__init__(board)

        # 戦略毎に必要なものを初期化する
        self.initialize_with_strategy()

        # debug: 何回 backtrack に入ったか
        self.debug_backtrack_count = 0

    def solve(self) -> None:
        """backtrack で数独を解く
        """
        is_solved: bool = self.backtrack()
        # self.print()
        # assert is_solved, f'not solved. debug_backtrack_count: {self.debug_backtrack_count}'
        # assert self.is_solution(), 'not solution'

    def backtrack(self) -> bool:
        """backtrack の本丸の実装
        探索が終わったなら True, そうでなければ False を返す。
        """
        self.debug_backtrack_count += 1

        # 次に探索する cell(variable) を選択する
        cell = self.select_unassigned_variable()

        # もしも次に探索すべきものがないならば、その時点で処理終わり。
        if cell is None:
            return True

        # その cell に入りうる value 毎に考える。
        for value in self.order_domain_values(cell):

            # 選んだ value を cell に入れることに矛盾がなければ、それを採用する
            if self.is_consistent(cell, value):

                # 実際に、その値を入れる
                self.put(cell, value)

                # "looking-ahead" を行う
                inference_result = self.inference(cell, value)

                # "looking-ahead" が成功したならば、次に進む。
                if inference_result:
                    result = self.backtrack()

                    # backtrack の結果が成功であれば、それを上に返す
                    if result:
                        return result

            # ここまで来たということは、その cell と value の組み合わせが不合理ということ
            # だから、すべての処理を revert する。
            self.remove(cell, value)
            self.revert_inference(cell, value)

        # ここまで来たということは、もうこの変数では手立てがないので、この変数に assign することを諦めて
        # 親に考え直してもらう。
        self.restore_unassigned_variable(cell)
        return False

    def initialize_with_strategy(self) -> None:
        """戦略毎に必要な初期化を行う
        ここで、self.ordered_cells を作らないと行けない
        """
        # 既に数字が cell を取り除いておく。
        variables = [cell for cell in self.board.keys() if self.board[cell] == 0]

        # default で、 (0, 0), (0, 1), ..., (8, 7), (8, 8) という順に並べておく
        self.ordered_cells = deque(sorted(variables))

    def select_unassigned_variable(self) -> Union[Tuple[int, int], None]:
        """次に探索する variable を選ぶ
        もうそのような variable が残っていないなら None を返す
        """
        # default では、順番に並べられたものを左から pop していく。
        if len(self.ordered_cells) != 0:
            return self.ordered_cells.popleft()
        return None

    def order_domain_values(self, cell: Tuple[int, int]) -> Iterator:
        """cell 毎に決まる domain のリストを返す
        """
        # default では、数字の小さい順に試していく
        # なお、この domain の要素は動的に変わっていくので、
        # ここで deepcopy をしておく
        domain = deepcopy(self.domains[cell])
        for c in domain:
            yield c

    def is_consistent(self, cell: Tuple[int, int], value: int) -> bool:
        """与えられた cell と value の組み合わせに矛盾がないかを調べる
        矛盾がなければ True, そうでなければ False.
        """
        return len(self._get_conflict_cells(cell, value)) == 0

    def put(self, cell: Tuple[int, int], value: int) -> None:
        """与えられた cell に value を配置する
        """
        self.board[cell] = value

    def inference(self, cell: Tuple[int, int], value: int) -> bool:
        """inference する
        inference というのは、 CSP 全体の (k-)consistency を保つこと。
        consistency 保てるならば True, そうでなければ False を返す。
        """
        return True

    def remove(self, cell: Tuple[int, int], value: int) -> None:
        """指定された cell から value を取り除く
        """
        self.board[cell] = 0

    def revert_inference(self, cell: Tuple[int, int], value: int) -> None:
        """inference した結果を元に戻す
        """
        pass

    def restore_unassigned_variable(self, cell: Tuple[int, int]) -> None:
        """cell を未割り当て状態に戻す
        """
        self.ordered_cells.appendleft(cell)


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

    solver = BacktrackingSimple(board_0)
    solver.print()
    solver.solve()
    solver.print()
    print(f'debug_backtrack_count: {solver.debug_backtrack_count}')
