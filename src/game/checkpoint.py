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

    def draw(self, surface):
        self._line.draw(surface, (255, 255, 0))

    def check_collision(self, rect,surf):
        size = rect.size
        topleft = rect.topleft
        bottomright = (rect.topleft[0] + size[0], rect.topleft[1] +size[1])
        
        # Create a line for each of the 
        lines = []
        lines.append( Line( topleft, (topleft[0]+size[0], topleft[1]) ) ) #TOP
        lines.append( Line( topleft, (topleft[0], topleft[1]+size[1]) ) ) #LEFT
        lines.append( Line( (topleft[0]+size[0], topleft[1]), bottomright ) ) #RIGHT
        lines.append( Line( (topleft[0], topleft[1]+size[1]), bottomright ) ) #BOTTOM
        
        for line in lines:
            line.draw(surf, (255, 0, 0))
            pygame.display.update()
            if self._line.intersects(line):
                return True

class Line():

    def __init__(self, start_at, end_at):
        
        self.start = start_at
        self.end = end_at

        rise = (end_at[1] - start_at[1])
        run =  (end_at[0] - start_at[0])

        if run == 0:
            #uh-oh - vertical line. Just go with a very large slope
            self.m = 10000
        else:
            self.m = rise / run
        self.b = - (self.m * start_at[0]) / start_at[1] # I should probably set this to 1 if we're at the 0th height

    def draw(self, surface, color):
        pygame.draw.line(surface, color, self.start, self.end, width=3)
        pygame.display.update()

    def intersects(self, line):
        # y = mx + b <~ match y's
        # m_1x + b_1 = m_2x + b_2
        # (m_1-m_2)x = b_2 - b_1
        # x = (b_2 - b_1 )/ (m_1-m_2)
        # y = m_1x + b_1 <- fill it in
        num_x = (line.b - self.b)
        denom_x = (self.m - line.m)
        if denom_x == 0:
            # Parallel lines! Can't intersect
            return False
        x = num_x / denom_x
        y = self.m * x + self.b

        print("x,y", x, y, self.m, self.b)

        # Now determine if that point falls outside the start/end for itself
        if x < self.start[0] and x < self.end[0]:
            print("1")
            return False
        if x > self.start[0] and x > self.end[0]:
            print("2")
            return False
        if y < self.start[1] and y < self.end[1]:
            print("3")
            return False
        if y > self.start[1] and y > self.end[1]:
            print("4")
            return False

        # And the same checks, but for the other line
        if x < line.start[0] and x < line.end[0]:
            print("5")
            return False
        if x > line.start[0] and x > line.end[0]:
            print("6")
            return False
        if y < line.start[1] and y < line.end[1]:
            print("7")
            return False
        if y > line.start[1] and y > line.end[1]:
            print("8")
            return False

        return True