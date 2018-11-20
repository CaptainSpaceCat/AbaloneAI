def getBoardIndicator(row, col, team):

    def boardIndicator(state):
        if state.board[row][col] == team:
            return 1
        return 0

    return ("indicator " + str(row) + ":" + str(col) + "|" + str(team), boardIndicator)

def getLossFeatures(maxBalls):

    def whiteLossFeature(state):
        return float(state.whiteRemaining)/maxBalls

    def blackLossFeature(state):
        return float(state.blackRemaining)/maxBalls

    return (("white loss percent", whiteLossFeature), ("black loss percent", blackLossFeature))

def getTurnFeature(team):

    def turnFeature(state):
        if state.turn == team:
            return 1
        return 0

    return ("turn " + str(team), turnFeature)

class TDLearning():

    def __init__(self, featureList, step, discount):

        #featurelist: list of features, each feature is a tuple of the form (name, function)
        self.featureList = featureList
        self.weights = []
        self.step = step
        self.discount = discount

        for feature in featureList:
            self.weights.append(1)

    #pass in external weights vector, for use once weights have been computed
    def applyWeights(self, newWeights):
        self.weights = newWeights
        assert(len(self.weights) == len(self.featureList))

    #returns the value of the game state based on the feature functions and weights
    def getValue(self, state):
        result = 0
        for i in range(len(self.featureList)):
            result += self.featureList[i][1](state) * self.weights[i]
        return result

    def updateWeights(self, state, action, reward, newState):
        scalar = self.step * (self.getValue(state) - (reward + self.discount * self.getValue(newState)))
        newWeights = []
        for i in range(len(self.weights)):
            newWeights.append(self.weights[i] - scalar * self.featureList[i][1](state))
        self.weights = newWeights

    def printWeights(self):
        for i in range(len(self.featureList)):
            print self.featureList[i][0] + " => " + str(self.weights[i])
