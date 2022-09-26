from collections import deque
from itertools import product
from typing import Tuple

from backtracking_simple import BacktrackingSimple


class BacktrackingAc(BacktrackingSimple):
    def keep_arc_consistency(self, cell, value):
        """arc-consistency を保つ
        与えられた cell に value を割り付けることで影響のある他の cell との
        arc-consistency を保つよう、 domain から value を取り除く。
        """
        # 行、列、ブロック、それぞれの cell から value を取り除く
        cells_row = {(cell[0], col) for col in range(0, 9)}
        cells_col = {(row, cell[1]) for row in range(0, 9)}
        cells_block = {(3 * (cell[0] // 3) + i, 3 * (cell[1] // 3) + j) for i, j in product(range(0, 3), range(0, 3))}
        cells = cells_row | cells_col | cells_block - {cell}
        for c in cells:
            self.domains[c] -= {value}
            # もしもこの時点で、まだ未割り当てな cell にも関わらず、 domain から候補が
            # 何もなくなった場合は、矛盾しているので、この時点で False を返す。
            if self.board[c] == 0 and len(self.domains[c]) == 0:
                return False
        # ここまでくれば arc-consistency に必要な処理は無事終了。 True を返そう。
        return True

    def initialize_with_strategy(self) -> None:
        """戦略に従った初期化
        今回は前処理で arc-consistency を保つようにして、
        さらに前もって制約の数が多い cell、つまり domain の数が少ない cell から
        順に探索できるようにしておく
        """
        # 既に数字が入っている cell をもとに、arc-consistency を保つ
        for cell in [c for c in self.board.keys() if self.board[c] != 0]:
            self.keep_arc_consistency(cell, self.board[cell])

        # 制約が多い cell から早く探索するようにする。
        # まずすでに割ついているもの(domainの数が0のやつ)は予め取り除く
        cell_domain_wo_assiendcell = [(cell, domain) for cell, domain in self.domains.items() if self.board[cell] == 0]
        # 並び替える
        sorted(cell_domain_wo_assiendcell, key=lambda v: len(v[1]))
        self.ordered_cells = deque([i[0] for i in sorted(cell_domain_wo_assiendcell, key=lambda v: len(v[1]))])

    def inference(self, cell: Tuple[int, int], value: int) -> bool:
        """look ahead
        """
        return self.keep_arc_consistency(cell, value)

    def revert_inference(self, cell: Tuple[int, int], value: int) -> None:
        """inference して取り除いた value をもとに戻す。
        ただし、あくまで consistency は保つこと。
        """
        # 行、列、ブロック、それぞれの cell の domain に value を元にもどす。
        # ただし、 consistency を保つために、その domain に value を入れて矛盾がないかを
        # この時点で調べておく。
        cells_row = {(cell[0], col) for col in range(0, 9)}
        cells_col = {(row, cell[1]) for row in range(0, 9)}
        cells_block = {(3 * (cell[0] // 3) + i, 3 * (cell[1] // 3) + j) for i, j in product(range(0, 3), range(0, 3))}
        cells = cells_row | cells_col | cells_block - {cell}
        for c in cells:
            if len(self._get_conflict_cells(cell, value)) == 0:
                self.domains[c].add(value)


if __name__ == '__main__':

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

    solver = BacktrackingAc(board_0)
    solver.print()
    solver.solve()
    solver.print()
    print(f'debug_backtrack_count: {solver.debug_backtrack_count}')
