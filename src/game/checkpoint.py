import pygame
from .bresenham import define_line

CHECKPOINT_COLOR = (255, 255, 0)

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

        self._rects : [pygame.Rect] = []

        self.create_rects()

    def draw(self, surface):
         pygame.draw.line(surface, CHECKPOINT_COLOR, self._start_at, self._end_at, width=3)
    
    # Use the Bresenham algorithm to find the list of points a line would
    # contain and creae one pixel rects to make use of pygame's rect
    # collision detection
    def create_rects(self):
        pixels = define_line(self._start_at[0], self._start_at[1], self._end_at[0], self._end_at[1])
        for pixel in pixels:
            rect = pygame.Rect(pixel[0], pixel[1], pixel[0], pixel[1])
            self._rects.append(rect)

    def check_collision(self, target):
        for rect in self._rects:
            if rect.colliderect(target):
                return True
        return False