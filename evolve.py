import sys
from src.game.game import Game, load_from_file

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("A command line argumnet is required - a specified track.json file")
    sys.exit()

trackpath = sys.argv[1]

populaton_size = 50
if len(sys.argv) == 3:
    population_size = int(sys.argv[2])

game = load_from_file(trackpath)
game._cars_per_generation = populaton_size
game.init()
game.evolve()