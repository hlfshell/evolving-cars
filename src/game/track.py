import pygame

class Track:

    def __init__(self, filename : str):
        self._surface = pygame.image.load("track1.png")#.convert()
        self._rect = self._surface.get_rect()
        self._rect.topleft= [0,0]

    def get_size(self):
        return self._surface.get_size()



# b = pygame.sprite.Sprite() # create sprite
# b.image = pygame.image.load("ball.png").convert() # load ball image
# b.rect = b.image.get_rect() # use image extent values
# b.rect.topleft = [0, 0] # put the ball in the top left corner
# screen.blit(b.image, b.rect)