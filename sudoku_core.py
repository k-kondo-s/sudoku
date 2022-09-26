from itertools import product
from typing import List, Tuple, Set


class Sudoku():
    def __init__(self, board: List[List]) -> None:
        """initialize. board をセットする
        """
        # CSP として初期化する
        self.initialize_as_csp(board)

    def initialize_as_csp(self, board: List[List]) -> None:
        """CSP として解くための初期化
        """
        # cell を tuple として board にアクセスできるようにしておく。
        self.board = {(row, col): board[row][col] for row, col in product(range(0, 9), range(0, 9))}

        # domain を初期化。すべての cell に入りうる値は 1 から 9
        self.domains = {(row, col): set(range(1, 10)) for row, col in product(range(0, 9), range(0, 9))}

    def is_solution(self) -> bool:
        """答えかどうか確認
        """
        # 行、列、ブロックと見ていって、足りない数がないかを確認する。
        one_to_nine_set = set(range(1, 10))
        for n in range(0, 9):
            row = {self.board[(n, j)] for j in range(0, 9)}
            if row != one_to_nine_set:
                return False
            col = {self.board[(j, n)] for j in range(0, 9)}
            if col != one_to_nine_set:
                return False
            block = {self.board[(3 * (n % 3) + i, 3 * (i // 3) + j)] for i, j in product(range(0, 3), range(0, 3))}
            if block != one_to_nine_set:
                return False
        return True

    def _get_conflict_cells(self, cell: Tuple[int, int], value: int) -> Set:
        """与えられた cell と value の組み合わせに矛盾する cell の集合を返す
        """
        # 与えられた cell の集まりの中に、与えられた value と同じ数字が既にあるならば
        # その cell の集合を返す。
        def _find_conflict(arr):
            return {c for c in arr if self.board[c] == value}

        # 行、列、ブロック毎に矛盾する cell を調査して、その集合を返す。
        cells_row = [(cell[0], col) for col in range(0, 9)]
        cells_col = [(row, cell[1]) for row in range(0, 9)]
        cells_block = [(3 * (cell[0] // 3) + i, 3 * (cell[1] // 3) + j) for i, j in product(range(0, 3), range(0, 3))]
        conflict_cell_set = _find_conflict(cells_row) | _find_conflict(cells_col) | _find_conflict(cells_block) - {cell}
        return conflict_cell_set

    def print(self) -> None:
        """board を print する. この処理は backtrack とは関係ない。
        """
        # dict から list in list 形式に変換する。
        board_list = [[self.board[(row, col)] for col in range(0, 9)] for row in range(0, 9)]

        # 先頭に空行
        print()

        # 一行ずつ print していく。
        for row_index, row in enumerate(board_list):

            # print する 1 行の文字列を作って print する
            print_row = ''
            for cell_index, cell in enumerate(row):
                # 0 の値は空白にする
                value = str(cell) if cell != 0 else ' '
                # 3 マスで区切りが入る
                value = value + '|' if cell_index in [2, 5] else value + ''
                print_row += value
            print(print_row)

            # 3 行目、また 6 行目であれば区切り線をいれる
            if row_index in [2, 5]:
                sep_list = ['-' for i in range(11)]
                sep_list[3], sep_list[7] = '+', '+'
                print(''.join(sep_list))
