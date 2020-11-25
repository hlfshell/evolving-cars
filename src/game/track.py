import pygame
from .car import Car
from math import radians, floor, tan, sqrt
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
    # distance.
    # To find the point where the line from the car at
    # said angle encounters the wall, we use trig and the
    # size of the image to calculate it. See doc/trig.jpg
    # for the breakdown.
    def distance_to_wall(self, car : Car, angle):
        # The angle is relative to the car's orientation, but we
        # need the angle for our caluclations relative to the
        # origin. Therefore we are going to convert its
        # coordinate frame
        # Why + 90? Because we were -90 on rotation at creation
        # time due to image not facing at 0 degrees
        angle = (angle + car.get_rotation() + 90) % 360

        # Validation / safety - negative angles
        # are just 360 minus that angle. We treat all angles
        # as COUNTERclockwise, with 0 degrees being straight
        # down, 180 up, 90 right, and 270 left. The counter
        # clockwise bit threw me for a loop for awhile.
        if angle < 0:
            angle = 360 - angle
        start = car.get_center()
        start = (int(start[0]), int(start[1]))
        shape = self.get_size()
        shape = (shape[0] - 1, shape[1] - 1)
        pixels = None

        # First, to make life easy, determine if the line is
        # horizontal or vertical to skip the mathematical
        # oddities and checks.
        # Horizontal
        if angle == 90:
            pixels = define_line(start[0], start[1], shape[0], start[1])
        elif angle == 270:
            pixels = define_line(start[0], start[1], 0, start[1])

        # Vertical
        elif angle == 0:
            pixels = define_line(start[0], start[1], start[0], shape[1])
        elif angle == 180:
            pixels = define_line(start[0], start[1], start[0], 0)

        else:
            # Is our angled line going up or down? Left or right? Our math
            # to find our "end point" changes based on this.
            # Again, reference doc/trig.jpg to see where I am pulling
            # the equations from.

            # If the first calculation results in an intersection outside
            # of the image boundaries, then logically we would have
            # intersected the other wall by then - so we'll switch to that
            # calculation.

            # Quadrant 1
            if angle <= 90:
                x = start[0] + floor(tan(radians(angle))*(shape[1]-start[1]))
                y = shape[1]
                if x > shape[0]:
                    x = shape[0]
                    y = start[1] + floor(tan(radians(90-angle))*(shape[0]-start[0]))
            # Quadrant 2
            elif angle > 90 and angle <= 180:
                x = shape[0]
                y = start[1] - floor(tan(radians(angle-90))*(shape[0]-start[0]))
                if y < 0:
                    x = start[0] + floor(tan(radians(180 - angle))*start[1])
                    y = 0
            # Quadrant 3
            elif angle > 180 and angle <= 270:
                x = start[0] - floor(tan(radians(angle - 180))*start[1])
                y = 0
                if x < 0:
                    x = 0
                    y = start[1] - floor(tan(radians(270-angle))*start[0])
            # Quadrant 4
            elif angle > 270:
                x = 0
                y = start[1] + floor(tan(radians(angle - 270))*start[0])
                if y > shape[1]:
                    x = start[0] - floor(tan(radians(360-angle))*(shape[1]-start[1]))
                    y = shape[1]

            end = (int(x), int(y))

            pixels = define_line(start[0], start[1], end[0], end[1])

        for pixel in pixels:
            if tuple(self.surf.get_at(pixel))[-1] != 0:
                end = pixel
                break

        # Calculate the total euclidean distance to the set end
        distance = sqrt( (end[0]-start[0])**2 + (end[1]-start[1])**2 )
        return end, distance