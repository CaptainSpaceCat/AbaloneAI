import math, random
from collections import defaultdict
import game, util, Minimax, TDLearning
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='file', default="default")
parser.add_argument('-n', dest='num', default="0")
parser.add_argument('-p', dest='play', default=False, action='store_true')
parser.add_argument('-w', dest='weights')
parser.add_argument('-s', dest='save')
args = vars(parser.parse_args())
#
# if args['f'] == None:
#     args['f'] = "default"
#
# numGames = 1
# if args['n'] != None:
numGames = int(args['num'])

gameInfo = util.getGameInfo(args['file'] + ".txt")
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
whiteWin, blackWin = TDLearning.getWinFeatures()
features.append(whiteWin)
features.append(blackWin)

features.append(TDLearning.getProtectedFeature(abgame, -1))
features.append(TDLearning.getProtectedFeature(abgame, 1))

features.append(TDLearning.getBorderFeature(abgame, 1))
features.append(TDLearning.getBorderFeature(abgame, -1))
#features.append(TDLearning.getTurnFeature(1))
#features.append(TDLearning.getTurnFeature(-1))

minimax = Minimax.Minimax(explore=.2)
tdlearning = TDLearning.TDLearning(features, step=.1, discount=.9)

print abgame
print "Training algorithm..."

if args['weights'] != None:
    tdlearning.applyWeights(util.getPreloadedWeights(args['weights'] + ".txt"))

for _ in range(numGames):
    while not (abgame.maxMovesExceeded() or abgame.isWon()):
        actions = abgame.getActions(abgame.state)
        #print actions
        bestAction = minimax.getLearningAction(abgame, tdlearning.getValue, depth=2)#actions[random.randint(0, len(actions))]
        #print(bestAction)
        oldState = abgame.state.getCopy()
        reward = abgame.makeMove(bestAction)
        tdlearning.updateWeights(oldState, bestAction, reward, abgame.state)
        #print abgame

    print abgame.getPostgameInfo()
    abgame.reset()

tdlearning.printWeights()
if args['save'] != None:
    util.saveCurrentWeights(tdlearning.weights, args['save'] + ".txt")

if args['play']:
    while not (abgame.maxMovesExceeded() or abgame.isWon()):
        if abgame.state.turn == -1:
            print abgame
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

    print abgame
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
