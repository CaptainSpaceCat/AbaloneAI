import Tkinter as tk
from Tkinter import *

LARGE_FONT= ("Verdana", 12)

class GraphicalGame():

    def __init__(self, game, player, minimax, evalFn, depth):
        self.command = []
        self.game = game
        self.player = player
        self.minimax = minimax
        self.eval = evalFn
        self.depth = depth

        self.root = tk.Tk()
        self.root.title("Abalone")
        self.root.configure(background='tan')

        self.slot_empty = PhotoImage(file="slot_empty.gif")
        self.slot_white = PhotoImage(file="slot_white.gif")
        self.slot_black = PhotoImage(file="slot_black.gif")
        self.selected_empty = PhotoImage(file="selected_empty.gif")
        self.selected_white = PhotoImage(file="selected_white.gif")
        self.selected_black = PhotoImage(file="selected_black.gif")

        self.buttons = []

        self.createBoard()
        self.displayBoard()

        self.root.mainloop()

    def getButtonCommand(self, row, col):
        def buttonCommand():
            if not (row, col) in self.command:
                self.command.append((row, col))
                if self.player == -1:
                    self.buttons[row][col].configure(image=self.selected_black)
                elif self.player == 1:
                    self.buttons[row][col].configure(image=self.selected_white)
                #make sure that the one we just appended is adjacent to the last one in the list
                self.handleCommand()
        return buttonCommand

    def createBoard(self):
        for r in range(self.game.width):
            self.buttons.append([])
            for c in range(self.game.width):
                if self.game.state.board[r][c] != None:
                    new = tk.Button(self.root, highlightthickness=0, height=64, width=64, image=self.slot_empty, command=self.getButtonCommand(r, c))
                    self.buttons[r].append(new)
                    new.grid(row=r, column=c*2+r-(self.game.width-1)/2, rowspan=1, columnspan=2)
                else:
                    self.buttons[r].append(None)
        for r in range(self.game.width):
            self.root.grid_rowconfigure(r, minsize=10)
        for c in range(self.game.width*2):
            self.root.grid_columnconfigure(c, minsize=10)

        self.whiteLabel = tk.Label(self.root, text="White remaining: " + str(self.game.state.whiteRemaining), font=LARGE_FONT)
        self.blackLabel = tk.Label(self.root, text="Black remaining: " + str(self.game.state.whiteRemaining), font=LARGE_FONT)
        self.whiteLabel.grid(row=self.game.width+1, column=0, columnspan=self.game.width, sticky=W)
        self.blackLabel.grid(row=self.game.width+1, column=self.game.width, columnspan=self.game.width, sticky=E)

        self.quitButton = tk.Button(self.root, text="Quit Game", font=LARGE_FONT, command=self.root.destroy)
        self.quitButton.grid(row=self.game.width+2, column=0, columnspan=self.game.width*2)

    def displayBoard(self):
        self.whiteLabel.configure(text="White remaining: " + str(self.game.state.whiteRemaining))
        self.blackLabel.configure(text="Black remaining: " + str(self.game.state.blackRemaining))
        if self.game.state.whiteRemaining == 0:
            self.root.configure(background='black')
        elif self.game.state.blackRemaining == 0:
            self.root.configure(background='white')
        for r in range(self.game.width):
            for c in range(self.game.width):
                if self.game.state.board[r][c] == 0:
                    self.buttons[r][c].configure(image=self.slot_empty)
                elif self.game.state.board[r][c] == -1:
                    self.buttons[r][c].configure(image=self.slot_black)
                elif self.game.state.board[r][c] == 1:
                    self.buttons[r][c].configure(image=self.slot_white)

    def handleCommand(self):
        if not self.newCommandAdjacent() or self.game.state.whiteRemaining == 0 or self.game.state.blackRemaining == 0:
            self.cancelCommand()
        else:
            lastSlot = self.command[len(self.command)-1]
            if self.game.state.board[lastSlot[0]][lastSlot[1]] != self.player or len(self.command) > self.game.maxPower:
                if len(self.command) < 2:
                    self.cancelCommand()
                else:
                    print len(self.command)
                    move = self.commandToMove()
                    if self.validateMove(move):
                        self.game.makeMove(move)
                        if self.game.state.whiteRemaining > 0 and self.game.state.blackRemaining > 0:
                            self.highlightOpponent()
                            self.command = []
                            Entry(self.root).after(500, self.makeOpposingMove)
                        else:
                            self.cancelCommand()
                    else:
                        self.cancelCommand()

    def cancelCommand(self):
        self.command = []
        self.displayBoard()

    def newCommandAdjacent(self):
        if len(self.command) < 2:
            return True
        for i in range(len(self.game.dirGrid)):
            dir = self.game.dirGrid[i]
            newest = self.command[len(self.command)-1]
            if self.command[len(self.command)-2] == (dir[0] + newest[0], dir[1] + newest[1]):
                return True
        return False

    def highlightOpponent(self):
        for r in range(self.game.width):
            for c in range(self.game.width):
                if self.game.state.board[r][c] == 0:
                    self.buttons[r][c].configure(image=self.slot_empty)
                elif self.game.state.board[r][c] == -1:
                    if self.player == -1:
                        self.buttons[r][c].configure(image=self.slot_black)
                    elif self.player == 1:
                        self.buttons[r][c].configure(image=self.selected_black)
                elif self.game.state.board[r][c] == 1:
                    if self.player == -1:
                        self.buttons[r][c].configure(image=self.selected_white)
                    elif self.player == 1:
                        self.buttons[r][c].configure(image=self.slot_white)

    def makeOpposingMove(self):
        bestAction = self.minimax.getBestAction(self.game, self.game.state, self.eval, self.depth)
        self.game.makeMove(bestAction)
        self.displayBoard()

    def validateMove(self, move):
        return (move in self.game.getActions(self.game.state))

    def commandToMove(self):
        coords = self.command[0]
        ballDir = -1
        ballNum = len(self.command)-1
        for i in range(len(self.game.dirGrid)):
            dir = self.game.dirGrid[i]
            if self.command[1][0] == coords[0]+dir[0] and self.command[1][1] == coords[1]+dir[1]:
                ballDir = i
                break
        lastBall = self.command[len(self.command)-2]
        moveDir = -1
        for i in range(len(self.game.dirGrid)):
            dir = self.game.dirGrid[i]
            if self.command[len(self.command)-1][0] == lastBall[0]+dir[0] and self.command[len(self.command)-1][1] == lastBall[1]+dir[1]:
                moveDir = i
                break

        if moveDir == ballDir or (abs(moveDir - ballDir) != 3 and ballDir > 2):
            print (self.command[len(self.command)-2], moveDir, (ballDir+3)%6, ballNum)
            return (self.command[len(self.command)-2], moveDir, (ballDir+3)%6, ballNum)
        print (coords, moveDir, ballDir, ballNum)
        return (coords, moveDir, ballDir, ballNum)
