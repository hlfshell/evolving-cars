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

        self._line = Line(start_at, end_at)

        self._rects : [pygame.Rect] = []

        self.create_rects(start_at[0], start_at[1], end_at[0], end_at[1])

    def draw(self, surface):
        self._line.draw(surface, (255, 255, 0))
    
    # All create_rects are essentially copied from the
    # Pseudocode from the wikipedia of Besenha's Algorithm
    # found at https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
    # The overall idea is that this can handle lines of any type
    # (including vertical which broke my euclidean approach)
    # to plot a line. Instead of plotting - I will just be creating
    # one pixel rects to make use of pygame's rect collision.

    def create_rects(self, x0, y0, x1, y1):
        if abs(y1-y0) < abs(x1-x0):
            if x0 > x1:
               self.create_rects_low(x1, y1, x0, y0)
            else:
                self.create_rects_low(x0, y0, x1, y1)
        else:
            if y0 > y1:
                self.create_rects_high(x1, y1, x0, y0)
            else:
                self.create_rects_high(x0, y0, x1, y1)

    def create_rects_low(self, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        yi = 1
        if dy < 0:
            yi = -1
            dy = -dy
        
        D = (2 * dy) - dx
        y = y0

        for x in range(x0, x1):
            rect = pygame.Rect(x, y, x, y)
            self._rects.append(rect)

            if D > 0:
                y = y + yi
                D = D + (2 * (dy-dx))
            else:
                D = D + 2*dy

    def create_rects_high(self, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        xi = 1

        if dx < 0:
            xi = -1
            dx = -dx
        
        D = (2 * dx) - dy
        x = x0

        for y in range(y0, y1):
            # rect = pygame.Surface((x, y),size=1).get_rect(center=(x,y))
            rect = pygame.Rect(x, y, x, y)
            self._rects.append(rect)
            
            if D > 0:
                x = x + xi
                D = D + (2 * (dx - dy))
            else:
                D = D + 2*dx

    def check_collision(self, target):
        for rect in self._rects:
            if rect.colliderect(target):
                return True
        return False