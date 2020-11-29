import pygame
from .bresenham import define_line
from uuid import uuid4 as uuid

CHECKPOINT_COLOR = (255, 255, 0)

class Checkpoint(pygame.sprite.Sprite):
    def __init__(
        self,
        start_at : (int, int),
        end_at : (int, int),
        ):
        super().__init__()

        self._id = uuid()
        self._start_at = start_at
        self._end_at = end_at

    def draw(self, surface):
         pygame.draw.line(surface, CHECKPOINT_COLOR, self._start_at, self._end_at, width=3)

    def check_collision(self, target):
        clipped_line = target.rect.clipline(self._start_at[0], self._start_at[1], self._end_at[0], self._end_at[1])
        if not clipped_line:
            return False
        else:
            return True 