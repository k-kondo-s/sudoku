from minconflict import MinConflict
from typing import Tuple, List
from itertools import product
import math


class MinConflict2(MinConflict):
    def __init__(self, board: List[List]) -> None:
        super().__init__(board)
        # 戦略をどちらかで決める。一様か局所か
        self.debug_high_entropy_is_good = True

    def evaluate(self, cell: Tuple[int, int], value: int) -> float:
        """評価。
        以下のように定義する local entropy とする:
            該当の cell が所属する block の value の出現率に伴う entropy.

        面白いのが、例えば「entropy が最小になるほど良い評価」とすれば、それは
        局所領域に同じ数字が集まる様子を観察することができる。
        また逆に「entropy が最大になるほどよい評価」とすれば、それは
        局所領域が一様になるような様子、つまり、普通の数独の解を作ろうと働く。
        """
        # 局所領域の定義
        cells_row, cells_col, cells_block = set(), set(), set()
        cells_row = [(cell[0], col) for col in range(0, 9)]
        cells_col = [(row, cell[1]) for row in range(0, 9)]
        cells_block = [(3 * (cell[0] // 3) + i, 3 * (cell[1] // 3) + j) for i, j in product(range(0, 3), range(0, 3))]
        local_area = list(set(cells_row) | set(cells_col) | set(cells_block))
        assert len(local_area) != 0, 'local_area must not be empty.'

        # 与えられた cell に value が入った場合の、局所における value たち
        local_values = []
        for c in local_area:
            if c == cell:
                local_values.append(value)
            else:
                local_values.append(self.board[c])

        # 局所における 1 から 9 までの出現率
        probabilities = [len([v for v in local_values if v == num]) / len(local_area) for num in range(1, 10)]

        # entropy
        def partial_entropy(prob: float):
            """ -p log(p) なんだけど、特に p == 0 のときは 0 を返す
            """
            if prob == 0.0:
                return 0.0
            return - prob * math.log(prob)
        entropy = sum([partial_entropy(p) for p in probabilities])

        # 返す値が低いほど、良い評価。
        # こういうふうにするなら、一様型
        if self.debug_high_entropy_is_good:
            return math.log(len(local_area)) - entropy
        # 普通に entoropy を返すなら、低いほうがいいので、集中型
        return entropy

    def set(self, cell: Tuple[int, int], value: int) -> None:
        """cell に value をセットする
        ここは、本質的には choose_conflict_cell で選ぶ cell を何にするか、ということが関わる。

        つまり evaluate に応じて heuristics が定まる場所

        例えば entropy が小さいほうを良い評価にする、ということであれば、影響のある cell を、
        一方 entropy が大きい方を良い評価にする、ということであれば、 conflict を起こしている cell を記録しておく。
        """
        # board に value をいれる
        self.board[cell] = value

        # このとき、影響のある cell たちを保存しておく
        # ここは戦略でかわる
        if self.debug_high_entropy_is_good:
            # 以下は、 entropy 最大が良いスケジュールのとき
            self.current_effected_cells = self._get_conflict_cells(cell, value) - {cell}
        else:
            # 以下は、 entropy 最小が良いスケジュールのとき
            cells_row = [(cell[0], col) for col in range(0, 9)]
            cells_col = [(row, cell[1]) for row in range(0, 9)]
            cells_block = [(3 * (cell[0] // 3) + i, 3 * (cell[1] // 3) + j)
                           for i, j in product(range(0, 3), range(0, 3))]
            local_area = set(cells_row) | set(cells_col) | set(cells_block)
            self.current_effected_cells = local_area - {cell}


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

    solver = MinConflict2(board_0)
    solver.print()
    solver.solve()
    # solver.print()
    print(f'debug_min_conflict_count: {solver.debug_min_conflict_count}')
