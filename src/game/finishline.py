import pygame

FINISH_LINE_COLOR = (0, 255, 0)

class FinishLine():
    def __init__(
        self,
        start_at : (int, int),
        end_at : (int, int),
        ):
        self._start_at = start_at
        self._end_at = end_at

    def draw(self, surface):
         pygame.draw.line(surface, FINISH_LINE_COLOR, self._start_at, self._end_at, width=3)

    def check_collision(self, target):
        clipped_line = target.rect.clipline(self._start_at[0], self._start_at[1], self._end_at[0], self._end_at[1])
        if not clipped_line:
            return False
        else:
            return True 