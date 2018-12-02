import math, random
from collections import defaultdict
import game, util, Minimax, TDLearning, graphics
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='file', default="default", help="[string] the filename from which to import the game board")
parser.add_argument('-n', dest='num', default="0", help="[int] number of training iterations")
parser.add_argument('-p', dest='play', default=False, action='store_true', help="play against the AI")
parser.add_argument('-w', dest='weights', help="[string], filename from which to import pre-existing weights vector")
parser.add_argument('-s', dest='save', help="[string] filename in which to store weights vector after training")
parser.add_argument('-r', dest='rand', default="0", help="[int] number of testing iterations, testing the AI against a random agent")
parser.add_argument('-t', dest='test', default="0", help="[int] number of testing iterations, testing the AI against a heuristic agent")

parser.add_argument('-discount', dest='discount', default=".9")
parser.add_argument('-step', dest='step', default=".001")
parser.add_argument('-explore', dest='explore', default=".2")
args = vars(parser.parse_args())

numGames = int(args['num'])

gameInfo = util.getGameInfo("boards/" + args['file'] + ".txt")
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

features.append(TDLearning.getSharedEdgeFeature(abgame, 1))
features.append(TDLearning.getSharedEdgeFeature(abgame, -1))

features.append(TDLearning.getBorderFeature(abgame, 1))
features.append(TDLearning.getBorderFeature(abgame, -1))

features.append(TDLearning.getCenterFeature(abgame, 1))
features.append(TDLearning.getCenterFeature(abgame, -1))

# features.append(TDLearning.getScoreFeature())

# whiteWin, blackWin = TDLearning.getWinFeatures()
# features.append(whiteWin)
# features.append(blackWin)


# features.append(TDLearning.getProtectedFeature(abgame, 1))
# features.append(TDLearning.getProtectedFeature(abgame, -1))

# features.append(TDLearning.getPushFeature(abgame, 1))
# features.append(TDLearning.getPushFeature(abgame, -1))

#features.append(TDLearning.getTurnFeature(1))
#features.append(TDLearning.getTurnFeature(-1))


minimax = Minimax.Minimax(explore=float(args["explore"]))
tdlearning = TDLearning.TDLearning(features, step=float(args["step"]), discount=float(args["discount"]))

TRAINING_DEPTH = 2
GAME_DEPTH = 3

print abgame
print "Training algorithm..."

if args['weights'] != None:
    tdlearning.applyWeights(util.getPreloadedWeights("weights/" + args['weights'] + ".txt"))

for _ in range(numGames):
    while not (abgame.maxMovesExceeded() or abgame.isWon()):
        actions = abgame.getActions(abgame.state)
        #print actions
        bestAction = minimax.getLearningAction(abgame, tdlearning.getValue, depth=TRAINING_DEPTH)#actions[random.randint(0, len(actions))]
        #print(bestAction)
        oldState = abgame.state.getCopy()
        reward = abgame.makeMove(bestAction)
        tdlearning.updateWeights(oldState, bestAction, reward, abgame.state)
        if args['save'] != None:
            util.saveCurrentWeights(tdlearning.weights, "weights/" + args['save'] + ".txt")
        #print abgame

    print abgame.getPostgameInfo()
    abgame.reset()

tdlearning.printWeights()

# whiteHeuristic = minimax.getHeuristic(abgame, 1)
# blackHeuristic = minimax.getHeuristic(abgame, -1)
if args['play']:
    graph = graphics.GraphicalGame(abgame, -1, minimax, tdlearning.getValue, GAME_DEPTH)
    # while not (abgame.maxMovesExceeded() or abgame.isWon()):
    #     if abgame.state.turn == -1:
    #         print abgame
    #         actions = abgame.getActions(abgame.state)
    #         playerMove = util.getPlayerAction()
    #         if playerMove:
    #             while not playerMove in actions:
    #                 print "Invalid move."
    #                 playerMove = util.getPlayerAction()
    #             abgame.makeMove(playerMove)
    #         else:
    #             bestAction = minimax.getBestAction(abgame, tdlearning.getValue, depth=TRAINING_DEPTH)#actions[random.randint(0, len(actions))]
    #             #bestAction = minimax.getBestAction(abgame, blackHeuristic, depth=2)
    #             abgame.makeMove(bestAction)
    #     else:
    #         actions = abgame.getActions(abgame.state)
    #         bestAction = minimax.getBestAction(abgame, tdlearning.getValue, depth=TRAINING_DEPTH)#actions[random.randint(0, len(actions))]
    #         #bestAction = minimax.getBestAction(abgame, whiteHeuristic, depth=2)
    #         abgame.makeMove(bestAction)
    #
    # print abgame
    print abgame.getPostgameInfo()

numTests = int(args['rand'])
totalGames = 0
aiWins = 0
if numTests > 0:
    print "\nTesting AI against random agent..."
    for _ in range(numTests):
        while not (abgame.maxMovesExceeded() or abgame.isWon()):
            if abgame.state.turn == -1:
                bestAction = minimax.getRandomAction(abgame)
            else:
                bestAction = minimax.getBestAction(abgame, abgame.state, tdlearning.getValue, depth=TRAINING_DEPTH)
            abgame.makeMove(bestAction)

        print abgame.getPostgameInfo()
        totalGames += 1
        if abgame.getPostgameInfo()[0] == "victor: 1":
            aiWins += 1
        abgame.reset()

    print "% of games won by AI: " + str(float(aiWins)/float(totalGames))

numTests = int(args['test'])
totalGames = 0
aiWins = 0
heuristic = minimax.getHeuristic(abgame, 1)
if numTests > 0:
    print "\nTesting AI against heuristic agent..."
    for _ in range(numTests):
        while not (abgame.maxMovesExceeded() or abgame.isWon()):
            actions = abgame.getActions(abgame.state)
            if abgame.state.turn == -1:
                bestAction = minimax.getBestAction(abgame, abgame.state, heuristic, depth=TRAINING_DEPTH)
            else:
                bestAction = minimax.getBestAction(abgame, abgame.state, tdlearning.getValue, depth=TRAINING_DEPTH)
            abgame.makeMove(bestAction)

        print abgame.getPostgameInfo()
        totalGames += 1
        if abgame.getPostgameInfo()[0] == "victor: 1":
            aiWins += 1
        abgame.reset()

    print "% of games won by AI: " + str(float(aiWins)/float(totalGames))

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
