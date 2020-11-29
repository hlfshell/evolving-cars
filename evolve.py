from src.game.game import Game, EVOLVE_MODE

game = Game("assets/track3.png", mode=EVOLVE_MODE, cars_per_generation=50)
game._show_checkpoints = True
game.init()
game.setup()
game.evolve()