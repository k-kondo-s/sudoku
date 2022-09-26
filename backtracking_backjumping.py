'''2022/09/24 実装失敗
'''
from collections import deque
from itertools import product
from backtracking_3 import BacktrackingAc
from typing import Tuple, Union, List


class Backjumping(BacktrackingAc):
    """backjumping の実装 -> 失敗
    backjumping は本当に構成的なのか？この理屈では、たしかに解に
    必ずたどり着ける、というわけではない。解のある branch を削ろうとしている可能性がある。
    """

    def __init__(self, board: List[List]) -> None:
        """initialize
        backjumping をするために、今まで探索した cell を保存する history,
        また backjumping で戻っている途中であることを示す変数も準備しておく
        """
        super().__init__(board)
        # 探索した cell を順番に保存する
        self.history = deque()
        # backjumping 中かどうか
        self.is_backjumping_going = False
        # 最新の conflict している cell を保存する。
        self.current_conflict_cell_set = set()
        # backtracking 中の conflicts set を cache するための dict
        self.cache_conf_cells = {cell: set() for cell in product(range(0, 10), range(0, 10))}

    def select_unassigned_variable(self) -> Union[Tuple[int, int], None]:
        """次に探索する cell を選択する
        このとき、 history に選択した cell を保存する。
        backjumping 中なら素直に leftpop する。
        """
        # if self.is_backjumping_going:
        if True:
            cell = self.ordered_cells.popleft()
        else:
            cell = super().select_unassigned_variable()
        self.history.append(cell)
        return cell

    def restore_unassigned_variable(self, cell: Tuple[int, int]) -> None:
        """cell を未割り当て状態に戻す
        このとき、 history の中からその cell を削除する。
        さらに、
        """
        # backjumping 中でなければ、今から新しく backjumping 始めるか決める。
        if not self.is_backjumping_going:
            # これまでに探索した cell の中に conflict しているものがあるかを残す
            self.current_conflict_cell_set = set(self.history) & self.cache_conf_cells[cell]
            # この時点で conflict set があるなら、backjumping を開始
            if len(self.current_conflict_cell_set) != 0:
                self.is_backjumping_going = True
        # backjumping したけど結局だめなら、 backjumping おわり
        if self.is_backjumping_going and cell in self.current_conflict_cell_set:
            self.is_backjumping_going = False
            self.current_conflict_cell_set = set()
        # cache を reset
        self.cache_conf_cells[cell] = set()
        # history から除く
        self.history.pop()
        # cell を未割り当てに戻す
        self.ordered_cells.appendleft(cell)

    def is_consistent(self, cell: Tuple[int, int], value: int) -> bool:
        """与えられた cell と value の組み合わせに矛盾がないかを調べる
        矛盾がなければ True, そうでなければ False.

        backjumping 中ならば、まず False にする。
        """
        # backjumping 中でかつ、自身がその戻りたい cell でない場合無条件で False 返す
        if self.is_backjumping_going and cell not in self.current_conflict_cell_set:
            assert self.is_backjumping_going and len(self.current_conflict_cell_set) != 0
            return False

        # ここまで来るということは、 backjumping 中ではないか、戻るべきところに戻ってきた、ということ
        # ということで、 backjumping の記録を消去する
        self.is_backjumping_going = False
        self.current_conflict_cell_set = set()

        # 矛盾がなければこの時点で True
        conflicts_set = self._get_conflict_cells(cell, value)
        if len(conflicts_set) == 0:
            return True

        # 矛盾があるなら、それを cache に入れて False を返す
        self.cache_conf_cells[cell] |= conflicts_set
        return False


if __name__ == '__main__':
    # board_0 = [
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    # ]

    # board_0 = [
    #     [9, 8, 4, 0, 3, 1, 0, 7, 2],
    #     [6, 1, 0, 0, 0, 7, 0, 0, 0],
    #     [2, 5, 7, 0, 0, 9, 8, 0, 0],
    #     [3, 0, 0, 0, 6, 0, 0, 1, 0],
    #     [0, 0, 0, 3, 7, 0, 9, 2, 0],
    #     [0, 0, 9, 0, 0, 5, 0, 0, 0],
    #     [0, 3, 0, 0, 0, 6, 0, 0, 0],
    #     [0, 4, 5, 0, 1, 8, 0, 9, 6],
    #     [1, 9, 6, 7, 0, 0, 2, 8, 0]
    # ]

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

    solver = Backjumping(board_0)
    solver.print()
    solver.solve()
    solver.print()
    print(f'debug_backtrack_count: {solver.debug_backtrack_count}')
