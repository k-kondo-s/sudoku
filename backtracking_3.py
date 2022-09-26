from collections import deque
from typing import Tuple, Union

from backtracking_2 import BacktrackingAc


class BacktrackingAcMrv(BacktrackingAc):
    def select_unassigned_variable(self) -> Union[Tuple[int, int], None]:
        """MRV に従って次のものを選ぶ
        """
        # 今の時点で domain の数が少ないものから選んでいく
        if len(self.ordered_cells) != 0:
            cell_domain_wo_assiendcell = [(cell, domain)
                                          for cell, domain in self.domains.items() if self.board[cell] == 0]
            sorted(cell_domain_wo_assiendcell, key=lambda v: len(v[1]))
            self.ordered_cells = deque([i[0] for i in sorted(cell_domain_wo_assiendcell, key=lambda v: len(v[1]))])
            return self.ordered_cells.popleft()
        return None


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

    # board_0 = [
    #     [8, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 3, 6, 0, 0, 0, 0, 0],
    #     [0, 7, 0, 0, 9, 0, 2, 0, 0],
    #     [0, 5, 0, 0, 0, 7, 0, 0, 0],
    #     [0, 0, 0, 0, 4, 5, 7, 0, 0],
    #     [0, 0, 0, 1, 0, 0, 0, 3, 0],
    #     [0, 0, 1, 0, 0, 0, 0, 6, 8],
    #     [0, 0, 8, 5, 0, 0, 0, 1, 0],
    #     [0, 9, 0, 0, 0, 0, 4, 0, 0]
    # ]

    # board_0 = [
    #     [0, 3, 0, 1, 0, 5, 0, 9, 0],
    #     [0, 0, 7, 0, 0, 0, 8, 0, 0],
    #     [0, 0, 0, 0, 6, 0, 0, 0, 0],
    #     [0, 1, 0, 2, 0, 3, 0, 5, 0],
    #     [0, 0, 0, 0, 0, 4, 0, 0, 0],
    #     [5, 0, 0, 0, 0, 0, 0, 0, 9],
    #     [0, 6, 0, 0, 9, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 4, 0, 0, 2, 0],
    #     [0, 0, 3, 6, 0, 2, 0, 0, 7],
    # ]

    solver = BacktrackingAcMrv(board_0)
    solver.print()
    solver.solve()
    solver.print()
    print(f'debug_backtrack_count: {solver.debug_backtrack_count}')
