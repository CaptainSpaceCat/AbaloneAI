import random

class Minimax():

    def __init__(self, explore):
        self.explore = explore

    def getBestAction(self, game, state, evalFn, depth, alpha=None, beta=None, returnAction=True):
        a = alpha
        b = beta
        if depth == 0 or state.whiteRemaining == 0 or state.blackRemaining == 0:
            return evalFn(state)
        if state.turn == 1:
            value = None
            bestAction = None
            actions = game.getActions(state)
            for act in actions:
                successor, reward = game.generateSuccessor(state.getCopy(), act)
                if value == None:
                    value = self.getBestAction(game, successor, evalFn, depth-1, alpha=a, beta=b, returnAction=False)
                else:
                    value = max(value, self.getBestAction(game, successor, evalFn, depth-1, alpha=a, beta=b, returnAction=False))
                if a == None:
                    a = value
                    bestAction = act
                else:
                    if value > a:
                        a = value
                        bestAction = act
                if a != None and b != None and a >= b:
                    break
            if returnAction:
                return bestAction
            return value
        else:
            value = None
            bestAction = None
            actions = game.getActions(state)
            for act in actions:
                successor, reward = game.generateSuccessor(state.getCopy(), act)
                if value == None:
                    value = self.getBestAction(game, successor, evalFn, depth-1, alpha=a, beta=b, returnAction=False)
                else:
                    value = min(value, self.getBestAction(game, successor, evalFn, depth-1, alpha=a, beta=b, returnAction=False))
                if b == None:
                    b = value
                    bestAction = act
                else:
                    if value < b:
                        b = value
                        bestAction = act
                if a != None and b != None and a >= b:
                    break
            if returnAction:
                return bestAction
            return value



        # scores = []
        # actions = game.getActions(state)
        # for act in actions:
        #     successor, reward = game.generateSuccessor(state.getCopy(), act)
        #     value = self.getBestValue(game, successor, evalFn, depth - 1)
        #     scores.append(value + reward)
        #
        # if state.turn == 1:
        #     return max(scores)
        # return min(scores)
    # def getBestValue(self, game, state, evalFn, depth, alpha=None, beta=None):
    #     scores = []
    #     actions = game.getActions(state)
    #     for act in actions:
    #         successor, reward = game.generateSuccessor(state.getCopy(), act)
    #         if depth == 0:
    #             value = evalFn(successor)
    #         else:
    #             value = self.getBestValue(game, successor, evalFn, depth - 1)
    #         scores.append(value)
    #
    #     if state.turn == 1:
    #         return max(scores)
    #     return min(scores)


    #accepts a board, a list of actions, an evaluation function, and a max depth
    #performs the minimax algorithm with alpha-beta pruning to choose the best action for the game state

    def getLearningAction(self, game, evalFn, depth):
        if random.random() < self.explore:
            return self.getRandomAction(game)
        return self.getBestAction(game, game.state, evalFn, depth)

    def getRandomAction(self, game):
        actions = game.getActions(game.state)
        return random.choice(actions)

    def scoreHeuristic(self, state):
        return state.score

    def getHeuristic(self, game, team):
        def heuristic(state):
            score = state.score

            #balls on edge
            total = 0
            for row in range(game.width):
                if row == 0 or row == game.width - 1:
                    for col in range(game.width):
                        if state.board[row][col] == team:
                            total += 1
                else:
                    front = 0
                    back = game.width - 1
                    while state.board[row][front] == None:
                        front += 1
                    while state.board[row][back] == None:
                        back -= 1
                    if state.board[row][front] == team:
                        total += 1
                    if state.board[row][back] == team:
                        total += 1
            score -= total * 10 * team

            #protected balls
            total = 0
            for row in range(game.width):
                for col in range(game.width):
                    if state.board[row][col] == team:
                        protected = True
                        for i in range(len(game.dirGrid)):
                            newRow = game.dirGrid[i][0] + row
                            newCol = game.dirGrid[i][1] + col
                            if not game.inBounds(newRow, newCol) or state.board[newRow][newCol] != team:
                                protected = False
                                break
                        if protected:
                            total += 1
            score += total * 5 * team

            #shared edges
            total = 0
            counted = [] #make this a set
            for row in range(game.width):
                for col in range(game.width):
                    if state.board[row][col] == team:
                        for i in range(len(game.dirGrid)):
                            newRow = game.dirGrid[i][0] + row
                            newCol = game.dirGrid[i][1] + col
                            if game.inBounds(newRow, newCol) and state.board[newRow][newCol] == team and not ((row, col), (newRow, newCol)) in counted and not ((newRow, newCol), (row, col)) in counted:
                                total += 1
                                counted.append(((row, col), (newRow, newCol)))
            score += total * 2 * team

            center = game.width/2
            total = 0
            for i in range(len(game.dirGrid)):
                row = game.dirGrid[i][0] + center
                col = game.dirGrid[i][1] + center
                if game.inBounds(row, col) and state.board[row][col] == team:
                    total += 1
            score += total * 10 * team

            return score

        return heuristic
