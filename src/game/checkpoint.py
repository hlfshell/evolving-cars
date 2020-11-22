import pygame
from math import floor

class Checkpoint(pygame.sprite.Sprite):
    def __init__(
        self, id : str,
        start_at : (int, int),
        end_at : (int, int),
        ):
        super().__init__()

        self._id = id
        self._start_at = start_at
        self._end_at = end_at

        # center_x = ((end_at[0] - start_at[0]) / 2) + start_at[0]
        # center_y = ((end_at[1] - start_at[1]) / 2) + start_at[1]
        # center = (floor(center_x), floor(center_y))

        # print(center)

        # length = ( (end_at[0]-start_at[0])**2 + (end_at[1]-start_at[1])**2 )**0.5

        # self.surface = pygame.Surface(center=center, size=length)#center)
        # self.surface.fill((255, 0, 0))
        # self.rect = self.surface.get_rect(topleft=start_at, bottomright=end_at)#center=center)

    def draw(self, surface):
        pygame.draw.line(surface, (255, 255, 0), self._start_at, self._end_at, width=3)

    def check_collision(self, rect):
        pass