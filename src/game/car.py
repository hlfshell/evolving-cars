import pygame
vector = pygame.math.Vector2
from PIL import Image
import numpy as np
from random import uniform, randint
from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN
from uuid import uuid4 as uuid

from .checkpoint import Checkpoint
from .nn import NN
from .nn import mate as nn_mate

im = Image.open('assets/car_sprite.png')
im = im.resize((28, 14))

CRASH = -50
CHECKPOINT = 150
NO_CHECKPOINTS = -100

class Car(pygame.sprite.Sprite):

    def __init__(
        self,
        position : (int, int),
        rotation : int = 0,
        color : (int, int, int) = None,
        nn = None
        ):
        super().__init__()

        self._id = uuid()

        self._crashed = False

        self._position = position
        self._rotation = rotation
        self._initial_position = position
        self._initial_rotation = rotation

        if color is None:
            color =  list(np.random.choice(range(256), size=3))
        self._color = color
        # replace that car color of "white" with the chosen color
        imagedata = np.array(im)
        red, green, blue = imagedata[:,:,0], imagedata[:,:,1], imagedata[:,:,2]
        mask = (red > 250) & (green > 250) & (blue > 250)
        imagedata[:,:,:3][mask] = [color[0], color[1], color[2]]

        self._image_shape = (imagedata.shape[0:2][1], imagedata.shape[0:2][0])
        self._image_data = imagedata.astype('uint8')

        self.surf = pygame.image.frombuffer(self._image_data, self._image_shape, 'RGBA')
        self.image = self.surf
        self.rect = self.surf.get_rect(center = self._position)
    
        self._velocity = vector(0,0)
        self._acceleration = vector(0,0)

        self._score = 0

        self._checkpoints = {}

        self._distances = {}
        self._distance_endpoints = {}

        if nn is None:
            self._nn = NN()
        else:
            self._nn = nn

    def get_center(self):
        return self._position

    def get_rotation(self):
        return self._rotation

    def get_keyboard_move(self, pressed_keys):
        rotation = 0

        if pressed_keys[K_LEFT]:
            rotation += 1
        elif pressed_keys[K_RIGHT]:
            rotation += -1

        acceleration = 0

        if pressed_keys[K_UP]:
            acceleration = 0.5
        elif pressed_keys[K_DOWN]:
            acceleration = -0.5

        return acceleration, rotation

    def get_nn_move(self):
        orders = self._nn.infer(self._velocity.magnitude(), self._rotation, self._distances)
        orders = orders >= 0.5
        # orders is the NN output with the following outputs
        # 1. acceleration
        # 2. deacceleration
        # 3+4. turn left (soft and hard)
        # 5+6. turn right (soft and hard)
        accelerate = orders[0]
        deaccelerate = orders[1]
        leftSlight = orders[2]
        leftHard = orders[3]
        rightSlight = orders[4]
        rightHard = orders[5]

        acceleration = 0
        if accelerate:
            acceleration += 0.5
        if deaccelerate:
            acceleration += -0.5

        rotation = 0
        if leftSlight:
            rotation += 1
        if leftHard:
            rotation += 4
        if rightSlight:
            rotation -= 1
        if rightHard:
            rotation -= 4

        return acceleration, rotation

    def move(self, acceleration, rotation):
        if self._crashed:
            return
        self._rotation += rotation
    
        if acceleration == 0:
            current_magnitude = self._velocity.magnitude()
            deaccelerate = 0.05
            if current_magnitude - deaccelerate < 0:
                acceleration = -current_magnitude
            else:
                acceleration = -deaccelerate
            
        velocity_magnitude = self._velocity.magnitude() + acceleration
        if velocity_magnitude > 10:
            velocity_magnitude = 10

        rotation = -self._rotation

        self._velocity = vector(velocity_magnitude, 0).rotate(rotation)
        self._position += self._velocity

    def render(self):
        surface = pygame.image.frombuffer(self._image_data, self._image_shape, 'RGBA')
        self.surf = pygame.transform.rotate(surface, self._rotation)
        self.image = self.surf # This is obtuse but it's how mask collisions work
        self.rect = self.surf.get_rect(center = self._position)

    def crash(self, seconds_since_start : int):
        if self._crashed:
            return
        self._score += CRASH + int(seconds_since_start)
        self._crashed = True

    def cross_checkpoint(self, checkpoint : Checkpoint, seconds_since_start : int):
        if checkpoint._id not in self._checkpoints:
            self._score += CHECKPOINT - int(seconds_since_start)
            self._checkpoints[checkpoint._id] = True

    def cross_finish_line(self):
        # We are clearing out the checkpoints, but because we punish
        # cars that don't go anywhere, we need *something* here to mark
        # that checkpoints have been crossed.
        self._checkpoints = {"finish": True}

    def add_end_score(self, seconds_since_start):
        if len(self._checkpoints) == 0:
            self._score += NO_CHECKPOINTS

    def add_distance(self, angle, end_point, distance):
        self._distance_endpoints[angle] = end_point
        self._distances[angle] = distance

    def reset(self):
        self._crashed = False
        self._position = self._initial_position
        self._rotation = self._initial_rotation
        self._velocity = vector(0,0)
        self._acceleration = vector(0,0)
        self._score = 0
        self._checkpoints = {}
        self._distances = {}
        self._distance_endpoints = {}
        self.render() # This reset the rectangle position for collision detection

def mate(a : Car, b : Car, a_parentage : float = 0.50, mutation : float = 0.05):
    # For fun, blend the colors
    # color = [0, 0, 0]
    # for index, channel in enumerate(color):
    #     if uniform(0, 1) < mutation:
    #         color[index] = randint(0, 255)
    #     elif uniform(0, 1) < a_parentage:
    #         color[index] = a._color[index]
    #     else:
    #         color[index] = b._color[index]
    # color = (color[0], color[1], color[2])

    nn = nn_mate(a._nn, b._nn, a_parentage=a_parentage, mutation=mutation)

    return Car(a._initial_position, a._initial_rotation, nn=nn)