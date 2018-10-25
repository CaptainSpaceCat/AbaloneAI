import math, random
from collections import defaultdict

class AbaloneGame():

    def __init__(self, board, maxPower, numToWin):
        self.board = board
        #self.width = (len(board) + 1) / 2
        self.blackCount = 0
        self.whiteCount = 0
        self.maxPower = maxPower
        self.numToWin = numToWin
        for row in self.board:
            for item in row:
                if item == 1:
                    self.whiteCount += 1
                elif item == -1:
                    self.blackCount += 1
        self.dirGrid = [
        (-1, 0),
        (-1, 1),
        (0, 1),
        (1, 0),
        (1, -1),
        (0, -1)
        ]

    def printRef(self):
        print(" 0 1")
        print("5 . 2")
        print(" 4 3")

    def printSelf(self):
        r = 0
        offset = (len(board) - 1)/2
        noneChar = " "
        for row in self.board:
            line = (" " * r)
            n = 0
            for item in row:
                if item == None:
                    line += noneChar + " "
                    n += 1
                elif item == 1:
                    line += "@ "
                elif item == -1:
                    line += "O "
                elif item == 0:
                    line += ". "
            if n == 0:
                noneChar = "\\"
            print(str(r) + "|" + line[offset:])
            r += 1

        print((" " * (r - offset + 2)) + ("\ " * len(board)))
        line = ""
        for i in range(len(board)):
            line += str(i) + " "
        print((" " * (r - offset + 3)) + line)
        self.printRef()

    def inBounds(self, row, col):
        return row >= 0 and col >= 0 and row < len(self.board) and col < len(self.board) and self.board[row][col] != None

    #assuming we're moving a white ball from row, col in direction dir
    #return the number of black balls we'd need to push to do so
    def getOpposition(self, row, col, dir):
        total = 0
        while True:
            currentRow = row + self.dirGrid[dir][0] * (total + 1)
            currentCol = col + self.dirGrid[dir][1] * (total + 1)
            if self.inBounds(currentRow, currentCol):
                if self.board[currentRow][currentCol] == 1:
                    #if we have a white ball in front of us, we cannot move forward
                    #set opposition to a ridiculously large number
                    return 1000000
                elif self.board[currentRow][currentCol] == 0:
                    return total
            else:
                return total
            total += 1

    #assuming we're moving a white ball from row, col in direction dir
    #return the number of white balls we have behind us to push with
    def getPower(self, row, col, dir):
        total = 1 #assuming this ball is white, we can just start at 1
        while total < self.maxPower:
            currentRow = row - self.dirGrid[dir][0] * total
            currentCol = col - self.dirGrid[dir][1] * total
            if not self.inBounds(currentRow, currentCol) or self.board[currentRow][currentCol] != 1:
                break
            total += 1
        return total

    def checkBroadMove(self, move):
        initialRow = move[0][0]
        initialCol = move[0][1]
        dir = move[1]
        ballDir = move[2]
        numBalls = move[3]
        for ball in range(numBalls):
            newRow = initialRow + self.dirGrid[ballDir][0] * ball + self.dirGrid[dir][0]
            newCol = initialCol + self.dirGrid[ballDir][1] * ball + self.dirGrid[dir][1]
            if not self.inBounds(newRow, newCol) or self.board[newRow][newCol] != 0:
                return False

        return True

    def getActions(self):
        actions = []
        #action format: ((row, col), direction, ball direction, number of balls)

        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if self.board[row][col] == 1:
                    #we found a white ball, check to see what we can do with it

                    #get pushing actions
                    for dir in range(6):
                        if self.inBounds(row + self.dirGrid[dir][0], col + self.dirGrid[dir][1]):
                            opposition = self.getOpposition(row, col, dir)
                            power = self.getPower(row, col, dir)
                            for i in range(1, power+1):
                                if i > opposition:
                                    actions.append(((row, col), dir, i))

        return actions


    def makeMove(self, action):
        row = action[0][0]
        col = action[0][1]
        dir = action[1]
        power = action[2]
        team = self.board[row][col]

        if ballDir == (dir + 3)%6:
            newRow = row - self.dirGrid[dir][0] * (power - 1)
            newCol = col - self.dirGrid[dir][1] * (power - 1)
            self.board[newRow][newCol] = 0
            newRow = row + self.dirGrid[dir][0]
            newCol = col + self.dirGrid[dir][1]
            other = self.board[newRow][newCol]
            self.board[newRow][newCol] = team
            if other != 0:
                newRow += self.dirGrid[dir][0]
                newCol += self.dirGrid[dir][1]
                while self.inBounds(newRow, newCol) and self.board[newRow][newCol] == other:
                    newRow += self.dirGrid[dir][0]
                    newCol += self.dirGrid[dir][1]
                if self.inBounds(newRow, newCol):
                    self.board[newRow][newCol] = other
                else:
                    if other == 1:
                        self.whiteCount -= 1;
                    elif other == -1:
                        self.blackCount -= 1;


def getGameBoard(fileName):
    f = open(fileName, "r")
    fl = f.readlines()
    f.close()
    board = []

    row = 0
    for line in fl:
        col = 0
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

            col += 1
        row += 1

    return board


board = getGameBoard("small.txt")
game = AbaloneGame(board, 3, 6)
game.printSelf()
actions = game.getActions()
print(actions)
#game.printSelf()
