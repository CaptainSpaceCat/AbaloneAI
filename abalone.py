import math, random
from collections import defaultdict
import game, util, Minimax, TDLearning
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='file', default="default", help="[string] the filename from which to import the game board")
parser.add_argument('-n', dest='num', default="0", help="[int] number of training iterations")
parser.add_argument('-p', dest='play', default=False, action='store_true', help="play against the AI")
parser.add_argument('-w', dest='weights', help="[string], filename from which to import pre-existing weights vector")
parser.add_argument('-s', dest='save', help="[string] filename in which to store weights vector after training")
parser.add_argument('-r', dest='rand', default="0", help="[int] number of testing iterations, testing the AI against a random agent")
parser.add_argument('-t', dest='test', default="0", help="[int] number of testing iterations, testing the AI against a heuristic agent")
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
            #features.append(TDLearning.getBoardIndicator(row, col, 1))
            #features.append(TDLearning.getBoardIndicator(row, col, -1))
            pass
whiteLoss, blackLoss = TDLearning.getLossFeatures(gameInfo[0].whiteRemaining)
features.append(whiteLoss)
features.append(blackLoss)
whiteWin, blackWin = TDLearning.getWinFeatures()
features.append(whiteWin)
features.append(blackWin)

features.append(TDLearning.getSharedEdgeFeature(abgame, 1))
features.append(TDLearning.getSharedEdgeFeature(abgame, -1))

features.append(TDLearning.getProtectedFeature(abgame, 1))
features.append(TDLearning.getProtectedFeature(abgame, -1))

features.append(TDLearning.getBorderFeature(abgame, 1))
features.append(TDLearning.getBorderFeature(abgame, -1))

features.append(TDLearning.getCenterFeature(abgame, 1))
features.append(TDLearning.getCenterFeature(abgame, -1))

# features.append(TDLearning.getPushFeature(abgame, 1))
# features.append(TDLearning.getPushFeature(abgame, -1))

#features.append(TDLearning.getTurnFeature(1))
#features.append(TDLearning.getTurnFeature(-1))

minimax = Minimax.Minimax(explore=.2)
tdlearning = TDLearning.TDLearning(features, step=.001, discount=.9)

MINIMAX_DEPTH = 1

print abgame
print "Training algorithm..."

if args['weights'] != None:
    tdlearning.applyWeights(util.getPreloadedWeights(args['weights'] + ".txt"))

for _ in range(numGames):
    while not (abgame.maxMovesExceeded() or abgame.isWon()):
        actions = abgame.getActions(abgame.state)
        #print actions
        bestAction = minimax.getLearningAction(abgame, tdlearning.getValue, depth=MINIMAX_DEPTH)#actions[random.randint(0, len(actions))]
        #print(bestAction)
        oldState = abgame.state.getCopy()
        reward = abgame.makeMove(bestAction)
        tdlearning.updateWeights(oldState, bestAction, reward, abgame.state)
        #print abgame

    print abgame.getPostgameInfo()
    abgame.reset()
    if args['save'] != None:
        util.saveCurrentWeights(tdlearning.weights, args['save'] + ".txt")

tdlearning.printWeights()

# whiteHeuristic = minimax.getHeuristic(abgame, 1)
# blackHeuristic = minimax.getHeuristic(abgame, -1)
if args['play']:
    while not (abgame.maxMovesExceeded() or abgame.isWon()):
        if abgame.state.turn == -1:
            print abgame
            playerMove = util.getPlayerAction()
            if playerMove:
                abgame.makeMove(playerMove)
            else:
                actions = abgame.getActions(abgame.state)
                bestAction = minimax.getBestAction(abgame, tdlearning.getValue, depth=3)#actions[random.randint(0, len(actions))]
                #bestAction = minimax.getBestAction(abgame, blackHeuristic, depth=2)
                abgame.makeMove(bestAction)
        else:
            actions = abgame.getActions(abgame.state)
            bestAction = minimax.getBestAction(abgame, tdlearning.getValue, depth=3)#actions[random.randint(0, len(actions))]
            #bestAction = minimax.getBestAction(abgame, whiteHeuristic, depth=2)
            abgame.makeMove(bestAction)

    print abgame
    print abgame.getPostgameInfo()

numTests = int(args['rand'])
randomWins = 0
aiWins = 0
if numTests > 0:
    print "\nTesting AI against random agent..."
    for _ in range(numTests):
        while not (abgame.maxMovesExceeded() or abgame.isWon()):
            actions = abgame.getActions(abgame.state)
            #print actions
            if abgame.state.turn == -1:
                bestAction = minimax.getRandomAction(abgame)
            else:
                #bestAction = minimax.getRandomAction(abgame)
                bestAction = minimax.getBestAction(abgame, tdlearning.getValue, depth=MINIMAX_DEPTH)#actions[random.randint(0, len(actions))]
            #print(bestAction)
            abgame.makeMove(bestAction)
            #print abgame

        print abgame.getPostgameInfo()
        if abgame.getPostgameInfo()[0] == "victor: 1":
            aiWins += 1
        else:
            randomWins += 1
        abgame.reset()

    print "% of games won by AI: " + str(float(aiWins)/float(aiWins+randomWins))

numTests = int(args['test'])
randomWins = 0
aiWins = 0
heuristic = minimax.getHeuristic(abgame, 1)
if numTests > 0:
    print "\nTesting AI against heuristic agent..."
    for _ in range(numTests):
        while not (abgame.maxMovesExceeded() or abgame.isWon()):
            actions = abgame.getActions(abgame.state)
            #print actions
            if abgame.state.turn == -1:
                bestAction = minimax.getBestAction(abgame, heuristic, depth=MINIMAX_DEPTH)
            else:
                #bestAction = minimax.getRandomAction(abgame)
                bestAction = minimax.getBestAction(abgame, tdlearning.getValue, depth=MINIMAX_DEPTH)#actions[random.randint(0, len(actions))]
            #print(bestAction)
            abgame.makeMove(bestAction)
            #print abgame

        print abgame.getPostgameInfo()
        if abgame.getPostgameInfo()[0] == "victor: 1":
            aiWins += 1
        elif abgame.getPostgameInfo()[0] == "victor: -1":
            randomWins += 1
        abgame.reset()

    print "% of games won by AI: " + str(float(aiWins)/float(aiWins+randomWins))

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
