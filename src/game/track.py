import pygame

class Track(pygame.sprite.Sprite):

    def __init__(self, filename : str):
        super().__init__()

        self.surf = pygame.image.load(filename)
        self.rect = self.surf.get_rect()
        self.rect.topleft= [0,0]
        self.mask = pygame.mask.from_surface(self.surf)

    def get_size(self):
        return self.surf.get_size()



# b = pygame.sprite.Sprite() # create sprite
# b.image = pygame.image.load("ball.png").convert() # load ball image
# b.rect = b.image.get_rect() # use image extent values
# b.rect.topleft = [0, 0] # put the ball in the top left corner
# screen.blit(b.image, b.rect)