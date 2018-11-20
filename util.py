import game

#reads in an abalone game board and associated info into a game object
#returns a tuple of information about the game
def getGameInfo(fileName):
    f = open(fileName, "r")
    fl = f.readlines()
    f.close()
    board = []

    boardWidth = len(fl[0])

    for row in range(boardWidth - 1):
        line = fl[row]
        board.append([])
        for c in line:
            if c == "_":
                board[row].append(None)
            elif c == "B":
                board[row].append(-1)
            elif c == "W":
                board[row].append(1)
            elif not c == "\n":
                board[row].append(0)

    maxPower = int(fl[boardWidth-1])
    numToWin = int(fl[boardWidth])

    return (game.Gamestate(board, numToWin, numToWin, -1), maxPower)

def getPlayerAction():
    nums = [int(n) for n in raw_input("Black >").split()]
    if len(nums) == 0:
        return None
    return ((nums[0], nums[1]), nums[2], nums[3], nums[4])
