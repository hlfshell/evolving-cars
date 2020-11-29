import sys
from src.game.game import Game, EVOLVE_MODE

if len(sys.argv) != 3:
    print("Two command line arguments required - the image asset, and where to save your track file to")
    sys.exit()

imagepath = sys.argv[1]
trackpath = sys.argv[2]

game = Game(imagepath, mode=EVOLVE_MODE, cars_per_generation=50)
game.init()
game.setup()

game.save(trackpath)