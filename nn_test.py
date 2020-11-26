from src.game.game import Game, EVOLVE_MODE

game = Game("assets/track1.png", mode = EVOLVE_MODE)
game._show_checkpoints = True
game.init()
game.setup()
game.manual_play()