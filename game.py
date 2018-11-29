import math, random
from collections import defaultdict

BALL_REMOVED_REWARD = 20
GAME_WON_REWARD = 100

class Gamestate():

    def __init__(self, board, numWhite, numBlack, turn):
        self.board = board
        self.whiteRemaining = numWhite
        self.blackRemaining = numBlack
        self.turn = turn
        self.score = 0
        self.ballTaken = False

    def getCopy(self):
        newBoard = []
        for row in range(len(self.board)):
            newBoard.append([])
            for col in range(len(self.board)):
                newBoard[row].append(self.board[row][col])
        return Gamestate(newBoard, self.whiteRemaining, self.blackRemaining, self.turn)

    def __str__(self):
        output = ""
        r = 0
        offset = (len(self.board) - 1)/2
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
            output += str(r) + "|" + line[offset:] + "\n"
            r += 1

        output += (" " * (r - offset + 2)) + ("\ " * len(self.board)) + "\n"
        line = ""
        for i in range(len(self.board)):
            line += str(i) + " "
        output += (" " * (r - offset + 3)) + line + "\n"
        return output


class AbaloneGame():

    def __init__(self, gameState, maxPower, maxTurns):
        self.defaultState = gameState
        self.state = gameState.getCopy()
        self.width = len(gameState.board)
        self.maxPower = maxPower

        #max number of turns before quitting
        #1 turn = 1 move for both sides
        self.moveCount = 0
        self.maxTurns = maxTurns

        self.dirGrid = [
        (-1, 0),
        (-1, 1),
        (0, 1),
        (1, 0),
        (1, -1),
        (0, -1)
        ]

    def __str__(self):
        output = str(self.state)
        output += " 0 1\n5 . 2\n 4 3\n"
        return output

    # def printRef(self):
    #     print(" 0 1")
    #     print("5 . 2")
    #     print(" 4 3")

    # def getCount(self):
    #     white = 0
    #     black = 0
    #     for row in self.board:
    #         for item in row:
    #             if item == 1:
    #                 white += 1
    #             elif item == -1:
    #                 black += 1
    #     return (white, black)

    def reset(self):
        self.state = self.defaultState.getCopy()
        self.moveCount = 0

    def isWon(self):
        if self.state.whiteRemaining == 0:
            return -1
        elif self.state.blackRemaining == 0:
            return 1
        else:
            return 0

    def maxMovesExceeded(self):
        return self.moveCount >= self.maxTurns*2

    def getPostgameInfo(self):
        return ("victor: " + str(self.isWon()), "moveCount: " + str(self.moveCount))

    def inBounds(self, row, col):
        return row >= 0 and col >= 0 and row < self.width and col < self.width and self.state.board[row][col] != None

    def makeMove(self, action):
        self.state, reward = self.generateSuccessor(self.state.getCopy(), action)
        self.moveCount += 1
        return reward

    #assuming we're moving a ball from row, col in direction dir
    #return the number of opposing balls we'd need to push to do so
    def getOpposingBalls(self, state, row, col, dir):
        total = 0
        while True:
            currentRow = row + self.dirGrid[dir][0] * (total + 1)
            currentCol = col + self.dirGrid[dir][1] * (total + 1)
            if self.inBounds(currentRow, currentCol):
                if state.board[currentRow][currentCol] == state.turn:
                    #if we have a ball of the same team in front of us, we cannot move forward
                    #set opposition to a ridiculously large number
                    return 1000000
                elif state.board[currentRow][currentCol] == 0:
                    return total
            else:
                return total
            total += 1

    #starting from row, col, count the number of balls in direction dir
    #that match the color of the ball at row, col
    #up to maxPower
    def getConsecutiveBalls(self, state, row, col, dir):
        if state.board[row][col] == 0:
            return 0
        total = 1 #since there's actually a ball, we can start at 1
        while total < self.maxPower:
            currentRow = row + self.dirGrid[dir][0] * total
            currentCol = col + self.dirGrid[dir][1] * total
            if not self.inBounds(currentRow, currentCol) or state.board[currentRow][currentCol] != state.turn:
                break
            total += 1
        return total

    #checks to see if the proposed broadside move is applicable to the provided game state
    def checkBroadMove(self, state, move):
        initialRow = move[0][0]
        initialCol = move[0][1]
        dir = move[1]
        ballDir = move[2]
        numBalls = move[3]
        for ball in range(numBalls):
            newRow = initialRow + self.dirGrid[ballDir][0] * ball + self.dirGrid[dir][0]
            newCol = initialCol + self.dirGrid[ballDir][1] * ball + self.dirGrid[dir][1]
            if not self.inBounds(newRow, newCol) or state.board[newRow][newCol] != 0:
                return False
        return True


    def getActions(self, state):
        actions = []
        assert (state.turn == -1 or state.turn == 1)
        #action format: ((row, col), direction, ball direction, number of balls)
        for row in range(self.width):
            for col in range(self.width):
                if state.board[row][col] == state.turn:
                    #we found a matching ball, check to see what we can do with it

                    #get pushing actions
                    for dir in range(6):
                        if self.inBounds(row + self.dirGrid[dir][0], col + self.dirGrid[dir][1]):
                            opposition = self.getOpposingBalls(state, row, col, dir)
                            power = self.getConsecutiveBalls(state, row, col, (dir+3)%6)
                            for i in range(1, power+1):
                                if i > opposition:
                                    actions.append(((row, col), dir, (dir+3)%6, i))

                    #get broadside actions
                    for ballDir in range(3):
                        power = self.getConsecutiveBalls(state, row, col, ballDir)
                        if power > 1:
                            for dir in range(6):
                                for numBalls in range(2, power+1):
                                    move = ((row, col), dir, ballDir, numBalls)
                                    if self.checkBroadMove(state, move):
                                        actions.append(move)
        return actions

    #applies the provided action to the provided game state
    #returns the new state
    def generateSuccessor(self, state, action):
        row = action[0][0]
        col = action[0][1]
        dir = action[1]
        ballDir = action[2]
        power = action[3]
        reward = 0
        state.ballTaken = False

        if ballDir == (dir + 3)%6:
            #we're performing a pushing action
            newRow = row - self.dirGrid[dir][0] * (power - 1)
            newCol = col - self.dirGrid[dir][1] * (power - 1)
            state.board[newRow][newCol] = 0
            newRow = row + self.dirGrid[dir][0]
            newCol = col + self.dirGrid[dir][1]
            other = state.board[newRow][newCol]
            state.board[newRow][newCol] = state.turn
            if other != 0:
                newRow += self.dirGrid[dir][0]
                newCol += self.dirGrid[dir][1]
                while self.inBounds(newRow, newCol) and state.board[newRow][newCol] == other:
                    newRow += self.dirGrid[dir][0]
                    newCol += self.dirGrid[dir][1]
                if self.inBounds(newRow, newCol):
                    state.board[newRow][newCol] = other
                else:
                    if other == 1:
                        state.whiteRemaining -= 1
                        state.ballTaken = True
                        reward = -1 * BALL_REMOVED_REWARD
                    elif other == -1:
                        state.blackRemaining -= 1
                        state.ballTaken = True
                        reward = BALL_REMOVED_REWARD
        else:
            for ball in range(power):
                newRow = row + self.dirGrid[ballDir][0] * ball
                newCol = col + self.dirGrid[ballDir][1] * ball
                state.board[newRow][newCol] = 0
                newRow += self.dirGrid[dir][0]
                newCol += self.dirGrid[dir][1]
                state.board[newRow][newCol] = state.turn

        if state.blackRemaining == 0:
            reward = GAME_WON_REWARD
        elif state.whiteRemaining == 0:
            reward = -1 * GAME_WON_REWARD

        state.turn *= -1
        state.score += reward
        return (state, reward)
