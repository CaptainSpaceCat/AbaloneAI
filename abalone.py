import math, random
from collections import defaultdict
import game, util, Minimax, TDLearning
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '-file')
parser.add_argument('-n', '-num')
parser.add_argument('-p', dest='play', default=False, action='store_true')
args = vars(parser.parse_args())

if args['f'] == None:
    args['f'] = "default"

numGames = 1
if args['n'] != None:
    numGames = int(args['n'])

gameInfo = util.getGameInfo(args['f'] + ".txt")
abgame = game.AbaloneGame(gameInfo[0], gameInfo[1], 1000)

features = []
for row in range(abgame.width):
    for col in range(abgame.width):
        if abgame.inBounds(row, col):
            features.append(TDLearning.getBoardIndicator(row, col, 1))
            features.append(TDLearning.getBoardIndicator(row, col, -1))
whiteLoss, blackLoss = TDLearning.getLossFeatures(gameInfo[0].whiteRemaining)
features.append(whiteLoss)
features.append(blackLoss)
#features.append(TDLearning.getTurnFeature(1))
#features.append(TDLearning.getTurnFeature(-1))

minimax = Minimax.Minimax(explore=.2)
tdlearning = TDLearning.TDLearning(features, step=.1, discount=.9)

abgame.printSelf()
print "Training algorithm..."
for _ in range(numGames):
    while not (abgame.maxMovesExceeded() or abgame.isWon()):
        if args['play'] and abgame.state.turn == -1:
            abgame.printSelf()
            abgame.makeMove(util.getPlayerAction())
        else:
            actions = abgame.getActions(abgame.state)
            #print actions
            bestAction = minimax.getLearningAction(abgame, tdlearning.getValue, depth=2)#actions[random.randint(0, len(actions))]
            #print(bestAction)
            oldState = abgame.state.getCopy()
            reward = abgame.makeMove(bestAction)
            tdlearning.updateWeights(oldState, bestAction, reward, abgame.state)
            #abgame.printSelf()

    print abgame.getPostgameInfo()
    abgame.reset()


tdlearning.printWeights()

while not (abgame.maxMovesExceeded() or abgame.isWon()):
    if abgame.state.turn == -1:
        abgame.printSelf()
        playerMove = util.getPlayerAction()
        if playerMove:
            abgame.makeMove(playerMove)
        else:
            actions = abgame.getActions(abgame.state)
            #print actions
            bestAction = minimax.getBestAction(abgame, tdlearning.getValue, depth=2)#actions[random.randint(0, len(actions))]
            #print(bestAction)
            abgame.makeMove(bestAction)
    else:
        actions = abgame.getActions(abgame.state)
        #print actions
        bestAction = minimax.getBestAction(abgame, tdlearning.getValue, depth=2)#actions[random.randint(0, len(actions))]
        #print(bestAction)
        abgame.makeMove(bestAction)

print abgame.getPostgameInfo()

# actions = abgame.getActions(-1)
# print(actions)
# abgame.makeMove(((2, 4), 4, 2, 2))
# abgame.printSelf()

'''potential heuristics:
- num shared edges (incentivizes clumping)
- distance from center
- aggressive knockouts
-
'''
