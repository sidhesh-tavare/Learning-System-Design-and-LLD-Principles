from dataclasses import dataclass
from enum import Enum,auto
from collections import deque
from abc import abstractmethod,ABC


class Mark(Enum):
    X ="X"
    O = "O"

@dataclass(frozen=True)
class Player:
    name : str 
    mark : Mark

class GameState(Enum):
    IN_PROGRESS = auto()
    DRAW = auto()
    WON = auto()

class InvalidMoveError(Exception):
    ''' Raised whenever the move played is Invalid '''
    ''' It may mean out f bounds or already occupied earlier'''

class Board:
    def __init__(self,size:int=3)->None:
        if size<3:
            raise ValueError("Board size must be minimum 3 ")
        self.size = size
        self._board : list[list[Mark|None]] = [[None]*self.size for _ in range(self.size)]
        self._moves = 0 

    @property
    def get(self,r:int,c:int):
        return self._board[r][c]
    
    def valid_move(self,r:int,c:int)->bool:
        if r>=self.size or c>=self.size or r<0 or c<0: 
            return InvalidMoveError(f"({r},{c}) is out of bound")
        if self._board[r][c] is not None:
            return InvalidMoveError(f"{{r},{c}} is already occupied by {self._board.get}")
        return True

    def place_mark(self, mark : Mark , r : int , c : int )->bool:
        if self.valid_move(r,c):
            self._board[r][c] = mark
            return True
        else:
            print("Invalid Move Try Again")
            return False 

    def is_filled(self)->bool:
        return self.is_filled == self.size*self.size
    
    def __str__(self)->str:
        return "\n".join(" | ".join(cell.value if cell else "." for cell in row) for row in self._board)

class Game:

    def __init__(self,game_name:str,players : list[Player]):
        self.game_name = game_name
        self.winner = None 
        self.players = deque(players)
        self.board = Board()
        self.moves = 0 

    def check_winner(self) -> Mark:
      
        # Check rows
        for r in range(3):
            if self.board[r][0] == self.board[r][1] == self.board[r][2] and self.board[r][0] != Mark.Empty:
                return self.board.board[r][0]

        # Check columns
        for c in range(3):
            if self.board[0][c] == self.board[1][c] == self.board[2][c] \
                    and self.board[0][c] != Mark.Empty:
                return self.board[0][c]

        # Check main diagonal
        curr = self.board[0][0]
        flag = False

        for r in range(1, 3):
            if self.board[r][r] != curr:
                flag = True
                break

        if not flag and curr != Mark.Empty:
            return curr

        # Check anti-diagonal
        curr = self.board[0][2]
        flag = False

        for r in range(1, 3):
            if self.board[r][2 - r] != curr:
                flag = True
                break

        if not flag and curr != Mark.Empty:
            return curr

        return Mark.Empty

    def play(self,r,c)->None:

        if self.winner ==Mark.Empty:
            curr_player = self.players.popleft()
            self.players.append(curr_player)
            mark = curr_player.mark

            if self.board.valid_move(r,c):
                self.board.place_mark(r,c,mark)
                print(f"{mark} placed at [r,c]")
                self.moves+=1
                winner = self.check_winner()
                if winner!=Mark.Empty:
                    print("Winner is {winner}")


            if self.moves == 9 : 
                self.endgame()

    def endgame()->None:
        print("Game Ended its a Draw")







    

    

    