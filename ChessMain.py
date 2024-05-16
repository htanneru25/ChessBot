"""This is our driver file, it is responsible for handling user input and displaying
the current gamestate object"""

import pygame as p
from ChessImages import ChessEngine, SmartMoveFinder

# Assuming GameState is the class we want to import

WIDTH = HEIGHT = 512
Dimensions = 8  # 8*8 board
SQ_SIZE = HEIGHT // Dimensions
MAX_FPS = 15  # for animations
IMAGES = {}


def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        # we can access image by saying Images["wp"]


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()  # Create an instance of GameState
    validMoves = gs.getValidMoves()
    moveMade = False  # Flag variable when a move is made
    animate = False
    loadImages()

    running = True
    sqselected = ()  # no square selected initially (tuple meaning row and column)
    playerClicks = []
    gameOver = False# keep track of player click
    playerOne = True
    playerTwo = False
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqselected == (row, col):  # user clicked the same square twice
                        sqselected = ()  # deselect
                    else:
                        playerClicks = []
                        sqselected = (row, col)
                        playerClicks.append(sqselected)  # append for both first and second clicks
                    if len(playerClicks) == 2:  # after the second click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:  # i here
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqselected = ()  # reset our click
                                playerClicks = []
                                break  # Add a break statement to exit the loop after making the move
                        if not moveMade:
                            playerClicks = [sqselected]
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:  # it will undo the move when you press z
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if event.key == p.K_r:  # reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqselected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade =True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            if gs.checkmate:
                gameOver = True
                if gs.whiteToMove:
                    drawText(screen, 'Black wins by checkmate')
                else:
                    drawText(screen, 'White wins by checkmate')
            elif gs.stalemate:
                gameOver = True
                drawText(screen, 'Stalemate')

        drawGameState(screen, gs, validMoves, sqselected)  # Draw the game state on the screen
        clock.tick(MAX_FPS)
        p.display.flip()  # Update the display


def highlightSquares(screen, gs, validMoves, sqselected):
    if sqselected != ():
        r, c = sqselected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # sqSelected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value -> transparent; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawGameState(screen, gs, validMoves, sqselected):
    """
    Draw the current game state on the screen.
    :param screen: Pygame screen object
    :param gs: GameState object representing the current state of the game
    """
    drawBoard(screen)  # Pass the board to drawBoard
    # add in piece highlighting or move suggestions (later)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares
    highlightSquares(screen, gs, validMoves, sqselected)  # Highlight squares


def drawBoard(screen):
    global colors
    """
    Draw the squares and pieces on the chessboard.
    :param screen: Pygame screen object
    :param board: 2D list representing the board state
    """
    colors = [p.Color("light grey"), p.Color("brown")]
    for r in range(Dimensions):
        for c in range(Dimensions):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    """
    Draw the pieces on the board using the current GameState board.
    :param screen: Pygame screen object
    :param board: 2D list representing the board state
    """
    for r in range(Dimensions):
        for c in range(Dimensions):
            piece = board[r][c]
            if piece != "--":  # not an empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10  # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()






