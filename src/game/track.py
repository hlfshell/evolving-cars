import pygame
from .car import Car
from math import tanh, radians, floor
from .bresenham import define_line

class Track(pygame.sprite.Sprite):

    def __init__(self, filename : str):
        super().__init__()

        self.surf = pygame.image.load(filename)
        self.rect = self.surf.get_rect()
        self.rect.topleft= [0,0]
        self.mask = pygame.mask.from_surface(self.surf)

    def get_size(self):
        return self.surf.get_size()

    # Given a car and an angle, find the distance from
    # the car's center to the wall at that angle.
    # Much like the checkpoint's collision detection
    # we use Bresenham's Algorithm to iterate over pixels
    # we will find the maximum possible point using the
    # bounds of the track itself, generate the line,
    # and then find the first pixel that contains a
    # non-zero alpha as a collision. From here we can
    # return the resulting point and the calculated
    # distance
    def distance_to_wall(self, car : Car, angle):
        # The angle is relative to the car's orientation, but we
        # need the angle for our caluclations relative to the
        # origin. Therefore we are going to convert its
        # coordinate frame
        angle = angle + car.get_rotation()
        print("ANGLE", angle)

        # Validation / safety - negative angles
        # are just 360 minus that angle. We treat
        # all angles as clockwise, with 0 being straight
        # up, 90 being right, 180 being down, 270 being left
        if angle < 0:
            angle = 360 - angle
        start = car.get_center()
        shape = self.get_size()
        pixels = None

        # First, to make life easy, determine if the line is
        # horizontal or vertical to skip the mathematical
        # oddities and checks.
        # Horizontal
        if angle == 90 or angle == 270:
            print("hori")
            pixels = define_line(start[0], start[1], shape[0], start[1])

        # Vertical
        elif angle == 0 or angle == 180:
            print("vert")
            pixels = define_line(start[0], start[1], start[0], shape[1])

        else: 
            print("other")
            # Is our angled line going up or down? Left or right? Our math
            # to find our "end point" changes based on this.
            
            # Quadrant 1
            if angle < 90:
                y_start = 0
                x_start = shape[0] - 1
            # Quadrant 2
            elif angle > 90 and angle < 180:
                y_start = shape[1] - 1
                x_start = shape[0] - 1
            # Quadrant 3
            elif angle > 180 and angle < 270:
                y_start = shape[1] - 1
                x_start = shape[0] - 1
            # Quadrant 4
            elif angle > 270:
                y_start = 0
                x_start = 0

            # Calculate the first "end point". 
            # First, we assume the angle will hit the top canvas (0) before it will hit the
            # side of the canvas
            # y = mx + b
            # m = slope = tanh(angle)
            # b = y - mx (use the start positions!)
            # Once you have B...
            # Set y = 0, solve for x to find intercept point
            # x = (y - b) / m
            m = tanh(radians(angle))
            b = start[1] - (m * start[0])
            x = floor((y_start - b) / m)

            # If x is not greater than the shape, we have our intercept point.
            if x > 0 and x < shape[0]:
                print("within")
                end = (x, 0)
                
            # Otherwise, we need to solve for x with our x_start
            else:
                print("without")
                end = (x_start, floor((m * x_start) + b))

            print(start, end)

# b = pygame.sprite.Sprite() # create sprite
# b.image = pygame.image.load("ball.png").convert() # load ball image
# b.rect = b.image.get_rect() # use image extent values
# b.rect.topleft = [0, 0] # put the ball in the top left corner
# screen.blit(b.image, b.rect)
