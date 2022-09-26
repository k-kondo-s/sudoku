from copy import deepcopy
from itertools import product
from typing import Iterator, Tuple

from backtracking_3 import BacktrackingAcMrv


class BacktrackingAcMrvLcv(BacktrackingAcMrv):
    def order_domain_values(self, cell: Tuple[int, int]) -> Iterator:
        """least constraint value に従って value を選ぶ
        """
        # その cell の近傍の cell を集める
        cells_row = [(cell[0], col) for col in range(0, 9)]
        cells_col = [(row, cell[1]) for row in range(0, 9)]
        cells_block = [(3 * (cell[0] // 3) + i, 3 * (cell[1] // 3) + j)
                       for i, j in product(range(0, 3), range(0, 3))]
        local_area = set(cells_row) | set(cells_col) | set(cells_block) - {cell}
        local_area &= set(self.ordered_cells)

        # その近傍の cell のすべての domain を見て、候補となる値をカウントしておく
        ranking_domain_values = {num: 0 for num in range(1, 10)}
        for c in local_area:
            for n in self.domains[c]:
                ranking_domain_values[n] += 1

        # それをもとに、今の cell に対応する domain との共通部分や差分に興味がある
        other_domains = {num for num, count in ranking_domain_values.items() if count > 0}

        # そもそも、他の domain には現れなくて自分の domain にしか無いものがあるならば、それを使う
        if len(self.domains[cell] - other_domains) != 0:
            domain = deepcopy(self.domains[cell])
            for c in domain:
                yield c

        # では、制約がない順(=他の cell の候補としてもよく上がっている順)に、 value を並べる
        top_domain_ranking = sorted(ranking_domain_values.items(), key=lambda v: v[1], reverse=True)
        domain = [v[0] for v in top_domain_ranking if v[0] in self.domains[cell] & other_domains]
        for c in domain:
            yield c


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

    solver = BacktrackingAcMrvLcv(board_0)
    solver.print()
    solver.solve()
    solver.print()
    print(f'debug_backtrack_count: {solver.debug_backtrack_count}')
