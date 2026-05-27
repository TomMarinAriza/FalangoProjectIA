import pygame as pg
import FalangoGameLogic as Falango
from FalangoEssentialSystems import fingerNames

# pygame setup
pg.init()

SCR_W: int = 1280
SCR_H: int = 720
screen: pg.Surface = pg.display.set_mode((SCR_H, SCR_H))

clock = pg.time.Clock()
pg.display.set_caption("Falango")
running: bool = True

# game setup
game = Falango.Game()

game.player1.left.evalHandPos()
game.player1.right.evalHandPos()
game.player2.left.evalHandPos()
game.player2.right.evalHandPos()

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.unicode in ['1','2','3','4','5','6']:
                # dedo escogido
                game.player1.right.closeHand()
                if event.unicode == '1':
                    game.player1.chooseFinger("thumb")
                elif event.unicode == '2':
                    game.player1.chooseFinger("index")
                elif event.unicode == '3':
                    game.player1.chooseFinger("middle")
                elif event.unicode == '4':
                    game.player1.chooseFinger("ring")
                elif event.unicode == '5':
                    game.player1.chooseFinger("pinkie")
                elif event.unicode == '6':
                    game.player1.chooseFinger("")
                
                if game.player1.chosenFinger in fingerNames: game.player1.right.openFinger(game.player1.chosenFinger)
            elif event.unicode == 'c':
                game.player2.right.closeHand()
                game.player2.chooseFinger(fingerNames)
                game.player2.right.openFinger(game.player2.chosenFinger)
            elif event.unicode == 'p':
                game.player2.chooseFinger(fingerNames)
                game.player2.right.openFinger(game.player2.chosenFinger)
                game.processRound()
                game.resetRightHands()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("gray")

    # RENDER YOUR GAME HERE
    screen.blit(pg.image.load(game.player1.left.sprite), (100, 200))
    screen.blit(pg.image.load(game.player1.right.sprite), (100, 400))
    screen.blit(pg.image.load(game.player2.right.sprite), (400, 200))
    screen.blit(pg.image.load(game.player2.left.sprite), (400, 400))

    # flip() the display to put your work on screen
    pg.display.flip()

    clock.tick(60)  # limits FPS to 60

pg.quit()