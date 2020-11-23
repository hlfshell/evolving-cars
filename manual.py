from src.game.game import Game

game = Game("assets/track1.png")
game._show_checkpoints = True
game.init()
game.setup()
game.manual_play()