import random

class Minimax():

    def __init__(self, explore):
        self.explore = explore

    #accepts a board, a list of actions, an evaluation function, and a max depth
    #performs the minimax algorithm with alpha-beta pruning to choose the best action for the game state
    def getBestAction(self, game, evalFn, depth):
        scores = []
        actions = game.getActions(game.state)
        for act in actions:
            successor, reward = game.generateSuccessor(game.state.getCopy(), act)
            #nextActions = game.getActions()
            value = evalFn(successor)
            scores.append(value)

        if game.state.turn == 1:
            bestScore = max(scores)
        else:
            bestScore = min(scores)

        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        return actions[random.choice(bestIndices)]

    def getLearningAction(self, game, evalFn, depth):
        scores = []
        actions = game.getActions(game.state)
        for act in actions:
            successor, reward = game.generateSuccessor(game.state.getCopy(), act)
            value = evalFn(successor)
            scores.append(value)

        if game.state.turn == 1:
            bestScore = max(scores)
        else:
            bestScore = min(scores)

        if random.random() < self.explore:
            return random.choice(actions)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        return actions[random.choice(bestIndices)]
